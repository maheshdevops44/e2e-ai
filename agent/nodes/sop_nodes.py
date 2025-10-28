"""
SOP (Standard Operating Procedure) related nodes
"""

import json
from datetime import datetime
from typing import Dict, Any
from config.llm_config import llm, opensearch_client
from models.state import GraphState
from models.messages import add_message_to_state, add_workflow_step

def fetch_sop_agent(state: GraphState) -> GraphState:
    """Fetch relevant SOP documents"""
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    import os
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    # Suppress tqdm progress bars
    import sys
    class DummyFile(object):
        def write(self, x): pass
        def flush(self): pass
    sys.stderr = DummyFile()
    print("\n### 🔄 Running node: FETCH SOP\n")
    
    # Add workflow step
    state = add_workflow_step(state, "fetch_sop", "in_progress")
    
    user_story = state.get("user_story", {})

    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",user_story)
    
    # Fix: Ensure query is always a string, not a list
    if isinstance(user_story, dict):
        # Try multiple fields to get a meaningful query
        # query = (user_story.get("Test Summary") or 
        #         user_story.get("Objective") or 
        #         user_story.get("Test_Automation") or
        #         user_story.get("Description") or
        #         str(user_story))
        query = (str(user_story))
    else:
        query = str(user_story)
    
    # Ensure query is a string, not a list
    if isinstance(query, list):
        query = " ".join(query)
    elif not isinstance(query, str):
        query = str(query)
    
    # Clean and improve the query
    query = query.strip()
    if len(query) < 10:  # If query is too short, add some context
        query = f"clearance eligibility testing {query}"
    
    print(f"🔍 SOP Query: {query[:200]}...")
    
    try:
        # Get retriever from opensearch client
        print(f"🔍 Attempting to retrieve SOP documents for query: {query[:100]}...")
        print(f"🔍 OpenSearch client type: {type(opensearch_client)}")
        
        retriever = opensearch_client.as_retriever(search_kwargs={"k": 1})  # Retrieve only 1 document
        print(f"🔍 Retriever type: {type(retriever)}")
        
        sop_context = retriever.get_relevant_documents(query, k=1)
        print(f"📄 Found {len(sop_context)} SOP documents")
        
        if sop_context:
            print(f"📄 First document type: {type(sop_context[0])}")
            print(f"📄 First document content preview: {sop_context[0].page_content[:200]}...")
        else:
            print("⚠️ No documents returned from retriever")
        
        if not sop_context:
            print("⚠️ No SOP documents found, using empty context")
            sop_context_str = "[]"
            workflow_status = "No SOP Found"
            state = add_workflow_step(state, "fetch_sop", "completed", "No SOP documents found, proceeding without SOP context")
        else:
            # Enhanced document processing with better metadata handling
            processed_docs = []
            for i, doc in enumerate(sop_context):
                # Extract scenario from various possible metadata fields (including misspelled 'sceanrio')
                scenario = (doc.metadata.get("scenario") or 
                           doc.metadata.get("sceanrio") or  # Handle misspelled field
                           doc.metadata.get("title") or 
                           doc.metadata.get("document_title") or
                           doc.metadata.get("file_name") or
                           f"Document {i+1}")
                
                # Extract additional metadata
                metadata_info = {
                    "scenario": scenario,
                    "steps": doc.page_content,
                    "score": getattr(doc, 'metadata', {}).get('score', 'N/A'),
                    "source": doc.metadata.get("source", "Unknown"),
                    "file_name": doc.metadata.get("file_name", "Unknown"),
                    "document_type": doc.metadata.get("document_type", "Unknown"),
                    "all_metadata": doc.metadata  # Include all metadata for debugging
                }
                
                processed_docs.append(metadata_info)
                
                # Debug output for each document
                print(f"📋 Document {i+1} Metadata:")
                print(f"  Scenario: {scenario}")
                print(f"  Source: {metadata_info['source']}")
                print(f"  File Name: {metadata_info['file_name']}")
                print(f"  Document Type: {metadata_info['document_type']}")
                print(f"  Content Length: {len(doc.page_content)} characters")
                #print(f"  Content Preview: {doc.page_content[:200]}...")
            
            sop_context_str = json.dumps(processed_docs, indent=1)
            
            workflow_status = "Retrieving SOP"
            state = add_workflow_step(state, "fetch_sop", "completed", f"SOP documents retrieved successfully ({len(sop_context)} found)")
        
        # Add message to state
        state = add_message_to_state(
            state, 
            "system", 
            f"SOP documents retrieved for query: {query[:100]}...",
            {"node": "fetch_sop", "query": query, "documents_found": len(sop_context)}
        )
        
    except Exception as e:
        print("EXCEPTION TYPE:", type(e))
        print(f"Error fetching SOP: {str(e)}")
        print(f"Error details: {e.__class__.__name__}: {str(e)}")
        
        # Check if it's a connection issue
        if "connection" in str(e).lower() or "timeout" in str(e).lower():
            print("🔌 Connection issue detected - check OpenSearch URL and credentials")
        elif "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
            print("🔐 Authentication issue detected - check OpenSearch credentials")
        elif "index" in str(e).lower():
            print("📚 Index issue detected - check if the index exists")
        
        sop_context_str = "[]"
        workflow_status = "Error Retrieving SOP"
        state = add_workflow_step(state, "fetch_sop", "failed", error=f"Error: {str(e)}")
        
        # Add error message to state
        state = add_message_to_state(
            state, 
            "system", 
            f"Error retrieving SOP documents: {str(e)}",
            {"node": "fetch_sop", "error": str(e)}
        )
    
    # Ensure sop_context is always a list
    if not isinstance(sop_context_str, str):
        sop_context_str = str(sop_context_str)
    
    print(f"📋 SOP Context length: {len(sop_context_str)} characters")
    #print(f"📋 SOP Context preview: {sop_context_str[:200]}...")
    
    # Additional debugging - show the actual content being returned
    print(f"🔍 DEBUG: Final SOP context being returned:")
    print(f"  Type: {type(sop_context_str)}")
    #print(f"  Content: {sop_context_str}")
    print(f"  Is empty: {sop_context_str == '[]' or sop_context_str == ''}")
    
    return {**state, "sop_context": [sop_context_str], "sop_query": query, "workflow_status": workflow_status} 