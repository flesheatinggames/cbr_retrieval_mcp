"""
Unit tests for ChromaDB index optimization configuration.

This test module validates:
1. IndexOptimizationConfig data model validation (required fields, defaults, validation rules)
2. HNSW parameter configuration (valid parameter ranges, invalid parameter handling)
3. Conversion to ChromaDB-compatible metadata format
4. Serialization/deserialization for config persistence

These tests follow TDD principles and should fail initially as IndexOptimizationConfig
model doesn't exist yet.
"""

import pytest
from pydantic import ValidationError

# Test will fail until IndexOptimizationConfig is implemented
try:
    from cbr_mcp_server.performance.data_models import IndexOptimizationConfig
except ImportError:
    IndexOptimizationConfig = None


@pytest.mark.skipif(
    IndexOptimizationConfig is None,
    reason="IndexOptimizationConfig not implemented yet",
)
class TestIndexOptimizationConfig:
    """Test suite for IndexOptimizationConfig data model validation."""

    def test_index_optimization_config_creation_with_all_fields(self):
        """
        Verify that IndexOptimizationConfig can be instantiated with all valid fields.

        This test ensures the model accepts all expected HNSW parameters:
        - space: Distance metric type
        - ef_construction: Build-time search parameter
        - ef_search: Query-time search parameter
        - M: Number of bi-directional links per node
        """
        config = IndexOptimizationConfig(
            space="l2", ef_construction=200, ef_search=100, M=16
        )

        assert config.space == "l2"
        assert config.ef_construction == 200
        assert config.ef_search == 100
        assert config.M == 16

    def test_index_optimization_config_with_defaults(self):
        """
        Verify that IndexOptimizationConfig uses appropriate default values.

        Default values should follow ChromaDB HNSW best practices:
        - space: "l2" (Euclidean distance)
        - ef_construction: 100 (balanced build time/accuracy)
        - ef_search: 10 (fast queries)
        - M: 16 (standard connectivity)
        """
        config = IndexOptimizationConfig()

        # Verify defaults are set (exact values defined in implementation)
        assert config.space in ["l2", "ip", "cosine"]
        assert config.ef_construction > 0
        assert config.ef_search > 0
        assert config.M > 0

    def test_index_optimization_config_space_type_validation_valid(self):
        """
        Verify that valid space types are accepted.

        ChromaDB supports three distance metrics:
        - l2: Euclidean distance (default)
        - ip: Inner product (dot product)
        - cosine: Cosine similarity
        """
        # Test all valid space types
        valid_spaces = ["l2", "ip", "cosine"]

        for space in valid_spaces:
            config = IndexOptimizationConfig(space=space)
            assert config.space == space

    def test_index_optimization_config_space_type_validation_invalid(self):
        """
        Verify that invalid space types raise ValidationError.

        Any space type not in [l2, ip, cosine] should be rejected.
        """
        invalid_spaces = ["euclidean", "manhattan", "hamming", "invalid", ""]

        for space in invalid_spaces:
            with pytest.raises(ValidationError) as exc_info:
                IndexOptimizationConfig(space=space)

            # Verify error message mentions space validation
            assert "space" in str(exc_info.value).lower()

    def test_index_optimization_config_ef_construction_validation_valid(self):
        """
        Verify that ef_construction accepts valid positive integers.

        Valid range is typically 4 to 1000 based on ChromaDB/HNSW documentation:
        - Lower values: faster build, lower accuracy
        - Higher values: slower build, higher accuracy
        - Typical range: 100-400
        """
        valid_values = [4, 10, 50, 100, 200, 400, 1000]

        for value in valid_values:
            config = IndexOptimizationConfig(ef_construction=value)
            assert config.ef_construction == value

    def test_index_optimization_config_ef_construction_validation_invalid(self):
        """
        Verify that invalid ef_construction values raise ValidationError.

        Invalid values include:
        - Zero
        - Negative numbers
        - Values outside valid range (< 4 or > 1000)
        """
        invalid_values = [0, -1, -100, 1, 2, 3, 1001, 2000]

        for value in invalid_values:
            with pytest.raises(ValidationError) as exc_info:
                IndexOptimizationConfig(ef_construction=value)

            # Verify error message mentions ef_construction validation
            assert "ef_construction" in str(exc_info.value).lower()

    def test_index_optimization_config_ef_search_validation_valid(self):
        """
        Verify that ef_search accepts valid positive integers.

        Valid range is typically 1 to ef_construction based on HNSW algorithm:
        - Lower values: faster queries, lower accuracy
        - Higher values: slower queries, higher accuracy
        - Should be <= ef_construction for optimal performance
        """
        valid_values = [1, 5, 10, 50, 100, 200]

        for value in valid_values:
            config = IndexOptimizationConfig(ef_search=value)
            assert config.ef_search == value

    def test_index_optimization_config_ef_search_validation_invalid(self):
        """
        Verify that invalid ef_search values raise ValidationError.

        Invalid values include:
        - Zero
        - Negative numbers
        """
        invalid_values = [0, -1, -50]

        for value in invalid_values:
            with pytest.raises(ValidationError) as exc_info:
                IndexOptimizationConfig(ef_search=value)

            # Verify error message mentions ef_search validation
            assert "ef_search" in str(exc_info.value).lower()

    def test_index_optimization_config_m_parameter_validation_valid(self):
        """
        Verify that M parameter accepts valid positive integers.

        Valid range is typically 4 to 64 based on HNSW algorithm:
        - Lower values: less memory, lower accuracy
        - Higher values: more memory, higher accuracy
        - Typical range: 8-32
        """
        valid_values = [4, 8, 12, 16, 24, 32, 48, 64]

        for value in valid_values:
            config = IndexOptimizationConfig(M=value)
            assert config.M == value

    def test_index_optimization_config_m_parameter_validation_invalid(self):
        """
        Verify that invalid M parameter values raise ValidationError.

        Invalid values include:
        - Zero
        - Negative numbers
        - Values outside valid range (< 4 or > 64)
        """
        invalid_values = [0, -1, 1, 2, 3, 65, 100, 200]

        for value in invalid_values:
            with pytest.raises(ValidationError) as exc_info:
                IndexOptimizationConfig(M=value)

            # Verify error message mentions M validation
            assert "m" in str(exc_info.value).lower()

    def test_index_optimization_config_ef_search_less_than_ef_construction(self):
        """
        Verify business rule that ef_search should be <= ef_construction.

        HNSW algorithm requires ef_search <= ef_construction for optimal performance.
        While technically ef_search can exceed ef_construction, it provides no benefit
        and wastes computation, so this should raise a validation error or warning.
        """
        # Valid: ef_search <= ef_construction
        valid_config = IndexOptimizationConfig(ef_construction=200, ef_search=100)
        assert valid_config.ef_search <= valid_config.ef_construction

        # Valid: ef_search == ef_construction (boundary case)
        equal_config = IndexOptimizationConfig(ef_construction=100, ef_search=100)
        assert equal_config.ef_search == equal_config.ef_construction

        # Invalid: ef_search > ef_construction
        with pytest.raises(ValidationError) as exc_info:
            IndexOptimizationConfig(ef_construction=100, ef_search=200)

        # Verify error message mentions ef_search/ef_construction relationship
        error_msg = str(exc_info.value).lower()
        assert "ef_search" in error_msg and "ef_construction" in error_msg

    def test_index_optimization_config_serialization(self):
        """
        Verify that IndexOptimizationConfig can be serialized to dict/JSON.

        This is required for:
        - Saving configuration to files
        - Passing configuration via API
        - Logging configuration state
        """
        config = IndexOptimizationConfig(
            space="cosine", ef_construction=200, ef_search=100, M=16
        )

        # Serialize to dict
        config_dict = config.model_dump()

        # Verify all fields are present
        assert config_dict["space"] == "cosine"
        assert config_dict["ef_construction"] == 200
        assert config_dict["ef_search"] == 100
        assert config_dict["M"] == 16

        # Verify it's a plain dict (not a Pydantic model)
        assert isinstance(config_dict, dict)

    def test_index_optimization_config_deserialization(self):
        """
        Verify that IndexOptimizationConfig can be deserialized from dict/JSON.

        This is required for:
        - Loading configuration from files
        - Receiving configuration via API
        - Restoring configuration state
        """
        config_dict = {
            "space": "ip",
            "ef_construction": 150,
            "ef_search": 75,
            "M": 24,
        }

        # Deserialize from dict
        config = IndexOptimizationConfig(**config_dict)

        # Verify all fields are correctly set
        assert config.space == "ip"
        assert config.ef_construction == 150
        assert config.ef_search == 75
        assert config.M == 24

    def test_index_optimization_config_type_validation(self):
        """
        Verify that incorrect types raise ValidationError.

        Pydantic should enforce type checking:
        - Integer fields should reject strings
        - String fields should reject integers (for space)
        """
        # Test string instead of integer for ef_construction
        with pytest.raises(ValidationError):
            IndexOptimizationConfig(ef_construction="200")

        # Test string instead of integer for ef_search
        with pytest.raises(ValidationError):
            IndexOptimizationConfig(ef_search="100")

        # Test string instead of integer for M
        with pytest.raises(ValidationError):
            IndexOptimizationConfig(M="16")

        # Test integer instead of string for space (should still work via coercion or fail)
        with pytest.raises(ValidationError):
            IndexOptimizationConfig(space=123)

    def test_index_optimization_config_none_values(self):
        """
        Verify that None values are handled appropriately.

        All fields should be required (no None allowed) or have defaults.
        """
        # If all fields have defaults, this should work
        config = IndexOptimizationConfig()
        assert config is not None

        # Explicit None should be rejected for required fields
        with pytest.raises(ValidationError):
            IndexOptimizationConfig(space=None)

        with pytest.raises(ValidationError):
            IndexOptimizationConfig(ef_construction=None)

        with pytest.raises(ValidationError):
            IndexOptimizationConfig(ef_search=None)

        with pytest.raises(ValidationError):
            IndexOptimizationConfig(M=None)


