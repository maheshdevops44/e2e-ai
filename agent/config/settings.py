"""
Configuration settings for the workflow application
"""

import os
import dotenv
from typing import Optional

# Load environment variables
dotenv.load_dotenv()

# Environment Variables for Playwright Automation Script

class Settings:
    """Application settings"""
    
    #OpenAI/Azure Configuration
    OPENAI_API_TYPE: str = os.getenv("OPENAI_API_TYPE")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    AZURE_DEPLOYMENT: str = os.getenv("AZURE_DEPLOYMENT")
    API_VERSION: str = os.getenv("API_VERSION")

    # SSL Configuration - Use certifi's default certificate or None
    @property
    def SSL_CERT_FILE(self) -> Optional[str]:
        try:
            import certifi
            return certifi.where()
        except ImportError:
            return None
    
    # # OpenSearch Configuration
    OPENSEARCH_URL: str = os.getenv("OPENSEARCH_URL")
    OPENSEARCH_INDEX: str = os.getenv("OPENSEARCH_INDEX")
    OPENSEARCH_USERNAME: str = os.getenv("OPENSEARCH_USERNAME")
    OPENSEARCH_PASSWORD: str = os.getenv("OPENSEARCH_PASSWORD")


    # Embeddings Configuration
    EMBEDDINGS_MODEL: str = "ai-coe-embeddings-3-small"
    EMBEDDINGS_TIMEOUT: int = 4000
    EMBEDDINGS_CHUNK_SIZE: int = 8000
    EMBEDDINGS_MAX_RETRIES: int = 5
    EMBEDDINGS_RETRY_MIN_SECONDS: int = 60
    EMBEDDINGS_RETRY_MAX_SECONDS: int = 120
    
    # API Configuration
    API_HOST: str = "localhost"
    API_PORT: int = 5000
    API_DEBUG: bool = True
    
    @classmethod
    def setup_environment(cls):
        """Setup environment variables"""
        os.environ["OPENAI_API_TYPE"] = cls.OPENAI_API_TYPE
        os.environ["AZURE_OPENAI_ENDPOINT"] = cls.AZURE_OPENAI_ENDPOINT
        os.environ["OPENAI_API_KEY"] = cls.OPENAI_API_KEY
        
        # Only set SSL_CERT_FILE if it exists
        ssl_cert_file = cls().SSL_CERT_FILE
        if ssl_cert_file and os.path.exists(ssl_cert_file):
            os.environ["SSL_CERT_FILE"] = ssl_cert_file
        else:
            # Remove SSL_CERT_FILE from environment if it doesn't exist
            os.environ.pop("SSL_CERT_FILE", None)

# Initialize settings
settings = Settings()
settings.setup_environment() 