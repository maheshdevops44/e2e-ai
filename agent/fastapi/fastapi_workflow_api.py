#!/usr/bin/env python3
"""
FastAPI Workflow API using LangGraph Checkpointing
Single endpoint for all workflow operations
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import sys
import json
from datetime import datetime

# Add the parent directory to the path to import workflow modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import workflow modules
from models.messages import format_state_to_ai_output
from models.state import GraphState
from workflow.builder import build_workflow

app = FastAPI(title="QA Workflow API with LangGraph Integration", version="3.0.0")

# Build the workflow once at startup
print("🔄 Building LangGraph workflow...")
workflow = build_workflow()
print("✅ LangGraph workflow built successfully")

class WorkflowRequest(BaseModel):
    """Enhanced request model for workflow operations"""
    input: Optional[str] = None
    run_id: Optional[str] = None
    human_input: Optional[Dict[str, Any]] = None

class WorkflowResponse(BaseModel):
    """Enhanced response model for workflow operations"""
    role: str
    message: str
    metadata: Dict[str, Any]
    run_id: str
    workflow_status: str
    awaiting_human_input: bool
    markdown: Optional[str] = None
    steps_markdown: Optional[str] = None
    gherkin_steps_markdown: Optional[str] = None
    test_case_markdown: Optional[str] = None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "langgraph_workflow": "built",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/opensearch-health")
async def opensearch_health_check():
    """Opensearch health check endpoint"""
    from config.llm_config import opensearch_client
    return {
        "status": "healthy",
        "opensearch_client": opensearch_client.as_retriever(search_kwargs={"k": 1}).get_relevant_documents("sop test")
    }

@app.post("/workflow")
async def workflow_handler(request: WorkflowRequest):
    print("Received request:", request.dict())
    
    try:
        # Generate run_id if not provided
        if not request.run_id:
            run_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        else:
            run_id = request.run_id
            
        print(f"🔄 Processing workflow with run_id: {run_id}")
        
        # Initialize state based on request type
        if request.input and not request.run_id:
            # New workflow - start with user story parsing
            print("🔄 Starting new workflow with user story parsing")
            initial_state = GraphState({
                "RunID": run_id,
                "input": request.input,
                "user_story": request.input,
                "parsed_story": {},
                "missing_fields": [],
                "updated_info": {},
                "steps": [],
                "validated": False,
                "updated_steps": [],
                "gherkins_scenario": "",
                "message": "",
                "messages": [],
                "llm_suggestion": "",
                "llm_feedback": "",
                "accept": False,
                "edited_fields": {},
                "sop_context": [],
                "workflow_status": "Starting",
                "Test_case": "",
                "last": {},
                "awaiting_human_input": False,
                "human_input": {},
                "validation_step": "",
                "playwright_code": ""
            })
            
            # Start the workflow from the beginning
            config = {"configurable": {"thread_id": run_id}}
            result = workflow.invoke(initial_state, config)
            
        elif request.input and request.run_id:
            # Resume workflow with human input
            print(f"🔄 Resuming workflow {request.run_id} with human input")
            
            # Create state with human input for resuming
            # Note: We only provide the human_input, the rest will be loaded from checkpoint
            resume_state = GraphState({
                "RunID": request.run_id,
                "human_input": {"feedback": request.input},
                "awaiting_human_input": False,
                "workflow_status": "Resuming with human input"
            })
            
            # Resume the workflow from checkpoint
            config = {"configurable": {"thread_id": request.run_id}}
            result = workflow.invoke(resume_state, config)
            print("++++++++++++++++++",config)
            print("++++++++++++++++++",resume_state)
            # result = None
            # for chunk in workflow.stream(resume_state, config):
            #     result = chunk
            #     print(chunk)
            
            # result = result or workflow.get_state(config).values
        
        else:
            raise HTTPException(
                status_code=400, 
                detail="Invalid request. Provide 'input' (user story) for new workflows or 'input' + 'run_id' for resuming workflows"
            )
        
        print(f"✅ Workflow execution completed")
        print(f"  Final status: {result.get('workflow_status', 'unknown')}")
        print(f"  Awaiting human input: {result.get('awaiting_human_input', False)}")
        
        # Format the response based on workflow state
        if result.get("awaiting_human_input", False):
            # Workflow is awaiting human input - show parsed story for validation
            parsed_story = result.get("parsed_story", {})
            
            # Create formatted message for human validation
            message_parts = []
            message_parts.append("## Parsed User Story")
            
            if parsed_story:
                if 'Objective' in parsed_story and parsed_story['Objective']:
                    message_parts.append(f"**Objective:** {parsed_story['Objective']}")
                if 'Test Summary' in parsed_story and parsed_story['Test Summary']:
                    message_parts.append(f"**Test Summary:** {parsed_story['Test Summary']}")
                if 'Acceptance Criteria' in parsed_story and parsed_story['Acceptance Criteria']:
                    message_parts.append("**Acceptance Criteria:**")
                    for i, crit in enumerate(parsed_story['Acceptance Criteria'], 1):
                        message_parts.append(f"{i}. {crit}")
                if 'Applications Involved' in parsed_story and parsed_story['Applications Involved']:
                    message_parts.append(f"**Applications Involved:** {', '.join(parsed_story['Applications Involved'])}")
                if 'Manual_Steps' in parsed_story and parsed_story['Manual_Steps']:
                    message_parts.append("**Manual Steps:**")
                    for i, step in enumerate(parsed_story['Manual_Steps'], 1):
                        message_parts.append(f"{i}. {step}")
                if 'Test_Automation' in parsed_story and parsed_story['Test_Automation']:
                    message_parts.append("**Test Automation Steps:**")
                    for i, step in enumerate(parsed_story['Test_Automation'], 1):
                        message_parts.append(f"{i}. {step}")
            
            # Add missing fields if any
            missing_fields = result.get("missing_fields", [])
            if missing_fields:
                message_parts.append("")
                message_parts.append("## Missing Fields")
                message_parts.append(f"The following fields are missing: {', '.join(missing_fields)}")
            
            # Add feedback prompt
            message_parts.append("")
            message_parts.append("**Please review the parsed user story above and provide feedback.**")
            message_parts.append("**Type 'approve' to proceed or provide specific feedback.**")
            
            message_md = "\n".join(message_parts)
            
            return {
                "role": "ai",
                "message": parsed_story,
                "metadata": {
                    "run_id": result.get("RunID", run_id),
                }
            }
            
        else:
            # Workflow completed - return final results
            test_case = result.get("Test_case", "")
            gherkin_scenario = result.get("gherkins_scenario", "")
            playwright_script = result.get("playwright_code", "")
            steps = result.get("steps", [])
            
            print(f"✅ Workflow completed successfully")
            print(f"  Test case generated: {bool(test_case)}")
            print(f"  Gherkin scenario generated: {bool(gherkin_scenario)}")
            print(f"  Playwright script generated: {bool(playwright_script)}")
            print(f"  Steps generated: {len(steps)}")
            
            # Generate markdown report if test artifacts exist
            markdown_content = ""
            try:
                if test_case or gherkin_scenario or playwright_script:
                    # Create a simple markdown report since the generator doesn't exist
                    markdown_content = f"""# Test Generation Report

## Run ID: {run_id}

## Test Case
{test_case if test_case else "No test case generated"}

## Gherkin Scenario
```gherkin
{gherkin_scenario if gherkin_scenario else "No Gherkin scenario generated"}
```

## Playwright Script
```python
{playwright_script if playwright_script else "No Playwright script generated"}
```

## Steps
{chr(10).join([f"{i+1}. {step}" for i, step in enumerate(steps)]) if steps else "No steps generated"}

## Applications Covered
{', '.join(result.get("parsed_story", {}).get("Applications Involved", []))}

Generated on: {datetime.now().isoformat()}
"""
                    print(f"📄 Simple markdown report generated")
                        
            except Exception as e:
                print(f"⚠️ Error generating markdown report: {e}")
                markdown_content = f"Error generating markdown report: {str(e)}"
            
            return {
                "role": "ai",
                "message": "Test Generation Completed Successfully",
                "metadata": {
                    "run_id": result.get("RunID", run_id),
                    "test_case": test_case,
                    "test_script": playwright_script
                    }
            }

    except Exception as e:
        print(f"❌ Exception in workflow_handler: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Workflow error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, timeout_keep_alive=200000)