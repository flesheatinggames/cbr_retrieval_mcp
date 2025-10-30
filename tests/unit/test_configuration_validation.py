"""
Test Configuration Validation System for CBR MCP Server

This test suite covers Task 5 (Configuration Validation) from the production stability spec:
- Startup configuration validator using Pydantic models
- Database path validation and accessibility checks  
- Embedding model availability verification
- ChromaDB connectivity validation on startup
- YAML configuration file loading and validation
- Environment variable override support
- Various failure scenarios and error conditions
- Successful validation scenarios

All tests are designed to fail initially as the configuration validation implementation 
does not yet exist.
"""

import pytest
import os
import tempfile
import yaml
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from pydantic import ValidationError
import chromadb
from sentence_transformers import SentenceTransformer

# Import the configuration validation classes that will be implemented
# These imports will fail initially, which is expected for TDD
try:
    from cbr_mcp_server import (
        CBRServerConfig,
        ConfigurationValidator,
        startup_configuration_validator,
        load_configuration_from_file,
        load_configuration_with_env_overrides
    )
except ImportError:
    # This is expected in TDD - the implementation doesn't exist yet
    CBRServerConfig = None
    ConfigurationValidator = None
    startup_configuration_validator = None
    load_configuration_from_file = None
    load_configuration_with_env_overrides = None


class TestCBRServerConfigModel:
    """Test the Pydantic configuration model."""
    
    def test_valid_configuration_creation(self):
        """Test that valid configuration data creates a proper config object."""
        config_data = {
            "database_path": "./test_db",
            "collection_name": "test_collection",
            "embedding_model": "nomic-ai/nomic-embed-text-v1.5",
            "max_results_default": 10,
            "similarity_threshold_default": 0.7,
            "enable_health_checks": True,
            "log_level": "INFO"
        }
        
        config = CBRServerConfig(**config_data)
        
        assert config.database_path == "./test_db"
        assert config.collection_name == "test_collection"
        assert config.embedding_model == "nomic-ai/nomic-embed-text-v1.5"
        assert config.max_results_default == 10
        assert config.similarity_threshold_default == 0.7
        assert config.enable_health_checks is True
        assert config.log_level == "INFO"
    
    def test_invalid_database_path_validation(self):
        """Test that invalid database paths raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            CBRServerConfig(
                database_path="",  # Empty path should be invalid
                collection_name="test_collection"
            )
        
        assert "database_path" in str(exc_info.value)
    
    def test_invalid_similarity_threshold_validation(self):
        """Test that similarity thresholds outside 0-1 range raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            CBRServerConfig(
                database_path="./test_db",
                similarity_threshold_default=1.5  # Invalid: > 1.0
            )
        
        assert "similarity_threshold_default" in str(exc_info.value)
    
    def test_invalid_max_results_validation(self):
        """Test that negative max_results raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            CBRServerConfig(
                database_path="./test_db",
                max_results_default=-1  # Invalid: negative
            )
        
        assert "max_results_default" in str(exc_info.value)
    
    def test_invalid_log_level_validation(self):
        """Test that invalid log levels raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            CBRServerConfig(
                database_path="./test_db",
                log_level="INVALID_LEVEL"
            )
        
        assert "log_level" in str(exc_info.value)


