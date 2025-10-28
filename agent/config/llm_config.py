"""
LLM and embeddings configuration
"""

import httpx
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain.tools.retriever import create_retriever_tool
from .settings import settings

from dotenv import load_dotenv
import os
from pathlib import Path

dotenv_path = Path(__file__).resolve().parent / ".env"

print(f"🔍 Loading .env file from: {dotenv_path}")
print(f"🔍 .env file exists: {dotenv_path.exists()}")

load_dotenv(dotenv_path)

# # Debug environment variables
# print(f"🔍 Environment variables after loading:")
# print(f"  OPENSEARCH_URL: {os.getenv('OPENSEARCH_URL', 'NOT_SET')}")
# print(f"  OPENSEARCH_INDEX: {os.getenv('OPENSEARCH_INDEX', 'NOT_SET')}")
# print(f"  OPENSEARCH_USERNAME: {os.getenv('OPENSEARCH_USERNAME', 'NOT_SET')}")
# print(f"  OPENSEARCH_PASSWORD: {os.getenv('OPENSEARCH_PASSWORD', 'NOT_SET')}")


# Add rate limiting configuration
RATE_LIMIT_RETRIES = 3
RATE_LIMIT_DELAY = 30  # seconds
RATE_LIMIT_BACKOFF = 2  # exponential backoff multiplier

def create_llm():
    """Create simple LLM function"""
    from openai import AzureOpenAI
    import httpx
    
    try:
        print(f"🔧 Creating Azure OpenAI client...")
        print(f"  Endpoint: {settings.AZURE_OPENAI_ENDPOINT}")
        print(f"  API Version: {settings.API_VERSION}")
        print(f"  Deployment: {settings.AZURE_DEPLOYMENT}")
        
        # Create client with SSL verification disabled for internal endpoints
        http_timeout = httpx.Timeout(connect=30.0, read=300.0, write=120.0, pool=60.0)
        client = AzureOpenAI(
            api_key=settings.OPENAI_API_KEY,
            api_version=settings.API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            http_client=httpx.Client(verify=False, timeout=http_timeout)  # Disable SSL verification and set timeout
        )
        
        print(f"✅ Azure OpenAI client created successfully")
        
    except Exception as e:
        print(f"❌ Failed to create Azure OpenAI client: {e}")
        raise e
    
    def llm_simple(prompt):
        """Simple LLM call without retry logic"""
        try:
            print(f"🔄 Making LLM call...")
            
            # chunks = []
            # with client.chat.completions.stream(
            #     model=settings.AZURE_DEPLOYMENT,
            #     messages=[{"role": "user", "content": prompt}],
            #     temperature=0.0,
            #     max_tokens=8000,
            # ) as stream:
            #     print(stream)
            #     for event in stream:
            #         print(stream)
            #         if event.type == "message.delta" and event.delta and event.delta.content:
            #             chunks.append(event.delta.content)
            #         elif event.type == "error":
            #             raise RuntimeError(event.error)
            #         elif event.type == "message.completed":
            #             break

            # result = "".join(chunks)
            # print("✅ LLM call successful")
            # return result
            # updated to included streaming -- 09152025
            response = client.chat.completions.create(
                model=settings.AZURE_DEPLOYMENT,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=8000
            )
            print(f"✅ LLM call successful")
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ LLM call failed: {e}")
            raise e
    
    return llm_simple

