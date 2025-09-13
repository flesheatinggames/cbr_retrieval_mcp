# CBR MCP Server - Performance Tuning Guide

> Last Updated: 2025-09-09
> Version: 1.0.0

## Overview

This comprehensive performance tuning guide provides detailed strategies, configuration optimizations, and benchmarking techniques to maximize the performance of the CBR MCP Server. It covers system resource optimization, database tuning, caching strategies, query optimization, and workload-specific configurations for different deployment scenarios.

## Performance Architecture Overview

### Performance Components

The CBR MCP Server performance is influenced by several key components:

1. **System Resources**: CPU, memory, disk I/O, and network
2. **Database Layer**: ChromaDB configuration and indexing
3. **Embedding Processing**: Model loading and inference optimization
4. **Caching Layer**: Multi-level caching strategies
5. **Request Processing**: Async operations and connection handling
6. **Network Layer**: Transport optimization and compression

### Performance Bottleneck Identification

Common performance bottlenecks and their indicators:

- **CPU Bottlenecks**: High CPU usage, query queuing, slow embedding generation
- **Memory Bottlenecks**: Memory pressure, swap usage, frequent garbage collection
- **Disk I/O Bottlenecks**: High disk wait times, slow database queries
- **Network Bottlenecks**: High latency, connection timeouts, bandwidth saturation
- **Cache Inefficiency**: Low hit rates, frequent cache misses

## System Resource Optimization

### CPU Optimization

#### CPU Affinity and Process Priority

```bash
#!/bin/bash
# cpu_optimization.sh - CPU optimization script

# Set CPU affinity for CBR server (use specific cores)
PID=$(pgrep -f "cbr-mcp-server")
if [ -n "$PID" ]; then
    # Bind to cores 2-7 (leaving 0-1 for system processes)
    taskset -cp 2-7 "$PID"
    echo "CPU affinity set for CBR server (PID: $PID)"
fi

# Set high priority for CBR server
renice -10 "$PID"
echo "Process priority increased"

# Optimize CPU governor for performance
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Disable CPU idle states for lowest latency (optional, increases power usage)
# sudo cpupower idle-set -D 0
```

#### Multi-threading Configuration

```yaml
# cpu-optimized.yaml - CPU optimization configuration
production:
  # Enable concurrent request processing
  max_concurrent_requests: 50
  thread_pool_size: 16        # 2x CPU cores typically optimal
  
  # Async processing optimization
  async_timeout: 30.0
  max_queue_size: 500
  
  # CPU-intensive operations
  embedding_batch_size: 32    # Batch embedding generation
  parallel_similarity_search: true
  
monitoring:
  # Reduce monitoring overhead on CPU
  interval: 60.0              # Less frequent monitoring
  cpu_affinity: [0, 1]       # Dedicate specific cores for monitoring
```

#### Environment Variables for CPU Optimization

```bash
# CPU optimization environment variables
export OMP_NUM_THREADS=8           # OpenMP threads for numerical libraries
export MKL_NUM_THREADS=8           # Intel MKL threads
export OPENBLAS_NUM_THREADS=8      # OpenBLAS threads
export NUMEXPR_NUM_THREADS=8       # NumExpr threads

# Python optimization
export PYTHONOPTIMIZE=1            # Enable Python optimizations
export PYTHONDONTWRITEBYTECODE=1   # Skip .pyc file generation

# Torch/embedding optimization
export TORCH_NUM_THREADS=8
export TOKENIZERS_PARALLELISM=false  # Disable tokenizer parallelism to avoid conflicts
```

### Memory Optimization

#### Memory Configuration

```yaml
# memory-optimized.yaml - Memory optimization configuration
query:
  max_results_default: 10           # Limit result set size
  similarity_threshold_default: 0.8 # Higher threshold = fewer results

production:
  # Cache configuration
  cache_enabled: true
  cache_ttl: 7200                   # 2 hours
  cache_max_size: 10000            # Limit cache entries
  cache_cleanup_interval: 3600      # Regular cleanup
  
  # Memory limits
  max_query_length: 5000           # Limit query size
  max_embedding_cache: 50000       # Embedding cache size
  
  # Garbage collection optimization
  gc_threshold_0: 1000             # Frequent small GC
  gc_threshold_1: 15               # Less frequent medium GC
  gc_threshold_2: 10               # Rare large GC

logging:
  # Reduce logging memory usage
  max_file_size: 20971520          # 20MB log files
  backup_count: 5                  # Fewer backup files
  buffer_size: 8192                # Smaller log buffers

monitoring:
  # Optimize monitoring memory usage
  retention_hours: 72              # 3 days instead of 7
  metrics_buffer_size: 1000        # Smaller metrics buffer
  alert_history_size: 500          # Limit alert history
```

#### Python Memory Optimization Script

```python
#!/usr/bin/env python3
# memory_optimizer.py - Runtime memory optimization

import gc
import os
import psutil
import logging
from typing import Optional
import resource

class MemoryOptimizer:
    def __init__(self):
        self.process = psutil.Process()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def set_memory_limits(self, max_memory_gb: float = 8.0):
        """Set memory limits for the process."""
        max_memory_bytes = int(max_memory_gb * 1024**3)
        
        # Set soft memory limit
        resource.setrlimit(resource.RLIMIT_AS, (max_memory_bytes, max_memory_bytes))
        
        self.logger.info(f"Memory limit set to {max_memory_gb}GB")
    
    def optimize_garbage_collection(self):
        """Optimize Python garbage collection settings."""
        # Set GC thresholds for better memory management
        gc.set_threshold(1000, 15, 10)
        
        # Force full garbage collection
        collected = gc.collect()
        
        self.logger.info(f"Garbage collection optimized, collected {collected} objects")
    
    def monitor_memory_usage(self) -> dict:
        """Monitor current memory usage."""
        memory_info = self.process.memory_info()
        memory_percent = self.process.memory_percent()
        
        return {
            'rss': memory_info.rss,
            'vms': memory_info.vms,
            'percent': memory_percent,
            'available': psutil.virtual_memory().available
        }
    
    def optimize_for_low_memory(self):
        """Apply optimizations for low-memory environments."""
        # Disable Python's memory allocator debug mode
        os.environ['PYTHONMALLOC'] = 'default'
        
        # Set smaller Python hash randomization seed
        os.environ['PYTHONHASHSEED'] = '0'
        
        # Force immediate memory cleanup
        gc.collect()
        
        # Optimize memory allocator
        try:
            import pymalloc
            pymalloc.set_memory_limit(4 * 1024**3)  # 4GB limit
        except ImportError:
            pass
        
        self.logger.info("Low-memory optimizations applied")
    
    def emergency_memory_cleanup(self):
        """Emergency memory cleanup procedure."""
        self.logger.warning("Performing emergency memory cleanup")
        
        # Force multiple GC cycles
        for _ in range(3):
            gc.collect()
        
        # Clear Python caches
        import sys
        if hasattr(sys, '_clear_type_cache'):
            sys._clear_type_cache()
        
        # Try to trim memory (Linux only)
        if hasattr(os, 'MADV_DONTNEED'):
            try:
                import mmap
                # This is a simplified example - actual implementation would be more complex
                self.logger.info("Memory trimming attempted")
            except:
                pass
        
        memory_usage = self.monitor_memory_usage()
        self.logger.info(f"Post-cleanup memory usage: {memory_usage['percent']:.1f}%")

def apply_memory_optimizations():
    """Apply system-wide memory optimizations."""
    optimizer = MemoryOptimizer()
    
    # Set memory limits
    optimizer.set_memory_limits(max_memory_gb=8.0)
    
    # Optimize GC
    optimizer.optimize_garbage_collection()
    
    # Check if we're in a low-memory environment
    total_memory_gb = psutil.virtual_memory().total / 1024**3
    if total_memory_gb < 8.0:
        optimizer.optimize_for_low_memory()
    
    return optimizer

if __name__ == "__main__":
    optimizer = apply_memory_optimizations()
    
    # Monitor memory periodically
    import time
    while True:
        usage = optimizer.monitor_memory_usage()
        print(f"Memory usage: {usage['percent']:.1f}%")
        
        # Emergency cleanup if memory usage is too high
        if usage['percent'] > 90:
            optimizer.emergency_memory_cleanup()
        
        time.sleep(60)
```

### Disk I/O Optimization

#### SSD Configuration