class TestDatabasePathValidation:
    """Test database path validation and accessibility checks."""
    
    @patch('os.path.exists')
    @patch('os.access')
    def test_valid_existing_database_path(self, mock_access, mock_exists):
        """Test validation of existing, accessible database path."""
        mock_exists.return_value = True
        mock_access.return_value = True
        
        validator = ConfigurationValidator()
        config = CBRServerConfig(database_path="./existing_db")
        
        result = validator.validate_database_path(config.database_path)
        
        assert result is True
        mock_exists.assert_called_once_with("./existing_db")
        mock_access.assert_called_once_with("./existing_db", os.R_OK | os.W_OK)
    
    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('os.access')
    def test_create_missing_database_directory(self, mock_access, mock_makedirs, mock_exists):
        """Test creation of missing database directory."""
        mock_exists.return_value = False
        mock_makedirs.return_value = None
        mock_access.return_value = True
        
        validator = ConfigurationValidator()
        config = CBRServerConfig(database_path="./new_db")
        
        result = validator.validate_database_path(config.database_path)
        
        assert result is True
        mock_exists.assert_called_with("./new_db")
        mock_makedirs.assert_called_once_with("./new_db", exist_ok=True)
    
    @patch('os.path.exists')
    @patch('os.access')
    def test_database_path_permission_denied(self, mock_access, mock_exists):
        """Test validation failure when database path lacks permissions."""
        mock_exists.return_value = True
        mock_access.return_value = False  # No read/write access
        
        validator = ConfigurationValidator()
        config = CBRServerConfig(database_path="./no_access_db")
        
        with pytest.raises(PermissionError) as exc_info:
            validator.validate_database_path(config.database_path)
        
        assert "database_path" in str(exc_info.value)
        assert "./no_access_db" in str(exc_info.value)
    
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_database_directory_creation_failure(self, mock_makedirs, mock_exists):
        """Test validation failure when directory creation fails."""
        mock_exists.return_value = False
        mock_makedirs.side_effect = OSError("Permission denied")
        
        validator = ConfigurationValidator()
        config = CBRServerConfig(database_path="./failed_db")
        
        with pytest.raises(OSError) as exc_info:
            validator.validate_database_path(config.database_path)
        
        assert "Permission denied" in str(exc_info.value)


