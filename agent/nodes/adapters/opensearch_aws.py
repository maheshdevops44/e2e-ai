import boto3
from opensearchpy import RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.embeddings import Embeddings
import os
import dotenv
dotenv.load_dotenv()

def get_aws_open_search(index_name : str , embeddings : Embeddings):
    return OpenSearchVectorSearch(
        opensearch_url= os.getenv("OPENSEARCH_URL"),
        index_name=index_name,
        embedding_function= embeddings,
        engine = "faiss",
        http_auth = (os.getenv("OPENSEARCH_USERNAME"), os.getenv("OPENSEARCH_PASS"))
    )

if __name__ ==  "__main__":
    from langchain_core.documents import Document
    from uuid import uuid4
    from nodes.adapters.embedding_adapters import get_azure_embeddings

    embeddings = get_azure_embeddings("ai-coe-embeddings-3-small")
    vector_store = get_aws_open_search("intake_index_version_2", embeddings)

    print(vector_store.similarity_search("Intake Index", k=1))