```bash
#!/bin/bash
# disk_optimization.sh - Disk I/O optimization

# SSD optimization
DISK_DEVICE="/dev/nvme0n1"  # Adjust for your SSD

# Enable SSD-specific optimizations
echo mq-deadline | sudo tee /sys/block/$(basename $DISK_DEVICE)/queue/scheduler
echo 0 | sudo tee /sys/block/$(basename $DISK_DEVICE)/queue/rotational
echo 1 | sudo tee /sys/block/$(basename $DISK_DEVICE)/queue/discard_max_bytes

# Optimize filesystem mount options
sudo mount -o remount,noatime,nodiratime /opt/cbr/data

# Set optimal readahead
sudo blockdev --setra 256 $DISK_DEVICE
```

#### Database Storage Optimization

```yaml
# disk-optimized.yaml - Disk I/O optimization configuration
database:
  # Use high-performance path for database
  path: "/opt/cbr/data/db"          # Ensure this is on SSD
  
  # ChromaDB optimization settings
  chroma_settings:
    persist_directory: "/opt/cbr/data/db"
    max_batch_size: 100
    
    # SQLite optimization (ChromaDB uses SQLite internally)
    sqlite_cache_size: 20000        # 20MB cache
    sqlite_temp_store: "memory"     # Keep temp data in memory
    sqlite_journal_mode: "WAL"      # Write-Ahead Logging for better performance
    sqlite_synchronous: "NORMAL"    # Balance safety and performance

logging:
  # Optimize log file I/O
  output_file: "/opt/cbr/logs/server.log"  # Separate disk if possible
  buffer_size: 65536                       # 64KB buffer
  flush_interval: 5.0                      # Batch writes

monitoring:
  # Optimize monitoring database
  db_path: "/opt/cbr/data/monitoring.db"
  write_batch_size: 100
  flush_interval: 30
```

#### I/O Monitoring Script

```python
#!/usr/bin/env python3
# io_monitor.py - I/O performance monitoring

import psutil
import time
import logging

class IOMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.last_io_stats = None
        
    def get_io_stats(self):
        """Get current I/O statistics."""
        # System-wide I/O stats
        disk_io = psutil.disk_io_counters()
        
        # Process-specific I/O (if available)
        try:
            process = None
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if 'cbr-mcp-server' in ' '.join(proc.info['cmdline'] or []):
                    process = proc
                    break
            
            if process:
                process_io = process.io_counters()
            else:
                process_io = None
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            process_io = None
        
        return {
            'system': {
                'read_bytes': disk_io.read_bytes if disk_io else 0,
                'write_bytes': disk_io.write_bytes if disk_io else 0,
                'read_count': disk_io.read_count if disk_io else 0,
                'write_count': disk_io.write_count if disk_io else 0,
                'read_time': disk_io.read_time if disk_io else 0,
                'write_time': disk_io.write_time if disk_io else 0
            },
            'process': {
                'read_bytes': process_io.read_bytes if process_io else 0,
                'write_bytes': process_io.write_bytes if process_io else 0,
                'read_count': process_io.read_count if process_io else 0,
                'write_count': process_io.write_count if process_io else 0
            } if process_io else None
        }
    
    def calculate_io_rates(self, current_stats, interval):
        """Calculate I/O rates between measurements."""
        if not self.last_io_stats:
            return None
            
        rates = {}
        
        # System I/O rates
        system_current = current_stats['system']
        system_last = self.last_io_stats['system']
        
        rates['system'] = {
            'read_bps': (system_current['read_bytes'] - system_last['read_bytes']) / interval,
            'write_bps': (system_current['write_bytes'] - system_last['write_bytes']) / interval,
            'read_iops': (system_current['read_count'] - system_last['read_count']) / interval,
            'write_iops': (system_current['write_count'] - system_last['write_count']) / interval
        }
        
        # Process I/O rates (if available)
        if current_stats['process'] and self.last_io_stats['process']:
            proc_current = current_stats['process']
            proc_last = self.last_io_stats['process']
            
            rates['process'] = {
                'read_bps': (proc_current['read_bytes'] - proc_last['read_bytes']) / interval,
                'write_bps': (proc_current['write_bytes'] - proc_last['write_bytes']) / interval,
                'read_iops': (proc_current['read_count'] - proc_last['read_count']) / interval,
                'write_iops': (proc_current['write_count'] - proc_last['write_count']) / interval
            }
        
        return rates
    
    def monitor_io_performance(self, interval=60):
        """Monitor I/O performance continuously."""
        while True:
            current_stats = self.get_io_stats()
            rates = self.calculate_io_rates(current_stats, interval)
            
            if rates:
                system_read_mbps = rates['system']['read_bps'] / 1024**2
                system_write_mbps = rates['system']['write_bps'] / 1024**2
                
                self.logger.info(f"I/O Rates - Read: {system_read_mbps:.2f} MB/s, "
                               f"Write: {system_write_mbps:.2f} MB/s")
                
                if rates.get('process'):
                    proc_read_mbps = rates['process']['read_bps'] / 1024**2
                    proc_write_mbps = rates['process']['write_bps'] / 1024**2
                    
                    self.logger.info(f"CBR Process I/O - Read: {proc_read_mbps:.2f} MB/s, "
                                   f"Write: {proc_write_mbps:.2f} MB/s")
                
                # Alert on high I/O
                if system_read_mbps > 500 or system_write_mbps > 500:
                    self.logger.warning("High I/O detected - potential bottleneck")
            
            self.last_io_stats = current_stats
            time.sleep(interval)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    monitor = IOMonitor()
    monitor.monitor_io_performance()
```

## ChromaDB Performance Tuning

### Database Configuration

```python
# chroma_optimization.py - ChromaDB performance optimization

import chromadb
from chromadb.config import Settings

def create_optimized_chroma_client(db_path="/opt/cbr/data/db"):
    """Create ChromaDB client with performance optimizations."""
    
    settings = Settings(
        # Core performance settings
        chroma_db_impl="duckdb+parquet",          # Use DuckDB for better performance
        persist_directory=db_path,
        
        # Memory settings
        chroma_memory_limit_mb=4096,              # 4GB memory limit
        
        # Query optimization
        chroma_collection_cache_size=1000,        # Cache collections
        chroma_segment_cache_size=100,            # Cache segments
        
        # Batch processing
        chroma_batch_size=1000,                   # Larger batches
        chroma_max_batch_size=10000,              # Max batch size
        
        # Threading
        chroma_num_threads=8,                     # Parallel processing
        
        # Storage optimization
        chroma_segment_max_size=10000000,         # 10M items per segment
        chroma_compaction_interval_seconds=3600,  # Hourly compaction
        
        # Advanced settings
        chroma_sqlite_cache_size=20000,           # 20MB SQLite cache
        chroma_sqlite_journal_mode="WAL",         # Write-ahead logging
        chroma_sqlite_synchronous="NORMAL"        # Balance safety/performance
    )
    
    return chromadb.PersistentClient(
        path=db_path,
        settings=settings
    )

def optimize_collection_indices(collection):
    """Optimize collection indices for better search performance."""
    
    # Configure HNSW parameters for optimal performance
    hnsw_params = {
        "space": "cosine",              # or "l2" depending on your embedding model
        "M": 32,                        # Number of connections (16-64 typical range)
        "ef_construction": 200,         # Higher = better quality, slower build
        "max_elements": 100000,         # Expected max elements
        "ef": 100,                      # Higher = better recall, slower search
        "seed": 42                      # Reproducible results
    }
    
    # Apply HNSW optimization (ChromaDB-specific method)
    try:
        collection.modify(metadata={"hnsw:space": hnsw_params["space"],
                                   "hnsw:M": hnsw_params["M"],
                                   "hnsw:ef_construction": hnsw_params["ef_construction"],
                                   "hnsw:ef": hnsw_params["ef"]})
    except:
        # Fallback if direct HNSW configuration is not available
        pass
    
    return collection

def run_database_maintenance(client):
    """Run maintenance operations for optimal performance."""
    
    # Get all collections
    collections = client.list_collections()
    
    for collection_info in collections:
        collection = client.get_collection(collection_info.name)
        
        # Optimize indices
        optimize_collection_indices(collection)
        
        # Compact collection (if supported)
        try:
            collection.compact()
        except:
            pass
    
    print(f"Maintenance completed for {len(collections)} collections")

class ChromaPerformanceAnalyzer:
    def __init__(self, client):
        self.client = client
        
    def analyze_query_performance(self, collection_name, test_queries, n_results=10):
        """Analyze query performance for optimization."""
        import time
        
        collection = self.client.get_collection(collection_name)
        results = []
        
        for query in test_queries:
            start_time = time.time()
            
            # Perform query
            search_results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            end_time = time.time()
            
            results.append({
                'query': query,
                'latency': end_time - start_time,
                'results_count': len(search_results['documents'][0]),
                'distances': search_results['distances'][0] if search_results['distances'] else []
            })
        
        # Analyze results
        avg_latency = sum(r['latency'] for r in results) / len(results)
        max_latency = max(r['latency'] for r in results)
        min_latency = min(r['latency'] for r in results)
        
        print(f"Query Performance Analysis:")
        print(f"Average latency: {avg_latency:.3f}s")
        print(f"Min latency: {min_latency:.3f}s")
        print(f"Max latency: {max_latency:.3f}s")
        
        # Identify slow queries
        slow_queries = [r for r in results if r['latency'] > avg_latency * 2]
        if slow_queries:
            print(f"Slow queries detected: {len(slow_queries)}")
            for sq in slow_queries:
                print(f"  - '{sq['query'][:50]}...': {sq['latency']:.3f}s")
        
        return results

if __name__ == "__main__":
    # Example usage
    client = create_optimized_chroma_client()
    run_database_maintenance(client)
    
    # Performance analysis
    analyzer = ChromaPerformanceAnalyzer(client)
    test_queries = [
        "authentication code example",
        "database connection",
        "error handling pattern",
        "logging configuration",
        "performance optimization"
    ]
    analyzer.analyze_query_performance("code_solutions_case_base", test_queries)
```