class TestEmbeddingModelValidation:
    """Test embedding model availability verification."""
    
    @patch('sentence_transformers.SentenceTransformer')
    def test_valid_embedding_model_loading(self, mock_transformer):
        """Test successful loading of valid embedding model."""
        mock_model = MagicMock()
        mock_transformer.return_value = mock_model
        
        validator = ConfigurationValidator()
        config = CBRServerConfig(embedding_model="nomic-ai/nomic-embed-text-v1.5")
        
        result = validator.validate_embedding_model(config.embedding_model)
        
        assert result is True
        mock_transformer.assert_called_once_with("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)
    
    @patch('sentence_transformers.SentenceTransformer')
    def test_embedding_model_loading_failure(self, mock_transformer):
        """Test validation failure when embedding model cannot be loaded."""
        mock_transformer.side_effect = Exception("Model not found")
        
        validator = ConfigurationValidator()
        config = CBRServerConfig(embedding_model="invalid/model")
        
        with pytest.raises(Exception) as exc_info:
            validator.validate_embedding_model(config.embedding_model)
        
        assert "Model not found" in str(exc_info.value)
    
    @patch('sentence_transformers.SentenceTransformer')
    def test_embedding_model_network_failure(self, mock_transformer):
        """Test validation failure due to network issues during model download."""
        mock_transformer.side_effect = ConnectionError("Network unreachable")
        
        validator = ConfigurationValidator()
        config = CBRServerConfig(embedding_model="nomic-ai/nomic-embed-text-v1.5")
        
        with pytest.raises(ConnectionError) as exc_info:
            validator.validate_embedding_model(config.embedding_model)
        
        assert "Network unreachable" in str(exc_info.value)


class TestChromaDBValidation:
    """Test ChromaDB connectivity validation on startup."""
    
    @patch('chromadb.PersistentClient')
    def test_successful_chromadb_connection(self, mock_client):
        """Test successful ChromaDB connection and collection access."""
        mock_chroma_client = MagicMock()
        mock_collection = MagicMock()
        mock_client.return_value = mock_chroma_client
        mock_chroma_client.get_or_create_collection.return_value = mock_collection
        
        validator = ConfigurationValidator()
        config = CBRServerConfig(
            database_path="./test_db",
            collection_name="test_collection"
        )
        
        result = validator.validate_chromadb_connectivity(
            config.database_path, 
            config.collection_name
        )
        
        assert result is True
        mock_client.assert_called_once_with(path="./test_db")
        mock_chroma_client.get_or_create_collection.assert_called_once_with(
            name="test_collection"
        )
    
    @patch('chromadb.PersistentClient')
    def test_chromadb_connection_failure(self, mock_client):
        """Test validation failure when ChromaDB connection fails."""
        mock_client.side_effect = Exception("Database connection failed")
        
        validator = ConfigurationValidator()
        config = CBRServerConfig(database_path="./test_db")
        
        with pytest.raises(Exception) as exc_info:
            validator.validate_chromadb_connectivity(config.database_path, "test_collection")
        
        assert "Database connection failed" in str(exc_info.value)
    
    @patch('chromadb.PersistentClient')
    def test_chromadb_collection_access_failure(self, mock_client):
        """Test validation failure when collection cannot be accessed."""
        mock_chroma_client = MagicMock()
        mock_client.return_value = mock_chroma_client
        mock_chroma_client.get_or_create_collection.side_effect = Exception("Collection access failed")
        
        validator = ConfigurationValidator()
        config = CBRServerConfig(database_path="./test_db")
        
        with pytest.raises(Exception) as exc_info:
            validator.validate_chromadb_connectivity(config.database_path, "test_collection")
        
        assert "Collection access failed" in str(exc_info.value)
    
    @patch('chromadb.PersistentClient')
    def test_chromadb_corrupted_database(self, mock_client):
        """Test validation failure when database files are corrupted."""
        mock_client.side_effect = Exception("Database corrupted")
        
        validator = ConfigurationValidator()
        config = CBRServerConfig(database_path="./corrupted_db")
        
        with pytest.raises(Exception) as exc_info:
            validator.validate_chromadb_connectivity(config.database_path, "test_collection")
        
        assert "Database corrupted" in str(exc_info.value)


class TestConfigurationFileLoading:
    """Test YAML configuration file loading and validation."""
    
    def test_load_valid_yaml_configuration(self):
        """Test loading valid YAML configuration file."""
        valid_config = {
            "database_path": "./config_db",
            "collection_name": "config_collection",
            "embedding_model": "nomic-ai/nomic-embed-text-v1.5",
            "max_results_default": 15,
            "similarity_threshold_default": 0.8,
            "enable_health_checks": True,
            "log_level": "DEBUG"
        }
        
        with patch("builtins.open", mock_open(read_data=yaml.dump(valid_config))):
            with patch("os.path.exists", return_value=True):
                config = load_configuration_from_file("config.yaml")
        
        assert isinstance(config, CBRServerConfig)
        assert config.database_path == "./config_db"
        assert config.collection_name == "config_collection"
        assert config.max_results_default == 15
        assert config.similarity_threshold_default == 0.8
        assert config.log_level == "DEBUG"
    
    def test_load_missing_configuration_file(self):
        """Test handling of missing configuration file."""
        with patch("os.path.exists", return_value=False):
            with pytest.raises(FileNotFoundError) as exc_info:
                load_configuration_from_file("missing_config.yaml")
        
        assert "missing_config.yaml" in str(exc_info.value)
    
    def test_load_invalid_yaml_syntax(self):
        """Test handling of malformed YAML syntax."""
        invalid_yaml = """
        database_path: "./test_db"
        collection_name: "test
        invalid_yaml_here: [unclosed_bracket
        """
        
        with patch("builtins.open", mock_open(read_data=invalid_yaml)):
            with patch("os.path.exists", return_value=True):
                with pytest.raises(yaml.YAMLError) as exc_info:
                    load_configuration_from_file("invalid.yaml")
        
        assert "YAML" in str(exc_info.value) or "yaml" in str(exc_info.value).lower()
    
    def test_load_yaml_with_invalid_configuration_values(self):
        """Test handling of YAML with invalid configuration values."""
        invalid_config = {
            "database_path": "",  # Invalid: empty path
            "similarity_threshold_default": 2.0,  # Invalid: > 1.0
            "max_results_default": -5,  # Invalid: negative
            "log_level": "INVALID_LEVEL"  # Invalid: not a valid log level
        }
        
        with patch("builtins.open", mock_open(read_data=yaml.dump(invalid_config))):
            with patch("os.path.exists", return_value=True):
                with pytest.raises(ValidationError) as exc_info:
                    load_configuration_from_file("invalid_values.yaml")
        
        assert "ValidationError" in str(type(exc_info.value))
    
    def test_load_yaml_with_missing_required_fields(self):
        """Test handling of YAML missing required configuration fields."""
        incomplete_config = {
            "collection_name": "test_collection"
            # Missing required database_path
        }
        
        with patch("builtins.open", mock_open(read_data=yaml.dump(incomplete_config))):
            with patch("os.path.exists", return_value=True):
                with pytest.raises(ValidationError) as exc_info:
                    load_configuration_from_file("incomplete.yaml")
        
        assert "database_path" in str(exc_info.value)


class TestEnvironmentVariableOverrides:
    """Test environment variable override support."""
    
    def test_environment_variable_precedence_over_config_file(self):
        """Test that environment variables override config file values."""
        file_config = {
            "database_path": "./file_db",
            "collection_name": "file_collection",
            "max_results_default": 10,
            "log_level": "INFO"
        }
        
        env_overrides = {
            "CBR_DATABASE_PATH": "./env_db",
            "CBR_MAX_RESULTS_DEFAULT": "20",
            "CBR_LOG_LEVEL": "DEBUG"
        }
        
        with patch("builtins.open", mock_open(read_data=yaml.dump(file_config))):
            with patch("os.path.exists", return_value=True):
                with patch.dict(os.environ, env_overrides):
                    config = load_configuration_with_env_overrides("config.yaml")
        
        assert config.database_path == "./env_db"  # Overridden by env
        assert config.collection_name == "file_collection"  # From file
        assert config.max_results_default == 20  # Overridden by env
        assert config.log_level == "DEBUG"  # Overridden by env
    
    def test_environment_variable_type_conversion(self):
        """Test proper type conversion of environment variables."""
        file_config = {
            "database_path": "./file_db",
            "collection_name": "file_collection"
        }
        
        env_overrides = {
            "CBR_MAX_RESULTS_DEFAULT": "25",  # String -> int
            "CBR_SIMILARITY_THRESHOLD_DEFAULT": "0.9",  # String -> float
            "CBR_ENABLE_HEALTH_CHECKS": "false"  # String -> bool
        }
        
        with patch("builtins.open", mock_open(read_data=yaml.dump(file_config))):
            with patch("os.path.exists", return_value=True):
                with patch.dict(os.environ, env_overrides):
                    config = load_configuration_with_env_overrides("config.yaml")
        
        assert config.max_results_default == 25
        assert config.similarity_threshold_default == 0.9
        assert config.enable_health_checks is False
    
    def test_invalid_environment_variable_values(self):
        """Test validation of invalid environment variable values."""
        file_config = {
            "database_path": "./file_db",
            "collection_name": "file_collection"
        }
        
        env_overrides = {
            "CBR_SIMILARITY_THRESHOLD_DEFAULT": "invalid_float",  # Invalid type conversion
        }
        
        with patch("builtins.open", mock_open(read_data=yaml.dump(file_config))):
            with patch("os.path.exists", return_value=True):
                with patch.dict(os.environ, env_overrides):
                    with pytest.raises((ValueError, ValidationError)) as exc_info:
                        load_configuration_with_env_overrides("config.yaml")
        
        assert "invalid_float" in str(exc_info.value) or "similarity_threshold" in str(exc_info.value).lower()
    
    def test_partial_environment_overrides(self):
        """Test scenarios where only some values are overridden via environment."""
        file_config = {
            "database_path": "./file_db",
            "collection_name": "file_collection",
            "embedding_model": "file-model",
            "max_results_default": 10,
            "similarity_threshold_default": 0.7,
            "enable_health_checks": True,
            "log_level": "INFO"
        }
        
        env_overrides = {
            "CBR_DATABASE_PATH": "./env_db",  # Only override database path
            "CBR_LOG_LEVEL": "ERROR"  # Only override log level
        }
        
        with patch("builtins.open", mock_open(read_data=yaml.dump(file_config))):
            with patch("os.path.exists", return_value=True):
                with patch.dict(os.environ, env_overrides):
                    config = load_configuration_with_env_overrides("config.yaml")
        
        # Overridden values
        assert config.database_path == "./env_db"
        assert config.log_level == "ERROR"
        
        # Non-overridden values from file
        assert config.collection_name == "file_collection"
        assert config.embedding_model == "file-model"
        assert config.max_results_default == 10
        assert config.similarity_threshold_default == 0.7
        assert config.enable_health_checks is True


class TestStartupValidationIntegration:
    """Test complete startup validation flow integration."""
    
    @patch('os.path.exists')
    @patch('os.access')
    @patch('sentence_transformers.SentenceTransformer')
    @patch('chromadb.PersistentClient')
    def test_complete_successful_startup_validation(
        self, mock_chroma_client, mock_transformer, mock_access, mock_exists
    ):
        """Test successful complete startup validation flow."""
        # Mock all dependencies to succeed
        mock_exists.return_value = True
        mock_access.return_value = True
        mock_transformer.return_value = MagicMock()
        mock_client = MagicMock()
        mock_chroma_client.return_value = mock_client
        mock_client.get_or_create_collection.return_value = MagicMock()
        
        config = CBRServerConfig(
            database_path="./test_db",
            collection_name="test_collection",
            embedding_model="nomic-ai/nomic-embed-text-v1.5"
        )
        
        result = startup_configuration_validator(config)
        
        assert result is True
        mock_exists.assert_called()
        mock_access.assert_called()
        mock_transformer.assert_called()
        mock_chroma_client.assert_called()
    
    @patch('os.path.exists')
    def test_startup_validation_early_failure_database_path(self, mock_exists):
        """Test that startup validation fails early for invalid database path."""
        mock_exists.return_value = False
        
        # Mock os.makedirs to fail
        with patch('os.makedirs', side_effect=PermissionError("Permission denied")):
            config = CBRServerConfig(database_path="./invalid_db")
            
            with pytest.raises(PermissionError) as exc_info:
                startup_configuration_validator(config)
            
            assert "Permission denied" in str(exc_info.value)
    
    @patch('os.path.exists')
    @patch('os.access')
    @patch('sentence_transformers.SentenceTransformer')
    def test_startup_validation_embedding_model_failure(
        self, mock_transformer, mock_access, mock_exists
    ):
        """Test that startup validation fails for embedding model issues."""
        mock_exists.return_value = True
        mock_access.return_value = True
        mock_transformer.side_effect = Exception("Model loading failed")
        
        config = CBRServerConfig(
            database_path="./test_db",
            embedding_model="invalid/model"
        )
        
        with pytest.raises(Exception) as exc_info:
            startup_configuration_validator(config)
        
        assert "Model loading failed" in str(exc_info.value)
    
    @patch('os.path.exists')
    @patch('os.access')  
    @patch('sentence_transformers.SentenceTransformer')
    @patch('chromadb.PersistentClient')
    def test_startup_validation_chromadb_failure(
        self, mock_chroma_client, mock_transformer, mock_access, mock_exists
    ):
        """Test that startup validation fails for ChromaDB connectivity issues."""
        mock_exists.return_value = True
        mock_access.return_value = True
        mock_transformer.return_value = MagicMock()
        mock_chroma_client.side_effect = Exception("ChromaDB connection failed")
        
        config = CBRServerConfig(database_path="./test_db")
        
        with pytest.raises(Exception) as exc_info:
            startup_configuration_validator(config)
        
        assert "ChromaDB connection failed" in str(exc_info.value)
    
    def test_startup_validation_with_configuration_file(self):
        """Test startup validation using configuration loaded from file."""
        valid_config = {
            "database_path": "./config_db",
            "collection_name": "config_collection",
            "embedding_model": "nomic-ai/nomic-embed-text-v1.5"
        }
        
        with patch("builtins.open", mock_open(read_data=yaml.dump(valid_config))):
            with patch("os.path.exists", return_value=True):
                with patch("os.access", return_value=True):
                    with patch("sentence_transformers.SentenceTransformer"):
                        with patch("chromadb.PersistentClient") as mock_client:
                            mock_client.return_value.get_or_create_collection.return_value = MagicMock()
                            
                            config = load_configuration_from_file("config.yaml")
                            result = startup_configuration_validator(config)
        
        assert result is True
    
    def test_startup_validation_with_env_overrides(self):
        """Test startup validation with environment variable overrides."""
        file_config = {
            "database_path": "./file_db",
            "collection_name": "file_collection",
            "embedding_model": "nomic-ai/nomic-embed-text-v1.5"
        }
        
        env_overrides = {
            "CBR_DATABASE_PATH": "./env_db",
            "CBR_COLLECTION_NAME": "env_collection"
        }
        
        with patch("builtins.open", mock_open(read_data=yaml.dump(file_config))):
            with patch("os.path.exists", return_value=True):
                with patch("os.access", return_value=True):
                    with patch("sentence_transformers.SentenceTransformer"):
                        with patch("chromadb.PersistentClient") as mock_client:
                            mock_client.return_value.get_or_create_collection.return_value = MagicMock()
                            with patch.dict(os.environ, env_overrides):
                                
                                config = load_configuration_with_env_overrides("config.yaml")
                                result = startup_configuration_validator(config)
        
        assert result is True


class TestErrorConditionsAndEdgeCases:
    """Test various error conditions and edge cases for configuration validation."""
    
    def test_configuration_with_extreme_values(self):
        """Test configuration validation with extreme but valid values."""
        config_data = {
            "database_path": "./test_db",
            "max_results_default": 1,  # Minimum valid value
            "similarity_threshold_default": 0.0,  # Minimum valid value
        }
        
        config = CBRServerConfig(**config_data)
        
        assert config.max_results_default == 1
        assert config.similarity_threshold_default == 0.0
    
    def test_configuration_with_unicode_paths(self):
        """Test configuration validation with Unicode characters in paths."""
        config_data = {
            "database_path": "./тест_данные/数据库",  # Unicode characters
            "collection_name": "测试_коллекция",  # Unicode collection name
        }
        
        config = CBRServerConfig(**config_data)
        
        assert config.database_path == "./тест_данные/数据库"
        assert config.collection_name == "测试_коллекция"
    
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_database_path_race_condition(self, mock_makedirs, mock_exists):
        """Test handling of race conditions during directory creation."""
        mock_exists.return_value = False
        mock_makedirs.side_effect = FileExistsError("Directory exists")
        
        validator = ConfigurationValidator()
        
        # Should handle race condition gracefully
        result = validator.validate_database_path("./race_condition_db")
        
        assert result is True
    
    def test_configuration_validation_memory_constraints(self):
        """Test configuration validation under memory constraints."""
        # This test would simulate low memory conditions
        # In a real implementation, this might test fallback behaviors
        config = CBRServerConfig(
            database_path="./memory_test_db",
            max_results_default=100000  # Large value that might cause memory issues
        )
        
        assert config.max_results_default == 100000
    
    def test_concurrent_validation_requests(self):
        """Test configuration validation with concurrent validation requests."""
        import threading
        import time
        
        results = []
        errors = []
        
        def validate_config():
            try:
                config = CBRServerConfig(
                    database_path="./concurrent_db",
                    collection_name="concurrent_collection"
                )
                validator = ConfigurationValidator()
                with patch('os.path.exists', return_value=True):
                    with patch('os.access', return_value=True):
                        result = validator.validate_database_path(config.database_path)
                        results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Start multiple validation threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=validate_config)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All validations should succeed without race conditions
        assert len(results) == 10
        assert all(result is True for result in results)
        assert len(errors) == 0


