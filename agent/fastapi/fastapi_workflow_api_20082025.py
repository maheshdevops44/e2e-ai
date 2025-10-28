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

# Add the parent directory to the path to import workflow modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import workflow modules
from models.messages import format_state_to_ai_output
#from markdown_report_generator import save_markdown_report
from nodes.parsing_nodes import parse_user_story_llm

# SOP-based generation is now built into the main workflow
SOP_GENERATION_AVAILABLE = True
print("✅ SOP-based generation built into main workflow")

app = FastAPI(title="QA Workflow API with SOP Generation", version="2.0.0")

class WorkflowRequest(BaseModel):
    """Enhanced request model for workflow operations with SOP support"""
    input: Optional[str] = None
    run_id: Optional[str] = None
    human_input: Optional[Dict[str, Any]] = None
    use_sop_generation: Optional[bool] = True  # Default to SOP generation
    sop_context: Optional[list] = None  # Optional SOP context

class WorkflowResponse(BaseModel):
    """Enhanced response model for workflow operations"""
    role: str
    message: str
    metadata: Dict[str, Any]
    run_id: str
    workflow_status: str
    awaiting_human_input: bool
    markdown: Optional[str] = None  # Add markdown field
    steps_markdown: Optional[str] = None
    gherkin_steps_markdown: Optional[str] = None
    test_case_markdown: Optional[str] = None
    sop_generation_used: Optional[bool] = False
    applications_covered: Optional[list] = None

def custom_json_serializer(obj):
    # Try to convert LangChain message objects to dict
    if hasattr(obj, 'dict'):
        return obj.dict()
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return str(obj)  # Fallback to string

def convert_to_pytest(script_content: str):
    """Convert Playwright script to pytest format"""
    # Add pytest imports and decorators
    pytest_header = '''import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import time
import traceback
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Configuration from environment variables
USERNAME = os.getenv('USERNAME', 'C9G5JS')
PASSWORD = os.getenv('PASSWORD', 'Emphatic-Award1-Tinker')
PATIENT_ID = os.getenv('PATIENT_ID', '17045254')
COMMON_INTAKE_ID = os.getenv('COMMON_INTAKE_ID', '17045254')
DRUG_NDC = os.getenv('DRUG_NDC', '00074055402')
TDM_TOOL_URL = os.getenv('TDM_TOOL_URL', 'https://tdm-tool-qa.express-scripts.com/')
INTAKE_URL = os.getenv('INTAKE_URL', 'https://spcia-qa.express-scripts.com/spcia')
CLEARANCE_URL = os.getenv('CLEARANCE_URL', 'https://clearance-qa.express-scripts.com/spclr')
RXP_URL = os.getenv('RXP_URL', 'https://sprxp-qa.express-scripts.com/sprxp/')
CRM_URL = os.getenv('CRM_URL', 'https://spcrmqa-internal.express-scripts.com/spcrm88/')

def delay():
    time.sleep(5)

def handle_error(page, step, e):
    print(f"[ERROR] Step: {step} - {e}")
    screenshot(page, f"error_{step}")
    traceback.print_exc()
    pytest.fail(f"Test failed at step {step}: {e}")

def login(page, url, step_prefix):
    try:
        page.goto(url, timeout=60000)
        delay()
        screenshot(page, f"{step_prefix}_login_page")
        page.fill("#txtUserID", USERNAME)
        page.fill("#txtPassword", PASSWORD)
        screenshot(page, f"{step_prefix}_credentials_filled")
        page.click("#sub")
        delay()
        screenshot(page, f"{step_prefix}_after_login")
    except Exception as e:
        handle_error(page, f"{step_prefix}_login", e)

'''
    
    # Replace main() function with pytest test function
    script_content = script_content.replace('def main():', '@pytest.mark.slow\ndef test_workflow():')
    
    # Remove the main() call at the end if it exists
    script_content = script_content.replace('if __name__ == "__main__":\n    main()', '')
    
    # Combine header with modified script
    pytest_script = pytest_header + script_content
    
    return pytest_script