### Database Index Optimization

```python
#!/usr/bin/env python3
# index_optimizer.py - Database index optimization

import chromadb
import numpy as np
import time
from typing import List, Dict, Any

class IndexOptimizer:
    def __init__(self, client, collection_name):
        self.client = client
        self.collection_name = collection_name
        self.collection = client.get_collection(collection_name)
        
    def analyze_data_distribution(self) -> Dict[str, Any]:
        """Analyze the distribution of data for optimization."""
        
        # Get collection statistics
        count = self.collection.count()
        
        # Sample embeddings to analyze distribution
        if count > 1000:
            sample_size = min(1000, count // 10)
            sample_data = self.collection.get(limit=sample_size, include=['embeddings'])
            embeddings = np.array(sample_data['embeddings'])
            
            # Calculate statistics
            mean_norm = np.mean(np.linalg.norm(embeddings, axis=1))
            std_norm = np.std(np.linalg.norm(embeddings, axis=1))
            dimensionality = embeddings.shape[1]
            
            # Calculate pairwise distances (sample)
            if len(embeddings) > 100:
                sample_embeddings = embeddings[:100]
                distances = []
                for i in range(len(sample_embeddings)):
                    for j in range(i+1, len(sample_embeddings)):
                        dist = np.linalg.norm(sample_embeddings[i] - sample_embeddings[j])
                        distances.append(dist)
                
                avg_distance = np.mean(distances)
                std_distance = np.std(distances)
            else:
                avg_distance = None
                std_distance = None
            
            return {
                'total_vectors': count,
                'dimensionality': dimensionality,
                'mean_norm': mean_norm,
                'std_norm': std_norm,
                'avg_pairwise_distance': avg_distance,
                'std_pairwise_distance': std_distance
            }
        else:
            return {'total_vectors': count}
    
    def recommend_hnsw_parameters(self, data_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend optimal HNSW parameters based on data characteristics."""
        
        total_vectors = data_stats['total_vectors']
        
        # Base recommendations
        recommendations = {
            'M': 16,                    # Default connections
            'ef_construction': 200,     # Construction parameter
            'ef': 50,                   # Search parameter
            'max_elements': total_vectors * 2  # Allow for growth
        }
        
        # Adjust based on collection size
        if total_vectors < 10000:
            # Small collection - optimize for accuracy
            recommendations['M'] = 32
            recommendations['ef_construction'] = 400
            recommendations['ef'] = 100
        elif total_vectors < 100000:
            # Medium collection - balanced
            recommendations['M'] = 24
            recommendations['ef_construction'] = 300
            recommendations['ef'] = 75
        else:
            # Large collection - optimize for speed
            recommendations['M'] = 16
            recommendations['ef_construction'] = 200
            recommendations['ef'] = 50
        
        # Adjust based on dimensionality if available
        if 'dimensionality' in data_stats:
            dim = data_stats['dimensionality']
            if dim > 768:  # High dimensional data
                recommendations['M'] = max(12, recommendations['M'] - 4)
                recommendations['ef_construction'] = max(150, recommendations['ef_construction'] - 50)
        
        return recommendations
    
    def benchmark_search_performance(self, test_queries: List[str], 
                                   n_results: int = 10, 
                                   iterations: int = 5) -> Dict[str, float]:
        """Benchmark search performance with current settings."""
        
        from sentence_transformers import SentenceTransformer
        
        # Load embedding model (same as CBR server)
        model = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', trust_remote_code=True)
        
        latencies = []
        
        for iteration in range(iterations):
            for query in test_queries:
                start_time = time.time()
                
                # Generate embedding
                query_embedding = model.encode([query])
                
                # Perform search
                results = self.collection.query(
                    query_embeddings=query_embedding.tolist(),
                    n_results=n_results
                )
                
                end_time = time.time()
                latencies.append(end_time - start_time)
        
        return {
            'avg_latency': np.mean(latencies),
            'min_latency': np.min(latencies),
            'max_latency': np.max(latencies),
            'p95_latency': np.percentile(latencies, 95),
            'p99_latency': np.percentile(latencies, 99),
            'std_latency': np.std(latencies)
        }
    
    def optimize_collection(self):
        """Run complete collection optimization."""
        
        print(f"Optimizing collection: {self.collection_name}")
        
        # Analyze data
        print("Analyzing data distribution...")
        data_stats = self.analyze_data_distribution()
        print(f"Collection stats: {data_stats}")
        
        # Get recommendations
        hnsw_params = self.recommend_hnsw_parameters(data_stats)
        print(f"Recommended HNSW parameters: {hnsw_params}")
        
        # Benchmark current performance
        test_queries = [
            "authentication implementation",
            "database connection pool",
            "error handling middleware",
            "logging configuration",
            "caching strategy"
        ]
        
        print("Benchmarking current performance...")
        current_perf = self.benchmark_search_performance(test_queries)
        print(f"Current performance: {current_perf}")
        
        return {
            'data_stats': data_stats,
            'recommended_params': hnsw_params,
            'current_performance': current_perf
        }

if __name__ == "__main__":
    # Example usage
    client = chromadb.PersistentClient(path="./db")
    optimizer = IndexOptimizer(client, "code_solutions_case_base")
    results = optimizer.optimize_collection()
    
    print("\nOptimization Results:")
    print("===================")
    for key, value in results.items():
        print(f"{key}: {value}")
```

## Embedding Model Optimization

### Model Loading Optimization