def create_embeddings() -> AzureOpenAIEmbeddings:
    """Create and configure the embeddings instance"""
    try:
        return AzureOpenAIEmbeddings(
            model=settings.EMBEDDINGS_MODEL,
            api_version=settings.API_VERSION,
            http_client=httpx.Client(verify=False),
            timeout=settings.EMBEDDINGS_TIMEOUT,
            chunk_size=settings.EMBEDDINGS_CHUNK_SIZE,
            max_retries=settings.EMBEDDINGS_MAX_RETRIES,
            retry_min_seconds=settings.EMBEDDINGS_RETRY_MIN_SECONDS,
            retry_max_seconds=settings.EMBEDDINGS_RETRY_MAX_SECONDS,
            show_progress_bar=True
        )
    except Exception as e:
        print(f"Warning: Failed to create embeddings with SSL verification disabled: {e}")
        # Try without http_client specification
        return AzureOpenAIEmbeddings(
            model=settings.EMBEDDINGS_MODEL,
            api_version=settings.API_VERSION,
            timeout=settings.EMBEDDINGS_TIMEOUT,
            chunk_size=settings.EMBEDDINGS_CHUNK_SIZE,
            max_retries=settings.EMBEDDINGS_MAX_RETRIES,
            retry_min_seconds=settings.EMBEDDINGS_RETRY_MIN_SECONDS,
            retry_max_seconds=settings.EMBEDDINGS_RETRY_MAX_SECONDS,
            show_progress_bar=True
        )

def create_opensearch_client():
    """Create and configure the OpenSearch client"""
    try:
        print(f"🔧 Creating OpenSearch client...")
        print(f"  URL: {settings.OPENSEARCH_URL}")
        print(f"  Index: {settings.OPENSEARCH_INDEX}")
        # print(f"  Username: {settings.OPENSEARCH_USERNAME}")
        # print(f"  Password: {'*' * len(settings.OPENSEARCH_PASSWORD) if settings.OPENSEARCH_PASSWORD else 'None'}")
        
        # Check if environment variables are loaded
        if not settings.OPENSEARCH_URL:
            raise ValueError("OPENSEARCH_URL not found in environment variables")
        if not settings.OPENSEARCH_INDEX:
            raise ValueError("OPENSEARCH_INDEX not found in environment variables")
        if not settings.OPENSEARCH_USERNAME:
            raise ValueError("OPENSEARCH_USERNAME not found in environment variables")
        if not settings.OPENSEARCH_PASSWORD:
            raise ValueError("OPENSEARCH_PASSWORD not found in environment variables")
        
        embeddings = create_embeddings()
        
        client = OpenSearchVectorSearch(
            opensearch_url=settings.OPENSEARCH_URL,
            index_name=settings.OPENSEARCH_INDEX,
            embedding_function=embeddings,
            engine="faiss",
            http_auth=(settings.OPENSEARCH_USERNAME, settings.OPENSEARCH_PASSWORD)
        )
        
        print(f"✅ OpenSearch client created successfully")
        return client
        
    except Exception as e:
        print(f"❌ Failed to create OpenSearch client: {e}")
        print(f"  Error type: {type(e).__name__}")
        print(f"  Error details: {str(e)}")
        
        # Return a mock client that returns empty results
        class MockOpenSearchClient:
            def as_retriever(self, **kwargs):
                class MockRetriever:
                    def get_relevant_documents(self, query, k=1):
                        print(f"⚠️ Using mock retriever - no documents found")
                        return []
                return MockRetriever()
        return MockOpenSearchClient()

def create_sop_retriever_tool():
    """Create the retriever tool"""
    opensearch_client = create_opensearch_client()
    retriever = opensearch_client.as_retriever(search_kwargs={"k": 1})
    print(retriever)
    return create_retriever_tool(
        retriever=retriever,
        name="retrieve_SOP",
        description="Read the given user story and then try to retrieve the SOP that would be relevant for generating detailed steps for running the test scenario in the user story. Search and return information or relevant steps from the SOP documents.",
    )

# Global instances with error handling
try:
    llm = create_llm()
    embeddings = create_embeddings()
    opensearch_client = create_opensearch_client()
    retriever_tool = create_sop_retriever_tool()
except Exception as e:
    print(f"Error initializing global instances: {e}")
    # Create fallback instances
    llm = None
    embeddings = None
    opensearch_client = None
    retriever_tool = None 