def run_sop_based_workflow(user_story: str, sop_context: Optional[list] = None):
    """
    Run SOP-based workflow for comprehensive test generation with human validation
    
    Args:
        user_story (str): The user story to process
        sop_context (list): Optional SOP context to use
    
    Returns:
        dict: Workflow result with parsed story for human validation
    """
    print(f"🔄 Running SOP-based workflow...")
    print(f"  User story length: {len(user_story)} characters")
    print(f"  SOP context provided: {sop_context is not None}")
    
    try:
        from datetime import datetime
        run_id = f"sop_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        # Use the LLM-based parser node (pure parsing without SOP context)
        state = {"user_story": user_story}
        parsed_result = parse_user_story_llm(state)
        parsed_story = parsed_result.get("parsed_story", {})
        
        # Use fetch_sop_agent to retrieve SOP context from OpenSearch index
        print("🔄 Retrieving SOP context from OpenSearch index...")
        try:
            from nodes.sop_nodes import fetch_sop_agent
            from models.state import GraphState
            
            # Create state with parsed story for SOP retrieval
            sop_state = GraphState({
                "parsed_story": parsed_story,
                "user_story": user_story
            })
            
            # Use fetch_sop_agent to get SOP context from index
            sop_result = fetch_sop_agent(sop_state)
            sop_context = sop_result.get("sop_context", [])
            sop_query = sop_result.get("sop_query", "")
            
            print(f"✅ Retrieved SOP context from OpenSearch index")
            print(f"🔍 SOP Query used: {sop_query[:100]}...")
            print(f"📄 SOP Context retrieved: {len(sop_context)} items")
            
            if sop_context and len(sop_context) > 0:
                print("🔍 SOP Context Details:")
                for i, context_item in enumerate(sop_context):
                    if isinstance(context_item, str):
                        try:
                            import json
                            parsed_context = json.loads(context_item)
                            print(f"  Item {i+1}: {len(parsed_context)} documents")
                        except:
                            print(f"  Item {i+1}: {len(context_item)} characters")
                    else:
                        print(f"  Item {i+1}: {type(context_item)}")
            else:
                print("⚠️ No SOP context retrieved from index")
                sop_context = []
            
        except Exception as e:
            print(f"❌ Error retrieving SOP context from index: {e}")
            print("🔄 Falling back to empty SOP context")
            sop_context = []
        # Ensure parsed story has basic required fields for proper display (no SOP-specific content)
        if not parsed_story.get("Applications_Involved"):
            parsed_story["Applications_Involved"] = []
        if not parsed_story.get("Objective"):
            parsed_story["Objective"] = ""
        if not parsed_story.get("Test_Summary"):
            parsed_story["Test_Summary"] = []
        if not parsed_story.get("Acceptance_Criteria"):
            parsed_story["Acceptance_Criteria"] = []
        
        workflow_result = {
            "RunID": run_id,
            "parsed_story": parsed_story,
            "input": user_story,
            "user_story": user_story,
            "steps": None,  # Will be generated after human approval
            "Test_case": None,  # Will be generated after human approval
            "gherkins_scenario": None,  # Will be generated after human approval
            "workflow_status": "Parsed Story - Awaiting Human Validation",
            "awaiting_human_input": True,  # Require human validation before test generation
            "sop_generation_used": True,
            "applications_covered": parsed_story.get("Applications_Involved", []),
            "sop_context": sop_context  # Store SOP context for later use
        }
        print(f"✅ SOP-based story parsing completed (LLM)")
        print(f"  Applications identified: {workflow_result.get('applications_covered', [])}")
        print(f"  Awaiting human input: {workflow_result.get('awaiting_human_input')}")
        print(f"  Run ID: {workflow_result.get('RunID')}")
        return workflow_result
    except Exception as e:
        print(f"❌ SOP-based workflow failed: {e}")
        raise e