```python
#!/usr/bin/env python3
# embedding_optimizer.py - Embedding model optimization

import torch
import os
import time
import psutil
from sentence_transformers import SentenceTransformer
from typing import List, Optional
import threading
import queue

class OptimizedEmbeddingModel:
    def __init__(self, model_name: str = 'nomic-ai/nomic-embed-text-v1.5',
                 device: Optional[str] = None,
                 cache_dir: Optional[str] = None):
        
        self.model_name = model_name
        self.cache_dir = cache_dir or os.path.expanduser('~/.cache/sentence_transformers')
        
        # Auto-detect optimal device
        if device is None:
            if torch.cuda.is_available():
                self.device = 'cuda'
                print(f"Using CUDA device: {torch.cuda.get_device_name()}")
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                self.device = 'mps'  # Apple Silicon
                print("Using Apple MPS device")
            else:
                self.device = 'cpu'
                print("Using CPU device")
        else:
            self.device = device
        
        # Optimization settings
        self.batch_size = self._determine_optimal_batch_size()
        self.max_seq_length = 512  # Model-specific
        
        # Model loading with optimizations
        self.model = self._load_optimized_model()
        
        # Embedding cache
        self.embedding_cache = {}
        self.cache_lock = threading.Lock()
        
        # Batch processing queue
        self.batch_queue = queue.Queue()
        self.batch_processor = None
        
    def _determine_optimal_batch_size(self) -> int:
        """Determine optimal batch size based on available memory."""
        
        if self.device == 'cuda':
            # GPU memory-based calculation
            gpu_memory = torch.cuda.get_device_properties(0).total_memory
            # Rough estimate: 1GB supports batch size of 32 for typical models
            optimal_batch = max(1, min(64, gpu_memory // (1024**3) * 32))
            return optimal_batch
        elif self.device == 'mps':
            # Apple Silicon - conservative batch size
            return 16
        else:
            # CPU - based on system memory
            system_memory_gb = psutil.virtual_memory().total // (1024**3)
            return max(1, min(32, system_memory_gb * 4))
    
    def _load_optimized_model(self) -> SentenceTransformer:
        """Load model with performance optimizations."""
        
        print(f"Loading model {self.model_name} on {self.device}...")
        start_time = time.time()
        
        # Model loading optimizations
        torch.set_num_threads(min(8, os.cpu_count()))
        
        if self.device == 'cuda':
            # CUDA optimizations
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.deterministic = False
        
        # Load model
        model = SentenceTransformer(
            self.model_name,
            device=self.device,
            cache_folder=self.cache_dir
        )
        
        # Model optimizations
        model.eval()  # Set to evaluation mode
        
        if self.device == 'cuda':
            # Half precision for inference (if supported)
            try:
                model.half()
                print("Using half precision (FP16)")
            except:
                print("Half precision not supported, using FP32")
        
        # Compile model for PyTorch 2.0+ (if available)
        try:
            if hasattr(torch, 'compile'):
                model = torch.compile(model, mode='reduce-overhead')
                print("Model compiled with PyTorch 2.0")
        except:
            pass
        
        load_time = time.time() - start_time
        print(f"Model loaded in {load_time:.2f} seconds")
        
        return model
    
    def encode_single(self, text: str, use_cache: bool = True) -> List[float]:
        """Encode single text with caching."""
        
        if use_cache:
            with self.cache_lock:
                if text in self.embedding_cache:
                    return self.embedding_cache[text]
        
        # Generate embedding
        embedding = self.model.encode([text], batch_size=1)[0]
        
        if use_cache:
            with self.cache_lock:
                # Limit cache size
                if len(self.embedding_cache) > 10000:
                    # Remove oldest entries (simple FIFO)
                    items_to_remove = list(self.embedding_cache.keys())[:1000]
                    for key in items_to_remove:
                        del self.embedding_cache[key]
                
                self.embedding_cache[text] = embedding.tolist()
        
        return embedding.tolist()
    
    def encode_batch(self, texts: List[str], use_cache: bool = True) -> List[List[float]]:
        """Encode batch of texts efficiently."""
        
        if not texts:
            return []
        
        results = [None] * len(texts)
        texts_to_encode = []
        indices_to_encode = []
        
        # Check cache first
        if use_cache:
            with self.cache_lock:
                for i, text in enumerate(texts):
                    if text in self.embedding_cache:
                        results[i] = self.embedding_cache[text]
                    else:
                        texts_to_encode.append(text)
                        indices_to_encode.append(i)
        else:
            texts_to_encode = texts
            indices_to_encode = list(range(len(texts)))
        
        # Encode remaining texts in batches
        if texts_to_encode:
            for batch_start in range(0, len(texts_to_encode), self.batch_size):
                batch_end = min(batch_start + self.batch_size, len(texts_to_encode))
                batch_texts = texts_to_encode[batch_start:batch_end]
                batch_indices = indices_to_encode[batch_start:batch_end]
                
                # Generate embeddings
                batch_embeddings = self.model.encode(
                    batch_texts,
                    batch_size=len(batch_texts),
                    show_progress_bar=False
                )
                
                # Store results
                for i, embedding in enumerate(batch_embeddings):
                    result_idx = batch_indices[i]
                    embedding_list = embedding.tolist()
                    results[result_idx] = embedding_list
                    
                    # Update cache
                    if use_cache:
                        with self.cache_lock:
                            self.embedding_cache[batch_texts[i]] = embedding_list
        
        return results
    
    def warm_up_model(self, sample_texts: Optional[List[str]] = None):
        """Warm up the model with sample inputs."""
        
        if sample_texts is None:
            sample_texts = [
                "Sample authentication code for user login",
                "Database connection pooling implementation",
                "Error handling middleware for REST API",
                "Logging configuration with structured output",
                "Caching layer implementation with Redis"
            ]
        
        print("Warming up embedding model...")
        start_time = time.time()
        
        # Warm up with batch processing
        self.encode_batch(sample_texts, use_cache=False)
        
        warmup_time = time.time() - start_time
        print(f"Model warm-up completed in {warmup_time:.2f} seconds")
        
        # Test performance
        test_start = time.time()
        self.encode_single(sample_texts[0])
        single_time = time.time() - test_start
        
        batch_start = time.time()
        self.encode_batch(sample_texts[:3])
        batch_time = time.time() - batch_start
        
        print(f"Single encoding: {single_time:.3f}s")
        print(f"Batch encoding (3 items): {batch_time:.3f}s")
        print(f"Batch efficiency: {(single_time * 3) / batch_time:.2f}x faster")
    
    def get_memory_usage(self) -> dict:
        """Get current memory usage statistics."""
        
        if self.device == 'cuda':
            gpu_allocated = torch.cuda.memory_allocated() / 1024**2  # MB
            gpu_cached = torch.cuda.memory_reserved() / 1024**2      # MB
            return {
                'gpu_allocated_mb': gpu_allocated,
                'gpu_cached_mb': gpu_cached,
                'cache_size': len(self.embedding_cache)
            }
        else:
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                'rss_mb': memory_info.rss / 1024**2,
                'vms_mb': memory_info.vms / 1024**2,
                'cache_size': len(self.embedding_cache)
            }
    
    def clear_cache(self):
        """Clear embedding cache to free memory."""
        with self.cache_lock:
            cache_size = len(self.embedding_cache)
            self.embedding_cache.clear()
            print(f"Cleared {cache_size} cached embeddings")

def benchmark_embedding_performance():
    """Benchmark embedding model performance."""
    
    # Test data
    test_texts = [
        "Authentication implementation with JWT tokens",
        "Database connection pooling with SQLAlchemy",
        "REST API error handling middleware",
        "Structured logging with JSON output format",
        "Redis caching layer implementation",
        "User session management system",
        "File upload handling with validation",
        "Background task processing with Celery",
        "Real-time notifications with WebSockets",
        "API rate limiting implementation"
    ]
    
    # Initialize optimized model
    model = OptimizedEmbeddingModel()
    model.warm_up_model()
    
    # Benchmark single encoding
    single_times = []
    for text in test_texts:
        start_time = time.time()
        model.encode_single(text)
        single_times.append(time.time() - start_time)
    
    # Benchmark batch encoding
    batch_start = time.time()
    model.encode_batch(test_texts)
    batch_time = time.time() - batch_start
    
    # Results
    avg_single_time = sum(single_times) / len(single_times)
    total_single_time = sum(single_times)
    
    print("\nPerformance Benchmark Results:")
    print("==============================")
    print(f"Average single encoding: {avg_single_time:.3f}s")
    print(f"Total single encoding time: {total_single_time:.3f}s")
    print(f"Batch encoding time: {batch_time:.3f}s")
    print(f"Batch speedup: {total_single_time / batch_time:.2f}x")
    print(f"Throughput: {len(test_texts) / batch_time:.1f} texts/second")
    
    # Memory usage
    memory_usage = model.get_memory_usage()
    print(f"\nMemory Usage:")
    for key, value in memory_usage.items():
        print(f"{key}: {value:.2f}")

if __name__ == "__main__":
    benchmark_embedding_performance()
```

### GPU Optimization