@pytest.mark.skipif(
    IndexOptimizationConfig is None,
    reason="IndexOptimizationConfig not implemented yet",
)
class TestHNSWParameterConfiguration:
    """Test suite for HNSW parameter configuration and ChromaDB integration."""

    def test_hnsw_config_to_chroma_metadata(self):
        """
        Verify conversion of IndexOptimizationConfig to ChromaDB-compatible metadata.

        ChromaDB expects HNSW parameters in specific metadata keys:
        - hnsw:space: Distance metric
        - hnsw:construction_ef: Build-time search parameter
        - hnsw:search_ef: Query-time search parameter
        - hnsw:M: Bi-directional links per node
        """
        config = IndexOptimizationConfig(
            space="l2", ef_construction=200, ef_search=100, M=16
        )

        # Convert to ChromaDB metadata format
        metadata = config.to_chroma_metadata()

        # Verify metadata structure
        assert isinstance(metadata, dict)
        assert metadata["hnsw:space"] == "l2"
        assert metadata["hnsw:construction_ef"] == 200
        assert metadata["hnsw:search_ef"] == 100
        assert metadata["hnsw:M"] == 16

    def test_hnsw_config_default_parameter_application(self):
        """
        Verify that default configuration produces valid ChromaDB metadata.

        This ensures defaults are production-ready and don't require
        explicit configuration for basic use cases.
        """
        config = IndexOptimizationConfig()

        # Convert to ChromaDB metadata
        metadata = config.to_chroma_metadata()

        # Verify metadata is valid and complete
        assert "hnsw:space" in metadata
        assert "hnsw:construction_ef" in metadata
        assert "hnsw:search_ef" in metadata
        assert "hnsw:M" in metadata

        # Verify values are within valid ranges
        assert metadata["hnsw:space"] in ["l2", "ip", "cosine"]
        assert metadata["hnsw:construction_ef"] >= 4
        assert metadata["hnsw:search_ef"] >= 1
        assert metadata["hnsw:M"] >= 4
        assert metadata["hnsw:M"] <= 64

    def test_hnsw_config_space_type_mapping(self):
        """
        Verify that space types map correctly to ChromaDB HNSW format.

        ChromaDB uses specific string values for distance metrics:
        - "l2": Euclidean distance
        - "ip": Inner product
        - "cosine": Cosine similarity
        """
        space_mappings = {
            "l2": "l2",
            "ip": "ip",
            "cosine": "cosine",
        }

        for input_space, expected_chroma_space in space_mappings.items():
            config = IndexOptimizationConfig(space=input_space)
            metadata = config.to_chroma_metadata()

            assert (
                metadata["hnsw:space"] == expected_chroma_space
            ), f"Space type {input_space} did not map correctly to ChromaDB format"

    def test_hnsw_config_parameter_bounds_enforcement(self):
        """
        Verify that parameter bounds are enforced when converting to ChromaDB metadata.

        This ensures invalid configurations cannot be accidentally applied to ChromaDB.
        """
        # Create config with boundary values
        config = IndexOptimizationConfig(
            space="l2",
            ef_construction=4,  # Minimum valid value
            ef_search=1,  # Minimum valid value
            M=4,  # Minimum valid value
        )

        metadata = config.to_chroma_metadata()

        # Verify boundary values are preserved
        assert metadata["hnsw:construction_ef"] == 4
        assert metadata["hnsw:search_ef"] == 1
        assert metadata["hnsw:M"] == 4

    def test_hnsw_config_performance_presets(self):
        """
        Verify that common performance presets produce expected metadata.

        This test documents recommended configurations for different use cases:
        - Fast: Optimized for query speed
        - Balanced: Trade-off between speed and accuracy
        - Accurate: Optimized for retrieval accuracy
        """
        # Fast preset: Lower parameters for speed
        fast_config = IndexOptimizationConfig(
            space="l2", ef_construction=50, ef_search=10, M=8
        )
        fast_metadata = fast_config.to_chroma_metadata()

        assert fast_metadata["hnsw:construction_ef"] == 50
        assert fast_metadata["hnsw:search_ef"] == 10
        assert fast_metadata["hnsw:M"] == 8

        # Balanced preset: Standard parameters
        balanced_config = IndexOptimizationConfig(
            space="l2", ef_construction=100, ef_search=50, M=16
        )
        balanced_metadata = balanced_config.to_chroma_metadata()

        assert balanced_metadata["hnsw:construction_ef"] == 100
        assert balanced_metadata["hnsw:search_ef"] == 50
        assert balanced_metadata["hnsw:M"] == 16

        # Accurate preset: Higher parameters for accuracy
        accurate_config = IndexOptimizationConfig(
            space="l2", ef_construction=400, ef_search=200, M=32
        )
        accurate_metadata = accurate_config.to_chroma_metadata()

        assert accurate_metadata["hnsw:construction_ef"] == 400
        assert accurate_metadata["hnsw:search_ef"] == 200
        assert accurate_metadata["hnsw:M"] == 32
