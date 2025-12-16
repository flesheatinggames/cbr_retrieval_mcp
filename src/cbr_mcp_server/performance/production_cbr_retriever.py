"""Production-ready CBR retriever with performance optimizations."""

import logging
import threading
from typing import Any, Callable, Dict, List, Optional

try:
    import chromadb
except ImportError:
    chromadb = None

from cbr_mcp_server.performance.memory_manager import MemoryManager

# Import performance components with lazy fallback
try:
    from cbr_mcp_server.performance.cache_system import ResultCache
    from cbr_mcp_server.performance.data_models import CachePolicy
except ImportError:
    # Fallback for when cache_system module doesn't exist yet
    ResultCache = None
    CachePolicy = None

try:
    from cbr_mcp_server.performance.lazy_loader import LazyLoader
except ImportError:
    # Fallback for when lazy_loader module doesn't exist yet
    LazyLoader = None

logger = logging.getLogger(__name__)


def _default_case_loader(case_id: str) -> Dict[str, Any]:
    """Default no-op case loader when none provided."""
    return {"case_id": case_id, "content": f"Case {case_id}", "category": "default"}


class LazyEmbeddingModel:
    """
    Lazy-loading wrapper for SentenceTransformer embedding model.

    This class defers the actual loading of the SentenceTransformer model
    until the first call to encode(), reducing server startup time by 2-4 seconds.

    Thread-safe implementation ensures the model is loaded only once even under
    concurrent access scenarios. Additionally, the encode() method is protected
    by a lock to prevent tensor shape mismatch errors when multiple threads
    encode queries of different lengths simultaneously.

    Attributes:
        model_name: Name of the sentence-transformers model to load
        trust_remote_code: Whether to trust remote code (required for some models)
        _model: The loaded SentenceTransformer instance (None until first use)
        _load_lock: Threading lock for thread-safe model loading
        _encode_lock: Threading lock for thread-safe encoding operations
    """

    def __init__(
        self,
        model_name: str = "nomic-ai/nomic-embed-text-v1.5",
        trust_remote_code: bool = True,
    ):
        """
        Initialize lazy embedding model wrapper.

        Args:
            model_name: Name of the sentence-transformers model to load
            trust_remote_code: Whether to trust remote code when loading model
        """
        self.model_name = model_name
        self.trust_remote_code = trust_remote_code
        self._model: Optional[Any] = None
        self._load_lock = threading.Lock()
        self._encode_lock = threading.Lock()

    def _load_model(self) -> Any:
        """
        Load the SentenceTransformer model if not already loaded.

        Thread-safe implementation using double-checked locking pattern.

        Returns:
            The loaded SentenceTransformer model

        Raises:
            ImportError: If sentence-transformers is not installed
            RuntimeError: If model loading fails
        """
        # Double-checked locking for thread safety
        if self._model is None:
            with self._load_lock:
                # Check again inside lock to prevent multiple loads
                if self._model is None:
                    try:
                        logger.info(
                            f"Loading embedding model lazily: {self.model_name}"
                        )
                        from sentence_transformers import SentenceTransformer

                        self._model = SentenceTransformer(
                            self.model_name, trust_remote_code=self.trust_remote_code
                        )
                        logger.info(
                            f"Embedding model loaded successfully: {self.model_name}"
                        )
                    except ImportError as e:
                        raise ImportError(
                            "sentence-transformers not installed. "
                            "Install with: pip install sentence-transformers"
                        ) from e
                    except Exception as e:
                        raise RuntimeError(
                            f"Failed to load embedding model '{self.model_name}': {str(e)}"
                        ) from e

        return self._model

    def encode(self, sentences, **kwargs):
        """
        Encode sentences to embeddings, loading model on first call.

        This method provides the same interface as SentenceTransformer.encode()
        but defers model loading until first use.

        Thread-safety: The encode operation is protected by a lock to prevent
        tensor shape mismatch errors when multiple threads encode queries of
        different lengths simultaneously. The SentenceTransformer.encode()
        method is not thread-safe due to internal batching that can cause
        "The size of tensor a (X) must match the size of tensor b (Y)"
        errors under concurrent access.

        Args:
            sentences: Text or list of texts to encode
            **kwargs: Additional arguments passed to SentenceTransformer.encode()

        Returns:
            Encoded embeddings as numpy array or list
        """
        model = self._load_model()
        # Lock encoding to prevent concurrent tensor shape mismatches
        with self._encode_lock:
            return model.encode(sentences, **kwargs)

    @property
    def is_loaded(self) -> bool:
        """
        Check if the embedding model has been loaded.

        Returns:
            True if model is loaded, False otherwise
        """
        return self._model is not None