```bash
#!/bin/bash
# gpu_optimization.sh - GPU optimization for embedding model

# NVIDIA GPU optimizations
if command -v nvidia-smi &> /dev/null; then
    echo "Optimizing NVIDIA GPU settings..."
    
    # Set GPU to performance mode
    sudo nvidia-smi -pm 1
    
    # Set maximum GPU clocks
    sudo nvidia-smi -ac memory_clock,graphics_clock
    
    # Enable persistence mode
    sudo nvidia-smi -i 0 -pm 1
    
    # Set power limit to maximum
    sudo nvidia-smi -i 0 -pl $(nvidia-smi --query-gpu=power.max_limit --format=csv,noheader,nounits | head -1)
    
    echo "NVIDIA GPU optimizations applied"
fi

# Environment variables for GPU optimization
export CUDA_CACHE_DISABLE=0
export CUDA_CACHE_MAXSIZE=2147483648    # 2GB cache
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# PyTorch optimizations
export TORCH_CUDNN_V8_API_ENABLED=1
export TORCH_SHOW_CPP_STACKTRACES=1

echo "GPU optimization environment variables set"
```

## Caching Strategies

### Multi-Level Caching Implementation

```python
#!/usr/bin/env python3
# advanced_caching.py - Advanced caching strategies

import time
import hashlib
import json
import threading
from typing import Any, Optional, Dict, List, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
import pickle
import redis
import diskcache

@dataclass
class CacheEntry:
    value: Any
    timestamp: float
    ttl: float
    access_count: int = 0
    last_access: float = 0
    size: int = 0

class CacheBackend(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: float = 3600) -> bool:
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        pass
    
    @abstractmethod
    def size(self) -> int:
        pass

class MemoryCache(CacheBackend):
    def __init__(self, max_size: int = 10000, max_memory_mb: int = 500):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.current_memory = 0
        self.lock = threading.RLock()
        
    def _get_entry_size(self, value: Any) -> int:
        """Estimate memory size of cached value."""
        try:
            return len(pickle.dumps(value))
        except:
            return len(str(value).encode('utf-8'))
    
    def _evict_lru(self):
        """Evict least recently used entries."""
        if not self.cache:
            return
        
        # Sort by last access time
        sorted_entries = sorted(
            self.cache.items(),
            key=lambda x: x[1].last_access
        )
        
        # Remove oldest entries until we're under limits
        entries_to_remove = []
        for key, entry in sorted_entries:
            if (len(self.cache) <= self.max_size * 0.8 and 
                self.current_memory <= self.max_memory_bytes * 0.8):
                break
            entries_to_remove.append(key)
        
        for key in entries_to_remove[:len(sorted_entries) // 4]:  # Remove 25%
            entry = self.cache.pop(key, None)
            if entry:
                self.current_memory -= entry.size
    
    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            entry = self.cache.get(key)
            if entry is None:
                return None
            
            current_time = time.time()
            
            # Check expiration
            if current_time - entry.timestamp > entry.ttl:
                self.delete(key)
                return None
            
            # Update access stats
            entry.access_count += 1
            entry.last_access = current_time
            
            return entry.value
    
    def set(self, key: str, value: Any, ttl: float = 3600) -> bool:
        with self.lock:
            current_time = time.time()
            entry_size = self._get_entry_size(value)
            
            # Check if adding this entry would exceed memory limit
            if entry_size > self.max_memory_bytes:
                return False
            
            # Remove old entry if exists
            if key in self.cache:
                old_entry = self.cache[key]
                self.current_memory -= old_entry.size
            
            # Evict if necessary
            if (len(self.cache) >= self.max_size or 
                self.current_memory + entry_size > self.max_memory_bytes):
                self._evict_lru()
            
            # Add new entry
            entry = CacheEntry(
                value=value,
                timestamp=current_time,
                ttl=ttl,
                last_access=current_time,
                size=entry_size
            )
            
            self.cache[key] = entry
            self.current_memory += entry_size
            
            return True
    
    def delete(self, key: str) -> bool:
        with self.lock:
            entry = self.cache.pop(key, None)
            if entry:
                self.current_memory -= entry.size
                return True
            return False
    
    def clear(self) -> bool:
        with self.lock:
            self.cache.clear()
            self.current_memory = 0
            return True
    
    def size(self) -> int:
        return len(self.cache)
    
    def get_stats(self) -> Dict[str, Any]:
        with self.lock:
            total_access_count = sum(entry.access_count for entry in self.cache.values())
            return {
                'entries': len(self.cache),
                'memory_mb': self.current_memory / 1024 / 1024,
                'memory_usage_percent': (self.current_memory / self.max_memory_bytes) * 100,
                'total_accesses': total_access_count,
                'avg_accesses_per_entry': total_access_count / len(self.cache) if self.cache else 0
            }

class RedisCache(CacheBackend):
    def __init__(self, host='localhost', port=6379, db=0, prefix='cbr:'):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=False)
        self.prefix = prefix
        
    def _make_key(self, key: str) -> str:
        return f"{self.prefix}{key}"
    
    def get(self, key: str) -> Optional[Any]:
        try:
            data = self.client.get(self._make_key(key))
            if data:
                return pickle.loads(data)
            return None
        except:
            return None
    
    def set(self, key: str, value: Any, ttl: float = 3600) -> bool:
        try:
            serialized = pickle.dumps(value)
            return self.client.setex(self._make_key(key), int(ttl), serialized)
        except:
            return False
    
    def delete(self, key: str) -> bool:
        try:
            return bool(self.client.delete(self._make_key(key)))
        except:
            return False
    
    def clear(self) -> bool:
        try:
            keys = self.client.keys(f"{self.prefix}*")
            if keys:
                return bool(self.client.delete(*keys))
            return True
        except:
            return False
    
    def size(self) -> int:
        try:
            return len(self.client.keys(f"{self.prefix}*"))
        except:
            return 0

class DiskCache(CacheBackend):
    def __init__(self, cache_dir: str = "/tmp/cbr_cache", max_size_gb: float = 1.0):
        self.cache = diskcache.Cache(cache_dir, size_limit=int(max_size_gb * 1024**3))
    
    def get(self, key: str) -> Optional[Any]:
        return self.cache.get(key)
    
    def set(self, key: str, value: Any, ttl: float = 3600) -> bool:
        try:
            self.cache.set(key, value, expire=ttl)
            return True
        except:
            return False
    
    def delete(self, key: str) -> bool:
        return self.cache.delete(key)
    
    def clear(self) -> bool:
        self.cache.clear()
        return True
    
    def size(self) -> int:
        return len(self.cache)

class MultiLevelCache:
    def __init__(self, 
                 l1_cache: Optional[CacheBackend] = None,
                 l2_cache: Optional[CacheBackend] = None,
                 l3_cache: Optional[CacheBackend] = None):
        
        # Default cache hierarchy
        self.l1_cache = l1_cache or MemoryCache(max_size=1000, max_memory_mb=100)  # Fast, small
        self.l2_cache = l2_cache or MemoryCache(max_size=10000, max_memory_mb=500)  # Medium
        self.l3_cache = l3_cache  # Optional disk/Redis cache
        
        self.hit_stats = {
            'l1_hits': 0,
            'l2_hits': 0,
            'l3_hits': 0,
            'misses': 0
        }
        self.stats_lock = threading.Lock()
    
    def _make_cache_key(self, key: str, operation: str = "query") -> str:
        """Create standardized cache key."""
        if isinstance(key, str):
            key_hash = hashlib.md5(key.encode('utf-8')).hexdigest()
        else:
            key_hash = hashlib.md5(str(key).encode('utf-8')).hexdigest()
        
        return f"{operation}:{key_hash}"
    
    def get(self, key: str, operation: str = "query") -> Optional[Any]:
        """Get value from cache hierarchy."""
        cache_key = self._make_cache_key(key, operation)
        
        # Try L1 cache first (fastest)
        value = self.l1_cache.get(cache_key)
        if value is not None:
            with self.stats_lock:
                self.hit_stats['l1_hits'] += 1
            return value
        
        # Try L2 cache
        value = self.l2_cache.get(cache_key)
        if value is not None:
            with self.stats_lock:
                self.hit_stats['l2_hits'] += 1
            # Promote to L1
            self.l1_cache.set(cache_key, value, ttl=1800)  # 30 min in L1
            return value
        
        # Try L3 cache if available
        if self.l3_cache:
            value = self.l3_cache.get(cache_key)
            if value is not None:
                with self.stats_lock:
                    self.hit_stats['l3_hits'] += 1
                # Promote to upper levels
                self.l2_cache.set(cache_key, value, ttl=3600)   # 1 hour in L2
                self.l1_cache.set(cache_key, value, ttl=1800)   # 30 min in L1
                return value
        
        # Cache miss
        with self.stats_lock:
            self.hit_stats['misses'] += 1
        return None
    
    def set(self, key: str, value: Any, operation: str = "query", ttl: float = 3600) -> bool:
        """Set value in cache hierarchy."""
        cache_key = self._make_cache_key(key, operation)
        
        # Set in all cache levels
        success = True
        
        # L1 cache (shorter TTL)
        success &= self.l1_cache.set(cache_key, value, ttl=min(ttl, 1800))
        
        # L2 cache
        success &= self.l2_cache.set(cache_key, value, ttl=ttl)
        
        # L3 cache (longer TTL)
        if self.l3_cache:
            success &= self.l3_cache.set(cache_key, value, ttl=ttl * 2)
        
        return success
    
    def delete(self, key: str, operation: str = "query") -> bool:
        """Delete from all cache levels."""
        cache_key = self._make_cache_key(key, operation)
        
        success = True
        success &= self.l1_cache.delete(cache_key)
        success &= self.l2_cache.delete(cache_key)
        if self.l3_cache:
            success &= self.l3_cache.delete(cache_key)
        
        return success
    
    def clear(self) -> bool:
        """Clear all cache levels."""
        success = True
        success &= self.l1_cache.clear()
        success &= self.l2_cache.clear()
        if self.l3_cache:
            success &= self.l3_cache.clear()
        
        # Reset stats
        with self.stats_lock:
            self.hit_stats = {key: 0 for key in self.hit_stats}
        
        return success
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        with self.stats_lock:
            total_requests = sum(self.hit_stats.values())
            
            stats = {
                'hit_stats': self.hit_stats.copy(),
                'total_requests': total_requests,
                'hit_rate': 0.0,
                'l1_hit_rate': 0.0,
                'l2_hit_rate': 0.0,
                'l3_hit_rate': 0.0
            }
            
            if total_requests > 0:
                total_hits = total_requests - self.hit_stats['misses']
                stats['hit_rate'] = total_hits / total_requests
                stats['l1_hit_rate'] = self.hit_stats['l1_hits'] / total_requests
                stats['l2_hit_rate'] = self.hit_stats['l2_hits'] / total_requests
                stats['l3_hit_rate'] = self.hit_stats['l3_hits'] / total_requests
            
            # Add cache-specific stats
            if hasattr(self.l1_cache, 'get_stats'):
                stats['l1_cache'] = self.l1_cache.get_stats()
            
            if hasattr(self.l2_cache, 'get_stats'):
                stats['l2_cache'] = self.l2_cache.get_stats()
            
            stats['cache_sizes'] = {
                'l1_size': self.l1_cache.size(),
                'l2_size': self.l2_cache.size(),
                'l3_size': self.l3_cache.size() if self.l3_cache else 0
            }
        
        return stats

class CBRCacheManager:
    """CBR-specific cache manager with query result caching."""
    
    def __init__(self, config: dict = None):
        config = config or {}
        
        # Initialize cache hierarchy
        l1_cache = MemoryCache(
            max_size=config.get('l1_max_size', 1000),
            max_memory_mb=config.get('l1_memory_mb', 100)
        )
        
        l2_cache = MemoryCache(
            max_size=config.get('l2_max_size', 10000),
            max_memory_mb=config.get('l2_memory_mb', 500)
        )
        
        l3_cache = None
        if config.get('use_redis'):
            try:
                l3_cache = RedisCache(
                    host=config.get('redis_host', 'localhost'),
                    port=config.get('redis_port', 6379),
                    db=config.get('redis_db', 0)
                )
            except:
                print("Redis not available, using disk cache")
                l3_cache = DiskCache(
                    cache_dir=config.get('disk_cache_dir', '/tmp/cbr_cache'),
                    max_size_gb=config.get('disk_cache_gb', 1.0)
                )
        elif config.get('use_disk_cache'):
            l3_cache = DiskCache(
                cache_dir=config.get('disk_cache_dir', '/tmp/cbr_cache'),
                max_size_gb=config.get('disk_cache_gb', 1.0)
            )
        
        self.cache = MultiLevelCache(l1_cache, l2_cache, l3_cache)
    
    def cache_query_result(self, query: str, results: List[dict], 
                          similarity_threshold: float = 0.7,
                          max_results: int = 10) -> bool:
        """Cache CBR query results."""
        
        # Create cache key from query parameters
        cache_key = f"{query}:threshold={similarity_threshold}:max={max_results}"
        
        # Cache with appropriate TTL based on result quality
        if results and len(results) > 0:
            avg_similarity = sum(r.get('similarity', 0) for r in results) / len(results)
            # Higher similarity results cached longer
            ttl = 1800 + (avg_similarity * 1800)  # 30min to 1hour
        else:
            ttl = 900  # 15 minutes for empty results
        
        return self.cache.set(cache_key, results, operation="query", ttl=ttl)
    
    def get_cached_query_result(self, query: str, 
                               similarity_threshold: float = 0.7,
                               max_results: int = 10) -> Optional[List[dict]]:
        """Get cached CBR query results."""
        
        cache_key = f"{query}:threshold={similarity_threshold}:max={max_results}"
        return self.cache.get(cache_key, operation="query")
    
    def cache_embeddings(self, text: str, embedding: List[float]) -> bool:
        """Cache text embeddings."""
        return self.cache.set(text, embedding, operation="embedding", ttl=7200)  # 2 hours
    
    def get_cached_embedding(self, text: str) -> Optional[List[float]]:
        """Get cached text embedding."""
        return self.cache.get(text, operation="embedding")
    
    def get_performance_report(self) -> str:
        """Generate performance report."""
        stats = self.cache.get_stats()
        
        report = f"""
CBR Cache Performance Report
============================

Hit Statistics:
  Total Requests: {stats['total_requests']}
  Overall Hit Rate: {stats['hit_rate']:.2%}
  L1 Hit Rate: {stats['l1_hit_rate']:.2%}
  L2 Hit Rate: {stats['l2_hit_rate']:.2%}
  L3 Hit Rate: {stats['l3_hit_rate']:.2%}
  Miss Rate: {(stats['hit_stats']['misses'] / stats['total_requests']):.2%}

Cache Sizes:
  L1 Cache: {stats['cache_sizes']['l1_size']} entries
  L2 Cache: {stats['cache_sizes']['l2_size']} entries
  L3 Cache: {stats['cache_sizes']['l3_size']} entries

Memory Usage:
"""
        
        if 'l1_cache' in stats:
            l1_stats = stats['l1_cache']
            report += f"  L1 Memory: {l1_stats['memory_mb']:.1f}MB ({l1_stats['memory_usage_percent']:.1f}%)\n"
        
        if 'l2_cache' in stats:
            l2_stats = stats['l2_cache']
            report += f"  L2 Memory: {l2_stats['memory_mb']:.1f}MB ({l2_stats['memory_usage_percent']:.1f}%)\n"
        
        return report

if __name__ == "__main__":
    # Example usage and benchmarking
    cache_config = {
        'l1_max_size': 1000,
        'l1_memory_mb': 100,
        'l2_max_size': 10000,
        'l2_memory_mb': 500,
        'use_disk_cache': True,
        'disk_cache_dir': '/tmp/cbr_cache_test',
        'disk_cache_gb': 0.5
    }
    
    cache_manager = CBRCacheManager(cache_config)
    
    # Simulate some queries
    test_queries = [
        ("authentication code", [{"id": 1, "similarity": 0.9}]),
        ("database connection", [{"id": 2, "similarity": 0.8}]),
        ("error handling", [{"id": 3, "similarity": 0.85}]),
    ]
    
    # Cache some results
    for query, results in test_queries:
        cache_manager.cache_query_result(query, results)
    
    # Test cache hits
    for query, _ in test_queries:
        cached_result = cache_manager.get_cached_query_result(query)
        print(f"Cache hit for '{query}': {cached_result is not None}")
    
    # Performance report
    print(cache_manager.get_performance_report())
```

