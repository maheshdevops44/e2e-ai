from langchain_openai import AzureOpenAIEmbeddings
import httpx
import os

import httpx

def get_azure_embeddings(model_name: str, api_version: str = '2023-05-15', **kwargs):
    return AzureOpenAIEmbeddings(
            model=model_name,
            # azure_deployment=model_name,
            api_version=api_version,
            http_client= httpx.Client(verify = False),
            timeout = 4000,
            chunk_size=8000,
            max_retries=5,                  # <--- This is the main control
            retry_min_seconds=60,
            retry_max_seconds=120,
            show_progress_bar=True,
            **kwargs
        )