def run_sop_test_generation(user_story: str, sop_context: Optional[list] = None):
    """
    Generate test artifacts after human approval using SOP context with application-level test cases
    
    Args:
        user_story (str): The user story to process
        sop_context (list): Optional SOP context to use
    
    Returns:
        dict: Workflow result with generated test artifacts
    """
    print(f"🔄 Generating SOP-based test artifacts with application-level test cases...")
    print(f"  User story length: {len(user_story)} characters")
    print(f"  SOP context provided: {sop_context is not None}")
    
    try:
        # Import the generation nodes for proper step and test case generation
        from nodes.generation_nodes import generate_steps_llm, generate_test_case, convert_to_gherkin_llm, generate_playwright_code
        from models.state import GraphState
        
        # Create initial state with user story
        state = GraphState({
            "user_story": user_story,
            "parsed_story": {
                "Applications_Involved": ["Intake", "Clearance", "RxP Order Entry", "RxP Data Verification", "CRM", "Trend Processing"],
                "Objective": "End-to-end test generation for Direct Patient Fax Referral with Humira therapy using SOP context",
                "Test_Summary": [
                    "Will generate comprehensive test artifacts covering all applications",
                    "Will use SOP context for accurate and relevant test generation",
                    "Will ensure complete workflow coverage from intake to order scheduling"
                ],
                "Acceptance_Criteria": [
                    "All applications in the workflow are covered",
                    "Test steps are accurate and follow SOP procedures",
                    "Gherkin scenarios are comprehensive and clear"
                ]
            }
        })
        
        # Use fetch_sop_agent to retrieve SOP context from OpenSearch index
        print("🔄 Step 0: Retrieving SOP context from OpenSearch index...")
        try:
            from nodes.sop_nodes import fetch_sop_agent
            
            # Create state with user story for SOP retrieval
            sop_state = GraphState({
                "user_story": user_story,
                "parsed_story": {
                    "Objective": "End-to-end test generation for Direct Patient Fax Referral with Humira therapy using SOP context",
                    "Test_Summary": [
                        "Will generate comprehensive test artifacts covering all applications",
                        "Will use SOP context for accurate and relevant test generation",
                        "Will ensure complete workflow coverage from intake to order scheduling"
                    ]
                }
            })
            
            # Use fetch_sop_agent to get SOP context from index
            sop_result = fetch_sop_agent(sop_state)
            sop_context = sop_result.get("sop_context", [])
            sop_query = sop_result.get("sop_query", "")
            
            print(f"✅ Retrieved SOP context from OpenSearch index")
            print(f"🔍 SOP Query used: {sop_query[:100]}...")
            print(f"📄 SOP Context retrieved: {len(sop_context)} items")
            
            if sop_context and len(sop_context) > 0:
                print("🔍 SOP Context Details:")
                for i, context_item in enumerate(sop_context):
                    if isinstance(context_item, str):
                        try:
                            import json
                            parsed_context = json.loads(context_item)
                            print(f"  Item {i+1}: {len(parsed_context)} documents")
                        except:
                            print(f"  Item {i+1}: {len(context_item)} characters")
                    else:
                        print(f"  Item {i+1}: {type(context_item)}")
            else:
                print("⚠️ No SOP context retrieved from index")
                sop_context = []
            
        except Exception as e:
            print(f"❌ Error retrieving SOP context from index: {e}")
            print("🔄 Falling back to empty SOP context")
            sop_context = []
        state["sop_context"] = sop_context
        
        # Ensure we have meaningful SOP context
        if not sop_context or len(sop_context) == 0:
            print("⚠️ No SOP context available - generating basic test cases from user story only")
            # Create basic test cases based only on user story
            basic_test_cases = [{
                "Description": "Basic test based on user story",
                "Prerequisite": "Basic setup",
                "Application": "General",
                "Test Steps": ["Execute basic workflow based on user story"],
                "Expected Result": "Basic workflow completed"
            }]
            
            return {
                "steps": ["Execute basic workflow based on user story"],
                "Test_case": basic_test_cases,
                "gherkins_scenario": "Feature: Basic Workflow\n\nScenario: Execute basic workflow\n  Given the basic setup\n  When executing the workflow\n  Then the workflow completes",
                "workflow_status": "Basic Test Generation Complete (No SOP Context)",
                "awaiting_human_input": False,
                "applications_covered": ["General"],
                "sop_generation_used": False,
                "sop_context": []
            }
        
        # Step 1: Generate detailed steps using the generation node
        print("🔄 Step 1: Generating detailed automation steps...")
        state = generate_steps_llm(state)
        steps = state.get("steps", [])
        print(f"✅ Generated {len(steps)} automation steps")
        
        # Step 2: Generate application-level test cases (uses steps as input)
        print("🔄 Step 2: Generating application-level test cases...")
        state = generate_test_case(state)
        test_cases = state.get("Test_case", [])
        print(f"✅ Generated test cases")
        
        # Step 3: Generate Gherkin scenarios
        print("🔄 Step 3: Generating Gherkin scenarios...")
        state = convert_to_gherkin_llm(state)
        gherkin_scenarios = state.get("gherkins_scenario", "")
        print(f"✅ Generated Gherkin scenarios")
        
        # Step 4: Generate Playwright script from steps
        print("🔄 Step 4: Generating Playwright script from steps...")
        state = generate_playwright_code(state)
        playwright_script = state.get("playwright_code", "")
        print(f"✅ Generated Playwright script")
        
        # Prepare the workflow result
        workflow_result = {
            "steps": steps,
            "Test_case": test_cases,
            "gherkins_scenario": gherkin_scenarios,
            "playwright_script": playwright_script,
            "workflow_status": "Test Generation Complete",
            "awaiting_human_input": False,  # No longer awaiting human input
            #"applications_covered": state.get("parsed_story", {}).get("Applications_Involved", []),
            "sop_generation_used": True,
            "sop_context": sop_context  # Include SOP context in result
        }
        
        print(f"✅ SOP-based test generation completed successfully")
        print(f"  Steps generated: {len(workflow_result.get('steps', []))}")
        print(f"  Test cases generated: {len(workflow_result.get('Test_case', []))}")
        print(f"  Applications covered: {workflow_result.get('applications_covered', [])}")
        print(f"  SOP context used: {len(sop_context)} documents")
        
        return workflow_result
        
    except Exception as e:
        print(f"❌ SOP-based test generation failed: {e}")
        raise e