class ProductionCBRRetriever:
    """
    Production-ready CBR retriever integrating performance optimizations.

    This class wraps core CBR retrieval functionality with:
    - MemoryManager for memory tracking during queries
    - ResultCache for query result caching
    - LazyLoader for on-demand embedding loading

    Attributes:
        memory_manager: MemoryManager instance for tracking memory usage
        result_cache: ResultCache instance for caching query results
        lazy_loader: LazyLoader instance for lazy embedding loading (if enabled)
        config: Configuration dictionary
    """

    def __init__(
        self,
        db_path: str,
        embedding_model: Optional[Any] = None,
        case_loader: Optional[Callable[[str], Dict[str, Any]]] = None,
        enable_lazy_loading: bool = False,
        config: Optional[Dict[str, Any]] = None,
        max_retries: int = 0,
    ):
        """
        Initialize ProductionCBRRetriever with performance components.

        Args:
            db_path: Path to ChromaDB database
            embedding_model: Optional embedding model for query encoding
            case_loader: Optional function for loading cases on-demand
            enable_lazy_loading: Whether to enable lazy loading of embeddings
            config: Optional configuration dictionary with performance settings
            max_retries: Maximum number of retry attempts for failed queries

        Raises:
            ValueError: If configuration is invalid
        """
        self.db_path = db_path
        self.embedding_model = embedding_model
        self.case_loader = case_loader
        self.enable_lazy_loading = enable_lazy_loading
        self.config = config or {}
        self.max_retries = max_retries

        # Validate configuration
        self._validate_config()

        # Extract configuration settings
        cache_config = self.config.get("cache", {})
        memory_config = self.config.get("memory", {})
        lazy_loading_config = self.config.get("lazy_loading", {})
        cache_warming_config = self.config.get("cache_warming", {})
        index_warming_config = self.config.get("index_warming", {})

        # Initialize MemoryManager with configuration
        max_memory_mb = memory_config.get("max_memory_mb", 512)
        warning_threshold = memory_config.get("warning_threshold", 0.8)
        self.memory_manager = MemoryManager(
            max_memory_mb=max_memory_mb,
            pressure_threshold=warning_threshold,
        )

        # Initialize ResultCache with configuration if available
        if ResultCache is not None and CachePolicy is not None:
            max_cache_size = cache_config.get("max_size", 1000)
            ttl_seconds = cache_config.get("ttl_seconds", 3600)
            cache_policy = CachePolicy(
                max_size=max_cache_size,
                default_ttl=ttl_seconds,
                eviction_policy="LRU",
            )
            self.result_cache = ResultCache(policy=cache_policy)
        else:
            # Fallback: simple dict-based cache
            self.result_cache = _SimpleCacheFallback()

        # Initialize LazyLoader if available
        # If no case_loader provided, create a default no-op loader
        if LazyLoader is not None:
            effective_case_loader = case_loader or _default_case_loader
            # LazyLoader only accepts case_loader and config parameters
            from cbr_mcp_server.performance.data_models import LazyLoadingConfig

            # Build LazyLoadingConfig from config dict
            lazy_config = LazyLoadingConfig(
                lazy_load_enabled=lazy_loading_config.get("enabled", True),
                preload_hot_cases=lazy_loading_config.get("preload_hot_cases", True),
                hot_case_count=lazy_loading_config.get("hot_case_count", 50),
                background_loading_enabled=lazy_loading_config.get(
                    "background_loading_enabled", True
                ),
                access_window_hours=lazy_loading_config.get("access_window_hours", 24),
                min_access_frequency=lazy_loading_config.get(
                    "min_access_frequency", 0.5
                ),
                preload_batch_size=lazy_loading_config.get("batch_size", 20),
                max_concurrent_loads=lazy_loading_config.get("max_concurrent_loads", 5),
                max_cache_size=lazy_loading_config.get("max_cache_size", 200),
            )
            self.lazy_loader = LazyLoader(
                case_loader=effective_case_loader, config=lazy_config
            )
        elif case_loader is not None:
            # Fallback: simple loader without batching
            self.lazy_loader = _SimpleLazyLoaderFallback(case_loader)
        else:
            # No LazyLoader module and no case_loader - create minimal fallback
            self.lazy_loader = _SimpleLazyLoaderFallback(_default_case_loader)

        # Initialize ChromaDB client only (Phase 1: Incremental Initialization)
        # Collection creation is deferred to first query (Phase 2) to reduce startup time
        if chromadb is not None:
            try:
                self.client = chromadb.PersistentClient(path=self.db_path)
                logger.info("ChromaDB persistent client initialized (Phase 1: startup)")
            except Exception as e:
                logger.error(f"Failed to initialize ChromaDB client: {str(e)}")
                self.client = None
        else:
            logger.warning("ChromaDB module not available")
            self.client = None

        # Collection is NOT created during __init__ - deferred to first query
        self.collection = None
        self._collection_lock = (
            threading.Lock()
        )  # For thread-safe collection initialization
        self._collection_initialized = False

        # Perform cache warming if configured
        if cache_warming_config.get("enabled", False):
            self._warm_cache(cache_warming_config.get("queries", []))

        # Perform index warming if configured (background, non-blocking)
        if index_warming_config.get("enabled", False):
            categories = index_warming_config.get("categories")
            warmup_query_count = index_warming_config.get("warmup_query_count", 3)
            self._warm_index(
                categories=categories, warmup_query_count=warmup_query_count
            )

    def _validate_config(self) -> None:
        """
        Validate configuration settings.

        Raises:
            ValueError: If configuration contains invalid values
        """
        if "cache" in self.config:
            cache_config = self.config["cache"]
            max_size = cache_config.get("max_size")
            if max_size is not None and max_size < 0:
                raise ValueError(
                    "Invalid cache configuration: max_size must be non-negative"
                )

        if "memory" in self.config:
            memory_config = self.config["memory"]
            max_memory_mb = memory_config.get("max_memory_mb")
            if max_memory_mb is not None and max_memory_mb < 0:
                raise ValueError(
                    "Invalid memory configuration: max_memory_mb must be non-negative"
                )
            warning_threshold = memory_config.get("warning_threshold")
            if warning_threshold is not None and (
                warning_threshold < 0 or warning_threshold > 1
            ):
                raise ValueError(
                    "Invalid memory configuration: warning_threshold must be between 0 and 1"
                )

        if "lazy_loading" in self.config:
            lazy_config = self.config["lazy_loading"]
            batch_size = lazy_config.get("batch_size")
            if batch_size is not None and batch_size < 1:
                raise ValueError(
                    "Invalid lazy_loading configuration: batch_size must be positive"
                )
            hot_case_count = lazy_config.get("hot_case_count")
            if hot_case_count is not None and hot_case_count < 1:
                raise ValueError(
                    "Invalid lazy_loading configuration: hot_case_count must be positive"
                )
            max_cache_size = lazy_config.get("max_cache_size")
            if max_cache_size is not None and max_cache_size < 1:
                raise ValueError(
                    "Invalid lazy_loading configuration: max_cache_size must be positive"
                )

        if "index_warming" in self.config:
            index_warming_config = self.config["index_warming"]
            warmup_query_count = index_warming_config.get("warmup_query_count")
            if warmup_query_count is not None and warmup_query_count < 0:
                raise ValueError(
                    "Invalid index_warming configuration: warmup_query_count must be non-negative"
                )

    def _ensure_collection_initialized(self) -> None:
        """
        Ensure ChromaDB collection is initialized (Phase 2: on-demand initialization).

        This method implements the second phase of incremental initialization:
        - Phase 1 (startup): Client created in __init__
        - Phase 2 (first query): Collection created here

        Thread-safe implementation using double-checked locking to ensure
        collection is initialized exactly once even under concurrent access.

        Raises:
            RuntimeError: If collection initialization fails
        """
        # Fast path: collection already initialized
        if self._collection_initialized:
            return

        # Double-checked locking for thread safety
        with self._collection_lock:
            # Check again inside lock to prevent multiple initializations
            if self._collection_initialized:
                return

            # Validate client is available
            if self.client is None:
                raise RuntimeError(
                    "ChromaDB client not available. Cannot initialize collection."
                )

            try:
                logger.info("Initializing ChromaDB collection (Phase 2: on-demand)")
                self.collection = self.client.get_or_create_collection(
                    name="code_solutions_case_base"
                )
                self._collection_initialized = True
                logger.info("ChromaDB collection initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize ChromaDB collection: {str(e)}")
                raise RuntimeError(
                    f"Failed to initialize ChromaDB collection: {str(e)}"
                ) from e

    def _warm_cache(self, queries: List[str]) -> None:
        """
        Warm cache with frequently accessed queries.

        Args:
            queries: List of queries to pre-load into cache
        """
        for query in queries:
            try:
                # Execute query to populate cache
                self.retrieve(query, max_results=5)
            except Exception:
                # Continue warming even if individual queries fail
                pass

    def _warm_index(
        self, categories: Optional[List[str]] = None, warmup_query_count: int = 3
    ) -> None:
        """
        Warm ChromaDB HNSW index by executing sample queries.

        This method pre-warms the ChromaDB HNSW index structures by executing
        sample queries across different categories. Index warming reduces first
        query latency by populating internal index caches.

        Runs in background (non-blocking) to avoid impacting startup time.

        Args:
            categories: List of categories to sample queries from (default: common categories)
            warmup_query_count: Number of warming queries to execute per category
        """
        import threading

        def _execute_warming():
            """Execute index warming in background thread."""
            try:
                # Ensure collection is initialized before warming
                self._ensure_collection_initialized()

                # Default categories if none provided
                default_categories = ["code", "orchestration", "best-practice"]
                categories_to_warm = categories or default_categories

                logger.info(
                    f"Starting index warming with {len(categories_to_warm)} categories, "
                    f"{warmup_query_count} queries per category"
                )

                warming_queries = []
                for category in categories_to_warm:
                    # Generate sample queries for each category
                    for i in range(warmup_query_count):
                        warming_queries.append(f"{category} example {i}")

                # Execute warming queries to populate HNSW index cache
                warmed_count = 0
                for query in warming_queries:
                    try:
                        # Execute lightweight query (small result set)
                        if (
                            self.embedding_model is not None
                            and self.collection is not None
                        ):
                            query_embedding = self.embedding_model.encode(query)

                            # Handle both list and numpy array embeddings
                            if hasattr(query_embedding, "tolist"):
                                embedding_list = query_embedding.tolist()
                            elif isinstance(query_embedding, list):
                                embedding_list = (
                                    query_embedding[0]
                                    if query_embedding
                                    and isinstance(query_embedding[0], list)
                                    else query_embedding
                                )
                            else:
                                embedding_list = list(query_embedding)

                            # Execute small query to warm index
                            self.collection.query(
                                query_embeddings=[embedding_list],
                                n_results=2,  # Small result set for warming
                            )
                            warmed_count += 1
                    except Exception as e:
                        # Log but continue warming even if individual queries fail
                        logger.debug(
                            f"Index warming query failed (continuing): {str(e)}"
                        )
                        continue

                logger.info(
                    f"Index warming completed: {warmed_count}/{len(warming_queries)} queries executed"
                )

            except Exception as e:
                # Index warming failure should not break functionality
                logger.warning(f"Index warming failed (non-critical): {str(e)}")

        # Execute warming in background thread (non-blocking)
        warming_thread = threading.Thread(target=_execute_warming, daemon=True)
        warming_thread.start()
        logger.debug("Index warming started in background")

    def retrieve(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant cases for a query with memory tracking and caching.

        Args:
            query: Query string to search for
            max_results: Maximum number of results to return

        Returns:
            List of matching cases with metadata

        Raises:
            RuntimeError: If memory tracking fails or query execution fails
        """
        # Track memory before query
        try:
            memory_before = self.memory_manager.check_memory_usage()
        except Exception as e:
            raise RuntimeError(f"Memory tracking system failure: {str(e)}")

        # Check cache for existing results
        try:
            cached_result = self.result_cache.get(query)
            if cached_result is not None:
                # Cache hit - return cached results
                return cached_result
        except Exception:
            # Cache error - continue with query execution
            pass

        # Cache miss - execute query
        results = self._execute_query(query, max_results)

        # Store results in cache
        try:
            self.result_cache.set(query, results)
        except Exception:
            # Cache storage error - continue anyway
            pass

        # Track memory after query
        try:
            memory_after = self.memory_manager.check_memory_usage()
        except Exception as e:
            raise RuntimeError(f"Memory tracking system failure: {str(e)}")

        return results

    def _execute_query(
        self, query: str, max_results: int, retry_count: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Execute query against ChromaDB with retry logic.

        Args:
            query: Query string to search for
            max_results: Maximum number of results to return
            retry_count: Current retry attempt number

        Returns:
            List of matching cases

        Raises:
            RuntimeError: If query fails after all retries
        """
        try:
            # Ensure collection is initialized (Phase 2: on-demand)
            self._ensure_collection_initialized()

            # Encode query using embedding model
            if self.embedding_model is None:
                raise RuntimeError("Embedding model not available")

            query_embedding = self.embedding_model.encode(query)

            # Query ChromaDB collection
            if self.collection is None:
                raise RuntimeError("ChromaDB collection not available")

            # Handle both list and numpy array embeddings
            if hasattr(query_embedding, "tolist"):
                embedding_list = query_embedding.tolist()
            elif isinstance(query_embedding, list):
                # Already a list - handle nested list structure [[...]]
                embedding_list = (
                    query_embedding[0]
                    if query_embedding and isinstance(query_embedding[0], list)
                    else query_embedding
                )
            else:
                embedding_list = list(query_embedding)

            raw_results = self.collection.query(
                query_embeddings=[embedding_list], n_results=max_results
            )

            # Format results
            return self._format_results(raw_results)

        except Exception as e:
            # Retry logic if configured
            if retry_count < self.max_retries:
                return self._execute_query(query, max_results, retry_count + 1)
            else:
                # Re-raise with context about embedding/model failure
                if "model" in str(e).lower() or "embedding" in str(e).lower():
                    raise
                else:
                    raise RuntimeError(f"Model inference failed: {str(e)}")

    def _format_results(self, raw_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format ChromaDB query results into standard format.

        Args:
            raw_results: Raw results from ChromaDB query

        Returns:
            Formatted list of result dictionaries
        """
        formatted = []

        ids = raw_results.get("ids", [[]])[0]
        documents = raw_results.get("documents", [[]])[0]
        metadatas = raw_results.get("metadatas", [[]])[0]
        distances = raw_results.get("distances", [[]])[0]

        for i, case_id in enumerate(ids):
            formatted.append(
                {
                    "id": case_id,
                    "content": documents[i] if i < len(documents) else "",
                    "metadata": metadatas[i] if i < len(metadatas) else {},
                    "distance": distances[i] if i < len(distances) else 1.0,
                }
            )

        return formatted

    def close(self) -> None:
        """
        Close ChromaDB connections and clean up resources.

        This method should be called explicitly when done using the retriever
        to ensure proper cleanup of file descriptors and database connections.
        """
        try:
            # Clear collection reference
            if self.collection is not None:
                self.collection = None
                self._collection_initialized = False
                logger.debug("Collection reference cleared")

            # Close ChromaDB client
            if self.client is not None:
                # ChromaDB PersistentClient doesn't have explicit close method
                # but clearing the reference helps with garbage collection
                self.client = None
                logger.debug("ChromaDB client reference cleared")

            # Clear caches to free memory
            if hasattr(self.result_cache, '_cache'):
                self.result_cache._cache.clear()
                logger.debug("Result cache cleared")

            # Clear lazy loader cache if it exists
            if hasattr(self.lazy_loader, '_loaded'):
                self.lazy_loader._loaded.clear()
                logger.debug("Lazy loader cache cleared")

            logger.info("ProductionCBRRetriever closed successfully")

        except Exception as e:
            logger.error(f"Error during ProductionCBRRetriever cleanup: {str(e)}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup."""
        self.close()
        return False  # Don't suppress exceptions

    def __del__(self):
        """Destructor - ensures cleanup on garbage collection."""
        try:
            self.close()
        except Exception:
            # Silently ignore errors in destructor
            pass


class _SimpleCacheFallback:
    """Simple fallback cache when ResultCache is not available."""

    def __init__(self):
        self._cache: Dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        self._cache[key] = value


class _SimpleLazyLoaderFallback:
    """Simple fallback lazy loader when LazyLoader is not available."""

    def __init__(self, case_loader: Callable[[str], Dict[str, Any]]):
        self.case_loader = case_loader
        self._loaded: Dict[str, Dict[str, Any]] = {}

    def load_on_demand(self, case_id: str) -> Dict[str, Any]:
        """Load case on demand."""
        if case_id not in self._loaded:
            self._loaded[case_id] = self.case_loader(case_id)
        return self._loaded[case_id]

    def is_loaded(self, case_id: str) -> bool:
        """Check if case is loaded."""
        return case_id in self._loaded