## Workload-Specific Optimizations

### High-Throughput Configuration

```yaml
# high-throughput.yaml - Configuration for high request volume
production:
  # Connection handling
  max_concurrent_requests: 200
  request_timeout: 30.0
  keep_alive_timeout: 75.0
  
  # Threading
  thread_pool_size: 32
  max_queue_size: 2000
  worker_connections: 1000
  
  # Caching (aggressive)
  cache_enabled: true
  cache_ttl: 7200           # 2 hours
  cache_max_size: 50000     # Large cache
  cache_cleanup_interval: 1800  # 30 minutes
  
  # Performance optimizations
  async_timeout: 60.0
  batch_size: 64
  prefetch_embeddings: true
  
query:
  # Optimize for speed over precision
  max_results_default: 5
  similarity_threshold_default: 0.8
  enable_result_streaming: true

monitoring:
  # Reduce monitoring overhead
  interval: 120.0           # 2 minutes
  performance_monitoring: false  # Disable detailed perf tracking
  
logging:
  # Minimal logging
  level: "WARNING"
  performance_logging: false
  request_correlation: false
```

### Low-Latency Configuration

```yaml
# low-latency.yaml - Configuration for minimal response time
production:
  # Optimize for speed
  max_concurrent_requests: 50  # Lower to reduce contention
  request_timeout: 10.0        # Fail fast
  
  # Pre-warming
  preload_embeddings: true
  warm_up_on_start: true
  
  # Caching (immediate access)
  cache_enabled: true
  cache_ttl: 1800             # 30 minutes
  cache_prefetch: true
  
  # Resource dedication
  cpu_affinity: [2, 3, 4, 5]  # Dedicated cores
  memory_pool_size: 2048      # Pre-allocated memory pool
  
query:
  # Optimize for fast results
  max_results_default: 3      # Fewer results
  similarity_threshold_default: 0.85  # Higher threshold
  early_stopping: true        # Stop when good results found
  
database:
  # Database optimization
  connection_pool_size: 20
  query_cache_size: 10000
  
monitoring:
  # Minimal monitoring overhead
  interval: 300.0             # 5 minutes
  lightweight_mode: true
```