@app.post("/workflow")
async def workflow_handler(request: WorkflowRequest):
    print("Received request:", request.dict())  # Log incoming request
    try:
        # Always use SOP-based generation for all requests
        if request.input and not request.run_id:
            # New workflow request - use SOP-based generation
            print("🔄 Using SOP-based generation for new workflow")
            result = run_sop_based_workflow(request.input, request.sop_context)
        elif request.input and request.run_id:
            # Resume workflow with human input - use SOP-based generation
            print("🔄 Resuming SOP-based workflow with human input")
            # For resuming, we need to handle the human approval logic
            # Since we don't have the original user story in the request, we'll need to handle this differently
            # For now, let's treat this as a new SOP workflow with the input as the user story
            result = run_sop_based_workflow(request.input, request.sop_context)
        elif request.run_id:
            # Resume workflow without input - this shouldn't happen with current setup
            print("⚠️ Resume workflow without input - not supported in SOP-based workflow")
            raise HTTPException(
                status_code=400, 
                detail="Resume workflow without input is not supported. Please provide 'input' with your request."
            )
        else:
            raise HTTPException(
                status_code=400, 
                detail="Invalid request. Provide 'input' (user story) for new or resumed workflows"
            )
        
        # Check if this is a human approval response
        if request.input and request.run_id and result.get("awaiting_human_input", False):
            print(f"📝 Human feedback received: {request.input}")
            
            # Use LLM to analyze human feedback using the validation node
            try:
                from nodes.validation_nodes import human_feedback
                from models.state import GraphState
                
                # Create state with human input for LLM analysis
                feedback_state = GraphState({
                    "human_input": request.input,
                    "parsed_story": result.get("parsed_story", {}),
                    "sop_context": result.get("sop_context", []),
                    "user_story": result.get("user_story", "")
                })
                
                # Process human feedback with LLM
                print("🔄 Analyzing human feedback with LLM...")
                processed_state = human_feedback(feedback_state)
                
                # Check if LLM determined this is an approval
                if not processed_state.get("awaiting_human_input", True):
                    print("✅ LLM determined this is an approval - proceeding with test generation")
                    
                    # For SOP workflows, generate test artifacts after approval
                    if result.get("sop_generation_used", False):
                        print("🔄 Generating SOP-based test artifacts after human approval...")
                        sop_context = result.get("sop_context")
                        test_result = run_sop_test_generation(request.input, sop_context)
                        
                        # Update result with generated test artifacts
                        result.update(test_result)
                        result["workflow_status"] = "Human Approved - Test Generation Complete"
                    else:
                        # For legacy workflows, just update status
                        result["awaiting_human_input"] = False
                        result["workflow_status"] = "Human Approved - Proceeding with Test Execution"
                else:
                    print("📝 LLM determined this is feedback, not approval")
                    # Keep awaiting human input but acknowledge the feedback
                    return {
                        "role": "ai",
                        "message": f"Thank you for your feedback: '{request.input}'. Please provide approval to continue with test generation.",
                        "metadata": {
                            "run_id": result.get("RunID", "unknown"),
                            "workflow_status": "Awaiting Human Approval",
                            "awaiting_human_input": True,
                            "sop_generation_used": result.get("sop_generation_used", False),
                            "applications_covered": result.get("applications_covered", [])
                        }
                    }
                    
            except Exception as e:
                print(f"❌ Error analyzing human feedback with LLM: {e}")
                # Fallback to simple keyword-based approval
                approval_keywords = ["approve", "proceed", "good to go", "ok", "yes", "continue", "go ahead"]
                user_input_lower = request.input.lower().strip()
                
                if user_input_lower in approval_keywords:
                    print("✅ Fallback: Simple approval detected - proceeding with test generation")
                    
                    # For SOP workflows, generate test artifacts after approval
                    if result.get("sop_generation_used", False):
                        print("🔄 Generating SOP-based test artifacts after human approval...")
                        sop_context = result.get("sop_context")
                        test_result = run_sop_test_generation(request.input, sop_context)
                        
                        # Update result with generated test artifacts
                        result.update(test_result)
                        result["workflow_status"] = "Human Approved - Test Generation Complete"
                    else:
                        # For legacy workflows, just update status
                        result["awaiting_human_input"] = False
                        result["workflow_status"] = "Human Approved - Proceeding with Test Execution"
                else:
                    print("📝 Fallback: Feedback detected, not approval")
                    return {
                        "role": "ai",
                        "message": f"Thank you for your feedback: '{request.input}'. Please provide approval to continue with test generation.",
                        "metadata": {
                            "run_id": result.get("RunID", "unknown"),
                            "workflow_status": "Awaiting Human Approval",
                            "awaiting_human_input": True,
                            "sop_generation_used": result.get("sop_generation_used", False),
                            "applications_covered": result.get("applications_covered", [])
                        }
                    }
        
        ai_output = format_state_to_ai_output(result)
        print("Returning response:", ai_output)  # Log outgoing response
        
        # Debug logging for workflow status
        print(f"🔍 DEBUG - Workflow Status: {result.get('workflow_status', 'unknown')}")
        print(f"🔍 DEBUG - Awaiting Human Input: {result.get('awaiting_human_input', False)}")
        print(f"🔍 DEBUG - Has Test Case: {bool(result.get('Test_case'))}")
        print(f"🔍 DEBUG - Has Gherkin: {bool(result.get('gherkins_scenario'))}")
        print(f"🔍 DEBUG - SOP Generation Used: {result.get('sop_generation_used', False)}")
        if result.get('sop_generation_used'):
            print(f"🔍 DEBUG - Applications Covered: {result.get('applications_covered', [])}")
        
        # Check if workflow is awaiting human input or if test case generation is complete
        if result.get("awaiting_human_input", False):
            # Check if this is SOP workflow or legacy workflow
            if result.get("sop_generation_used", False):
                # SOP workflow - show parsed story for human validation (test artifacts will be generated after approval)
                parsed_story = result.get("parsed_story", {})
                
                # Create a message showing the parsed story in the desired format
                message_parts = []
                message_parts.append(" Parsed User Story ")
                
                if parsed_story:
                    if 'Objective' in parsed_story and parsed_story['Objective']:
                        message_parts.append(f"**Objective:** {parsed_story['Objective']}")
                    if 'Applications_Involved' in parsed_story and parsed_story['Applications_Involved']:
                        message_parts.append(f"**Applications Involved:** {', '.join(parsed_story['Applications_Involved'])}")
                    if 'Manual_Steps' in parsed_story and parsed_story['Manual_Steps']:
                        message_parts.append("**Manual Steps:**")
                        for i, step in enumerate(parsed_story['Manual_Steps'], 1):
                            message_parts.append(f"{i}. {step}")
                    if 'Test_Automation' in parsed_story and parsed_story['Test_Automation']:
                        message_parts.append("**Test Automation Steps:**")
                        for i, step in enumerate(parsed_story['Test_Automation'], 1):
                            message_parts.append(f"{i}. {step}")
                
                # Add feedback prompt
                message_parts.append("")
                message_parts.append("**Please review the parsed user story above and provide feedback.**")
                
                message_md = "\n".join(message_parts)
                
                return {
                    "role": "ai",
                    "message": message_md,
                    "metadata": {
                        "run_id": result.get("RunID", "unknown")
                    }
                }
            else:
                # Legacy workflow - show parsed story for human validation
                parsed_story = result.get("parsed_story", {})
                missing_fields = result.get("missing_fields", [])
                
                # Create a formatted message showing the parsed story
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
                    "role": ai_output.get("role", "ai"),
                    "message": message_md,
                    "metadata": {
                        "run_id": result.get("RunID", "unknown"),
                        "workflow_status": result.get("workflow_status", "Awaiting Human Feedback"),
                        "awaiting_human_input": bool(result.get("awaiting_human_input", False)),
                        "sop_generation_used": result.get("sop_generation_used", False),
                        "applications_covered": result.get("applications_covered", []),
                        "parsed_story": parsed_story,
                        "missing_fields": missing_fields
                    }
                }
        # Only proceed to test generation if NOT awaiting human input AND test artifacts exist
        elif not result.get("awaiting_human_input", False) and (result.get("Test_case") or result.get("gherkins_scenario")):
            # Test case generation is complete
            Test_case = result.get("Test_case") or ""
            gherkins_scenario = result.get("gherkins_scenario") or ""
            
            # Debug logging for gherkin scenario
            print(f"🔍 DEBUG - Test_case length: {len(Test_case)}")
            print(f"🔍 DEBUG - gherkins_scenario length: {len(gherkins_scenario)}")
            print(f"🔍 DEBUG - gherkins_scenario preview: {gherkins_scenario[:200] if gherkins_scenario else 'EMPTY'}...")
            
            # Step 1: Use the generated Playwright script from the workflow
            print("🔄 Auto Step 1: Using generated Playwright script from workflow...")
            playwright_script = result.get("playwright_script", "")
            steps = result.get("steps", [])
            
            if playwright_script and steps:
                print(f"✅ Generated Playwright script available (length: {len(playwright_script)} characters)")
                print(f"✅ Steps available: {len(steps)} steps")
            else:
                print(f"⚠️ No generated Playwright script available")
                playwright_script = ""
            
            # Generate and save markdown report
            try:
                # Add playwright script to result for markdown report
                result["playwright_code"] = playwright_script
                
                # Generate markdown report
                run_id = result.get("RunID", "unknown")
                markdown_file_path = save_markdown_report(result, run_id, "reports")
                
                print(f"📄 Markdown report generated: {markdown_file_path}")
                
                # Read the markdown content to include in response
                with open(markdown_file_path, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()
                
            except Exception as e:
                print(f"⚠️ Error generating markdown report: {e}")
                markdown_content = f"Error generating markdown report: {str(e)}"
                markdown_file_path = "Error"
            
            # Return the response with the generated Playwright script immediately
            response_data = {
                "role": "ai",
                "message": "Test Script Generation Completed",
                "metadata": {
                    "run_id": result.get("RunID", "unknown"),
                    "test_case": Test_case,
                    #"gherkins": gherkins_scenario,
                    "test_script": playwright_script
                }
            }
            
            # # Auto-trigger pytest execution in background
            # if playwright_script:
            #     print("🚀 Auto-triggering pytest execution in background...")
            #     import threading
                
            #     def run_pytest_background():
            #         try:
            #             import subprocess
            #             import os
            #             from pathlib import Path

            #             # Use dynamic path for output.py file
            #             current_dir = Path.cwd()
            #             pytest_file = current_dir / "output.py"
                        
            #             # Run pytest in background
            #             result = subprocess.run(
            #                 ["python", "-m", "pytest", str(pytest_file), "-v", "--tb=short"],
            #                 capture_output=True,
            #                 text=True,
            #                 cwd=os.getcwd()
            #             )
                        
            #             print(f"✅ Background pytest completed with return code: {result.returncode}")
            #             if result.stdout:
            #                 print("📋 Background pytest output:", result.stdout)
            #             if result.stderr:
            #                 print("⚠️ Background pytest errors:", result.stderr)
                            
            #         except Exception as e:
            #             print(f"❌ Background pytest error: {e}")
                
            #     # Start background thread
            #     pytest_thread = threading.Thread(target=run_pytest_background, daemon=True)
            #     pytest_thread.start()
            #     print("✅ Background pytest thread started")
            
            return response_data
        else:
            # Fallback case - workflow completed but no test case generated
            return {
                "role": "ai",
                "message": "Workflow completed but no test case was generated. Please check the workflow status.",
                "metadata": {
                    "run_id": result.get("RunID", "unknown"),
                    "workflow_status": result.get("workflow_status", "Completed - No Test Case"),
                    "awaiting_human_input": False,
                    "debug_info": {
                        "has_test_case": bool(result.get("Test_case")),
                        "has_gherkin": bool(result.get("gherkins_scenario")),
                        "has_steps": bool(result.get("steps")),
                        "has_sop_context": bool(result.get("sop_context"))
                    }
                }
            }
            # After automation, update message and metadata as required
            # return {
            #     "role": "ai",
            #     "message": "Test Script Generation Completed",
            #     "metadata": {
            #         "Test_case": Test_case,
            #         "Gherkins_Scenario": gherkins_scenario,
            #         "Test_script": playwright_code
            #     }
            # }
    except Exception as e:
        print("Exception in workflow_handler:", str(e))  # Log exception
        raise HTTPException(status_code=500, detail=f"Workflow error: {str(e)}")

@app.post("/sync-orchestrator")
async def sync_orchestrator_endpoint():
    """Endpoint to sync orchestrator.py with step.py"""
    print("🔄 Syncing orchestrator...")
    result = sync_orchestrator_step()
    if result["success"]:
        return {"status": "success", "message": result["message"], "output": result.get("output", "")}
    else:
        raise HTTPException(status_code=500, detail=result["message"])

@app.post("/run-automation")
async def run_automation_endpoint():
    """Endpoint to run automation via run_step.py"""
    print("🤖 Running automation...")
    result = run_step_automation()
    if result["success"]:
        return {"status": "success", "message": result["message"], "output": result.get("output", "")}
    else:
        raise HTTPException(status_code=500, detail=result["message"])

@app.post("/sop-workflow")
async def sop_workflow_handler(request: WorkflowRequest):
    """Dedicated endpoint for SOP-based workflow with human validation"""
    if not SOP_GENERATION_AVAILABLE:
        raise HTTPException(status_code=503, detail="SOP-based generation not available")
    
    print("🔄 SOP workflow request received")
    print(f"  Input length: {len(request.input) if request.input else 0} characters")
    print(f"  SOP context provided: {request.sop_context is not None}")
    
    try:
        if not request.input:
            raise HTTPException(status_code=400, detail="SOP workflow requires 'input' (user story)")
        
        result = run_sop_based_workflow(request.input, request.sop_context)
        
        # Check if this is a human approval response
        if request.input and request.run_id and result.get("awaiting_human_input", False):
            # Check if user provided approval feedback (using LLM to interpret)
            approval_keywords = ["approve", "proceed", "good to go", "ok", "yes", "continue", "go ahead"]
            user_input_lower = request.input.lower().strip()
            
            # Check for exact matches first
            if user_input_lower in approval_keywords:
                print("✅ Human approval received - proceeding with test generation")
                
                # Generate test artifacts after approval
                print("🔄 Generating SOP-based test artifacts after human approval...")
                sop_context = result.get("sop_context")
                test_result = run_sop_test_generation(request.input, sop_context)
                
                # Update result with generated test artifacts
                result.update(test_result)
                result["workflow_status"] = "Human Approved - Test Generation Complete"
            else:
                print(f"📝 Human feedback received: {request.input}")
                # Keep awaiting human input but acknowledge the feedback
                return {
                    "role": "ai",
                    "message": f"Thank you for your feedback: '{request.input}'. Please provide approval (e.g., 'approve', 'proceed', 'good to go') to continue with test generation.",
                    "metadata": {
                        "run_id": result.get("RunID", "unknown"),
                        "workflow_status": "Awaiting Human Approval",
                        "awaiting_human_input": True,
                        "sop_generation_used": True,
                        "applications_covered": result.get("applications_covered", [])
                    }
                }
        
        # Check if workflow is awaiting human input
        if result.get("awaiting_human_input", False):
            # Show parsed story for human validation (test artifacts will be generated after approval)
            parsed_story = result.get("parsed_story", {})
            
            # Create a message showing the parsed story
            message_parts = []
            message_parts.append("## Parsed User Story (SOP-Enhanced)")
            
            if parsed_story:
                if 'Objective' in parsed_story and parsed_story['Objective']:
                    message_parts.append(f"**Objective:** {parsed_story['Objective']}")
                if 'Test_Summary' in parsed_story and parsed_story['Test_Summary']:
                    message_parts.append("**Test Summary:**")
                    for i, summary in enumerate(parsed_story['Test_Summary'], 1):
                        message_parts.append(f"{i}. {summary}")
                if 'Acceptance_Criteria' in parsed_story and parsed_story['Acceptance_Criteria']:
                    message_parts.append("**Acceptance Criteria:**")
                    for i, crit in enumerate(parsed_story['Acceptance_Criteria'], 1):
                        message_parts.append(f"{i}. {crit}")
                if 'Applications_Involved' in parsed_story and parsed_story['Applications_Involved']:
                    message_parts.append(f"**Applications Involved:** {', '.join(parsed_story['Applications_Involved'])}")
            
            # Add SOP context info if available
            sop_context = result.get("sop_context")
            if sop_context:
                message_parts.append("")
                message_parts.append("**SOP Context Available:** ✅")
                message_parts.append(f"**SOP Items:** {len(sop_context)}")
            
            # Add feedback prompt
            message_parts.append("")
            message_parts.append("**Please review the parsed user story above and provide feedback.**")
            message_parts.append("**Type 'approve', 'proceed', or 'good to go' to generate test cases and Gherkin scenarios.**")
            
            message_md = "\n".join(message_parts)
            
            return {
                "role": "ai",
                "message": message_md,
                "metadata": {
                    "run_id": result.get("RunID", "unknown"),
                    "workflow_status": result.get("workflow_status", "Awaiting Human Feedback"),
                    "awaiting_human_input": True,
                    "sop_generation_used": True,
                    "applications_covered": result.get("applications_covered", []),
                    "parsed_story": parsed_story,
                    "sop_context": sop_context
                }
            }
        else:
            # Workflow completed without human input (shouldn't happen with current setup)
            return {
                "role": "ai",
                "message": "SOP-based Test Generation Completed",
                "metadata": {
                    "run_id": result.get("RunID", "unknown"),
                    "workflow_status": result.get("workflow_status", "Completed"),
                    "steps": result.get("steps", []),
                    "test_case": result.get("Test_case", []),
                    "gherkin_scenarios": result.get("gherkins_scenario", ""),
                    "applications_covered": result.get("applications_covered", []),
                    "sop_generation_used": True
                }
            }
        
    except Exception as e:
        print(f"❌ SOP workflow error: {e}")
        raise HTTPException(status_code=500, detail=f"SOP workflow error: {str(e)}")

@app.post("/complete-flow")
async def complete_flow_endpoint():
    """Complete flow: sync orchestrator + run automation"""
    print("🚀 Starting complete flow...")
    
    # Step 1: Sync orchestrator
    print("🔄 Step 1: Syncing orchestrator...")
    sync_result = sync_orchestrator_step()
    if not sync_result["success"]:
        raise HTTPException(status_code=500, detail=f"Sync failed: {sync_result['message']}")
    
    # Step 2: Run automation
    print("🤖 Step 2: Running automation...")
    automation_result = run_step_automation()
    if not automation_result["success"]:
        raise HTTPException(status_code=500, detail=f"Automation failed: {automation_result['message']}")
    
    return {
        "status": "success",
        "message": "Complete flow executed successfully",
        "sync_output": sync_result.get("output", ""),
        "automation_output": automation_result.get("output", "")
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from datetime import datetime
    return {
        "status": "healthy",
        "sop_generation_available": SOP_GENERATION_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/run-pytest")
async def run_pytest_endpoint():
    """Run pytest on the output.py file"""
    try:
        import subprocess
        import os
        from pathlib import Path
        
        # Check if output.py exists
        output_file = Path("output.py")
        if not output_file.exists():
            raise HTTPException(status_code=404, detail="output.py file not found")
        
        print(f"🚀 Running pytest on: {output_file}")
        
        # Run pytest
        result = subprocess.run(
            ["python", "-m", "pytest", str(output_file), "-v", "--tb=short"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        pytest_result = {
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0
        }
        
        print(f"✅ Pytest execution completed with return code: {result.returncode}")
        
        return {
            "status": "success",
            "pytest_result": pytest_result,
            "file": str(output_file)
        }
        
    except Exception as e:
        print(f"❌ Pytest execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Pytest execution failed: {str(e)}")

@app.get("/capabilities")
async def get_capabilities():
    """Get API capabilities"""
    return {
        "legacy_workflow": True,
        "sop_based_workflow": SOP_GENERATION_AVAILABLE,
        "applications_supported": [
            "Intake", "Clearance", "RxP Order Entry", 
            "RxP Data Verification", "CRM", "Trend Processing"
        ] if SOP_GENERATION_AVAILABLE else [],
        "features": [
            "Comprehensive test case generation",
            "Gherkin scenario generation", 
            "Playwright automation script generation",
            "Markdown report generation",
            "SOP context integration",
            "Pytest execution for output.py"
        ] if SOP_GENERATION_AVAILABLE else [
            "Basic test case generation",
            "Gherkin scenario generation"
        ],
        "endpoints": [
            "/workflow - Main workflow endpoint",
            "/sop-workflow - SOP-based workflow endpoint", 
            "/complete-flow - Complete workflow endpoint",
            "/sync-orchestrator - Sync orchestrator endpoint",
            "/run-automation - Run automation endpoint",
            "/run-pytest - Run pytest on output.py",
            "/health - Health check endpoint",
            "/capabilities - This endpoint"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting FastAPI with SOP-based generation support...")
    print(f"✅ SOP Generation Available: {SOP_GENERATION_AVAILABLE}")
    uvicorn.run(app, host="0.0.0.0", port=8000, timeout_keep_alive=200000)