### Memory-Constrained Configuration

```yaml
# memory-constrained.yaml - Configuration for low-memory environments
production:
  # Conservative memory usage
  max_concurrent_requests: 10
  thread_pool_size: 4
  
  # Minimal caching
  cache_enabled: true
  cache_ttl: 900              # 15 minutes
  cache_max_size: 1000        # Small cache
  cache_cleanup_interval: 300 # Frequent cleanup
  
  # Resource limits
  max_query_length: 2000      # Smaller queries
  max_embedding_cache: 5000   # Small embedding cache
  
query:
  # Reduce result set sizes
  max_results_default: 3
  similarity_threshold_default: 0.9  # Very selective
  
logging:
  # Minimal logging
  level: "ERROR"
  buffer_size: 1024           # Small buffers
  max_file_size: 5242880      # 5MB max
  backup_count: 2
  
monitoring:
  # Reduced monitoring
  interval: 300.0             # 5 minutes
  retention_hours: 24         # 1 day only
  metrics_buffer_size: 100
```

## Benchmarking and Measurement

### Performance Benchmarking Suite

```python
#!/usr/bin/env python3
# benchmark_suite.py - Comprehensive performance benchmarking

import asyncio
import aiohttp
import time
import statistics
import json
import concurrent.futures
from typing import List, Dict, Any
import requests
from dataclasses import dataclass
import numpy as np

@dataclass
class BenchmarkResult:
    name: str
    avg_latency: float
    min_latency: float
    max_latency: float
    p95_latency: float
    p99_latency: float
    throughput: float
    success_rate: float
    errors: List[str]
    total_requests: int
    duration: float

class CBRBenchmarkSuite:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.test_queries = [
            "user authentication implementation",
            "database connection pooling",
            "REST API error handling",
            "logging configuration setup",
            "caching layer implementation",
            "file upload validation",
            "session management system",
            "background task processing",
            "real-time notifications",
            "API rate limiting"
        ]
    
    def _make_cbr_request(self, query: str, max_results: int = 10, 
                         similarity_threshold: float = 0.7) -> Dict[str, Any]:
        """Make a CBR retrieve request."""
        payload = {
            "method": "tools/call",
            "params": {
                "name": "cbr_retrieve",
                "arguments": {
                    "query": query,
                    "max_results": max_results,
                    "similarity_threshold": similarity_threshold
                }
            }
        }
        
        response = requests.post(
            f"{self.base_url}/mcp",
            json=payload,
            timeout=30
        )
        
        return {
            "status_code": response.status_code,
            "response_time": response.elapsed.total_seconds(),
            "success": response.status_code == 200,
            "response": response.json() if response.status_code == 200 else None
        }
    
    def benchmark_single_queries(self, iterations: int = 100) -> BenchmarkResult:
        """Benchmark single query performance."""
        
        print(f"Running single query benchmark ({iterations} iterations)...")
        
        latencies = []
        errors = []
        successful_requests = 0
        start_time = time.time()
        
        for i in range(iterations):
            query = self.test_queries[i % len(self.test_queries)]
            
            try:
                result = self._make_cbr_request(query)
                latencies.append(result["response_time"])
                
                if result["success"]:
                    successful_requests += 1
                else:
                    errors.append(f"HTTP {result['status_code']}")
                    
            except Exception as e:
                errors.append(str(e))
        
        end_time = time.time()
        duration = end_time - start_time
        
        return BenchmarkResult(
            name="Single Queries",
            avg_latency=statistics.mean(latencies) if latencies else 0,
            min_latency=min(latencies) if latencies else 0,
            max_latency=max(latencies) if latencies else 0,
            p95_latency=np.percentile(latencies, 95) if latencies else 0,
            p99_latency=np.percentile(latencies, 99) if latencies else 0,
            throughput=iterations / duration,
            success_rate=successful_requests / iterations,
            errors=list(set(errors)),
            total_requests=iterations,
            duration=duration
        )
    
    def benchmark_concurrent_queries(self, concurrent_users: int = 10, 
                                   queries_per_user: int = 10) -> BenchmarkResult:
        """Benchmark concurrent query performance."""
        
        print(f"Running concurrent benchmark ({concurrent_users} users, {queries_per_user} queries each)...")
        
        def user_queries(user_id: int) -> List[Dict[str, Any]]:
            results = []
            for i in range(queries_per_user):
                query = self.test_queries[(user_id + i) % len(self.test_queries)]
                try:
                    result = self._make_cbr_request(query)
                    results.append(result)
                except Exception as e:
                    results.append({
                        "success": False,
                        "response_time": 0,
                        "error": str(e)
                    })
            return results
        
        start_time = time.time()
        
        # Run concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(user_queries, user_id) for user_id in range(concurrent_users)]
            all_results = []
            
            for future in concurrent.futures.as_completed(futures):
                all_results.extend(future.result())
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Analyze results
        latencies = [r["response_time"] for r in all_results if r.get("response_time", 0) > 0]
        successful_requests = sum(1 for r in all_results if r.get("success", False))
        errors = [r.get("error", "Unknown error") for r in all_results if not r.get("success", True)]
        
        total_requests = concurrent_users * queries_per_user
        
        return BenchmarkResult(
            name="Concurrent Queries",
            avg_latency=statistics.mean(latencies) if latencies else 0,
            min_latency=min(latencies) if latencies else 0,
            max_latency=max(latencies) if latencies else 0,
            p95_latency=np.percentile(latencies, 95) if latencies else 0,
            p99_latency=np.percentile(latencies, 99) if latencies else 0,
            throughput=total_requests / duration,
            success_rate=successful_requests / total_requests,
            errors=list(set(errors)),
            total_requests=total_requests,
            duration=duration
        )
    
    async def benchmark_async_queries(self, concurrent_requests: int = 50, 
                                     total_requests: int = 1000) -> BenchmarkResult:
        """Benchmark async query performance."""
        
        print(f"Running async benchmark ({concurrent_requests} concurrent, {total_requests} total)...")
        
        semaphore = asyncio.Semaphore(concurrent_requests)
        
        async def make_async_request(session, query):
            async with semaphore:
                payload = {
                    "method": "tools/call",
                    "params": {
                        "name": "cbr_retrieve",
                        "arguments": {
                            "query": query,
                            "max_results": 10,
                            "similarity_threshold": 0.7
                        }
                    }
                }
                
                start_time = time.time()
                try:
                    async with session.post(f"{self.base_url}/mcp", json=payload, timeout=30) as response:
                        end_time = time.time()
                        return {
                            "success": response.status == 200,
                            "response_time": end_time - start_time,
                            "status_code": response.status
                        }
                except Exception as e:
                    end_time = time.time()
                    return {
                        "success": False,
                        "response_time": end_time - start_time,
                        "error": str(e)
                    }
        
        start_time = time.time()
        
        # Create requests
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(total_requests):
                query = self.test_queries[i % len(self.test_queries)]
                task = make_async_request(session, query)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Analyze results
        latencies = [r["response_time"] for r in results if r["response_time"] > 0]
        successful_requests = sum(1 for r in results if r["success"])
        errors = [r.get("error", f"HTTP {r.get('status_code')}") for r in results if not r["success"]]
        
        return BenchmarkResult(
            name="Async Queries",
            avg_latency=statistics.mean(latencies) if latencies else 0,
            min_latency=min(latencies) if latencies else 0,
            max_latency=max(latencies) if latencies else 0,
            p95_latency=np.percentile(latencies, 95) if latencies else 0,
            p99_latency=np.percentile(latencies, 99) if latencies else 0,
            throughput=total_requests / duration,
            success_rate=successful_requests / total_requests,
            errors=list(set(errors)),
            total_requests=total_requests,
            duration=duration
        )
    
    def benchmark_cache_performance(self, cache_hit_queries: int = 50, 
                                   cache_miss_queries: int = 50) -> Dict[str, BenchmarkResult]:
        """Benchmark cache hit vs miss performance."""
        
        print("Running cache performance benchmark...")
        
        # First, populate cache with some queries
        cache_queries = self.test_queries[:5]  # Use first 5 queries for cache testing
        
        # Warm up cache
        for query in cache_queries:
            self._make_cbr_request(query)
        
        # Benchmark cache hits
        hit_latencies = []
        hit_errors = []
        hit_successful = 0
        
        start_time = time.time()
        for i in range(cache_hit_queries):
            query = cache_queries[i % len(cache_queries)]
            try:
                result = self._make_cbr_request(query)
                hit_latencies.append(result["response_time"])
                if result["success"]:
                    hit_successful += 1
                else:
                    hit_errors.append(f"HTTP {result['status_code']}")
            except Exception as e:
                hit_errors.append(str(e))
        
        hit_duration = time.time() - start_time
        
        # Benchmark cache misses (unique queries)
        miss_latencies = []
        miss_errors = []
        miss_successful = 0
        
        start_time = time.time()
        for i in range(cache_miss_queries):
            query = f"unique query for cache miss test {i} {time.time()}"
            try:
                result = self._make_cbr_request(query)
                miss_latencies.append(result["response_time"])
                if result["success"]:
                    miss_successful += 1
                else:
                    miss_errors.append(f"HTTP {result['status_code']}")
            except Exception as e:
                miss_errors.append(str(e))
        
        miss_duration = time.time() - start_time
        
        hit_result = BenchmarkResult(
            name="Cache Hits",
            avg_latency=statistics.mean(hit_latencies) if hit_latencies else 0,
            min_latency=min(hit_latencies) if hit_latencies else 0,
            max_latency=max(hit_latencies) if hit_latencies else 0,
            p95_latency=np.percentile(hit_latencies, 95) if hit_latencies else 0,
            p99_latency=np.percentile(hit_latencies, 99) if hit_latencies else 0,
            throughput=cache_hit_queries / hit_duration,
            success_rate=hit_successful / cache_hit_queries,
            errors=list(set(hit_errors)),
            total_requests=cache_hit_queries,
            duration=hit_duration
        )
        
        miss_result = BenchmarkResult(
            name="Cache Misses",
            avg_latency=statistics.mean(miss_latencies) if miss_latencies else 0,
            min_latency=min(miss_latencies) if miss_latencies else 0,
            max_latency=max(miss_latencies) if miss_latencies else 0,
            p95_latency=np.percentile(miss_latencies, 95) if miss_latencies else 0,
            p99_latency=np.percentile(miss_latencies, 99) if miss_latencies else 0,
            throughput=cache_miss_queries / miss_duration,
            success_rate=miss_successful / cache_miss_queries,
            errors=list(set(miss_errors)),
            total_requests=cache_miss_queries,
            duration=miss_duration
        )
        
        return {"cache_hits": hit_result, "cache_misses": miss_result}
    
    def run_full_benchmark_suite(self) -> Dict[str, Any]:
        """Run complete benchmark suite."""
        
        print("Starting CBR Performance Benchmark Suite")
        print("=" * 50)
        
        results = {}
        
        # Single query performance
        results["single_queries"] = self.benchmark_single_queries(100)
        
        # Concurrent performance
        results["concurrent_queries"] = self.benchmark_concurrent_queries(10, 10)
        
        # Async performance
        results["async_queries"] = asyncio.run(self.benchmark_async_queries(20, 200))
        
        # Cache performance
        cache_results = self.benchmark_cache_performance(50, 50)
        results.update(cache_results)
        
        return results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive performance report."""
        
        report = """
CBR MCP Server Performance Benchmark Report
===========================================

"""
        
        for test_name, result in results.items():
            if isinstance(result, BenchmarkResult):
                report += f"""
{result.name} Performance:
{'-' * (len(result.name) + 13)}
  Total Requests:    {result.total_requests}
  Duration:          {result.duration:.2f}s
  Success Rate:      {result.success_rate:.2%}
  Throughput:        {result.throughput:.2f} req/s
  
  Latency Statistics:
    Average:         {result.avg_latency:.3f}s
    Minimum:         {result.min_latency:.3f}s
    Maximum:         {result.max_latency:.3f}s
    95th Percentile: {result.p95_latency:.3f}s
    99th Percentile: {result.p99_latency:.3f}s
  
  Errors: {len(result.errors)} unique error types
"""
                if result.errors:
                    report += f"    Error Types: {', '.join(result.errors[:3])}\n"
        
        # Performance comparison
        if "cache_hits" in results and "cache_misses" in results:
            hit_avg = results["cache_hits"].avg_latency
            miss_avg = results["cache_misses"].avg_latency
            cache_speedup = miss_avg / hit_avg if hit_avg > 0 else 0
            
            report += f"""
Cache Performance Analysis:
---------------------------
  Cache Hit Latency:     {hit_avg:.3f}s
  Cache Miss Latency:    {miss_avg:.3f}s
  Cache Speedup:         {cache_speedup:.1f}x faster
"""
        
        # Performance recommendations
        report += """
Performance Recommendations:
----------------------------
"""
        
        single_result = results.get("single_queries")
        if single_result and single_result.avg_latency > 1.0:
            report += "  - Consider optimizing database queries (avg latency > 1s)\n"
        
        if single_result and single_result.success_rate < 0.95:
            report += "  - Investigate error causes (success rate < 95%)\n"
        
        concurrent_result = results.get("concurrent_queries")
        if concurrent_result and single_result:
            if concurrent_result.throughput < single_result.throughput * 8:
                report += "  - Poor concurrent scaling detected - check for bottlenecks\n"
        
        if "cache_hits" in results and results["cache_hits"].avg_latency > 0.1:
            report += "  - Cache performance suboptimal (consider faster cache backend)\n"
        
        return report

def main():
    """Main benchmarking function."""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='CBR MCP Server Performance Benchmark')
    parser.add_argument('--url', default='http://localhost:8080', help='CBR server URL')
    parser.add_argument('--output', help='Output file for results JSON')
    
    args = parser.parse_args()
    
    # Run benchmark suite
    benchmark = CBRBenchmarkSuite(args.url)
    results = benchmark.run_full_benchmark_suite()
    
    # Generate and display report
    report = benchmark.generate_report(results)
    print(report)
    
    # Save results to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            # Convert results to JSON-serializable format
            json_results = {}
            for key, result in results.items():
                if isinstance(result, BenchmarkResult):
                    json_results[key] = {
                        'name': result.name,
                        'avg_latency': result.avg_latency,
                        'min_latency': result.min_latency,
                        'max_latency': result.max_latency,
                        'p95_latency': result.p95_latency,
                        'p99_latency': result.p99_latency,
                        'throughput': result.throughput,
                        'success_rate': result.success_rate,
                        'errors': result.errors,
                        'total_requests': result.total_requests,
                        'duration': result.duration
                    }
            
            json.dump(json_results, f, indent=2)
            print(f"\nResults saved to: {args.output}")

if __name__ == "__main__":
    main()
```

This comprehensive performance tuning guide provides detailed optimization strategies, configuration examples, and benchmarking tools to maximize the performance of the CBR MCP Server across different deployment scenarios and workload requirements.