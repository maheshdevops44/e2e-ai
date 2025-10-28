"""
Parsing nodes for user story processing
"""

import json
from datetime import datetime
from typing import Dict, Any

from langgraph.store.base import Result
from config.llm_config import llm
from models.state import GraphState
from models.messages import add_message_to_state, add_workflow_step

import sys
import os
# Ensure project root is in sys.path for qa_workflow imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

#from generated_scripts.generated_playwright_20250714_061229 import run_clearance_workflow

def parse_user_story_llm(state: GraphState) -> GraphState:
    """Parse user story using LLM"""
    print("\n=== [PARSING NODE] Starting user story parsing ===\n")
    print("\n" + "="*40)
    print(f"### 🔄 Running node: `PARSING NODE`")
    print("="*40 + "\n")
    
    # Add workflow step
    state = add_workflow_step(state, "parse_user_story", "in_progress")
    
    # Add system message
    state = add_message_to_state(
        state, 
        "system", 
        "Starting user story parsing",
        {"node": "parse_user_story", "timestamp": datetime.now().isoformat()}
    )
    
    parse_prompt = """
    
    **We have applications like Daas, TDM, Intake, Clearance, RxP, RPH and CRM in our system. Steps belongs to Daas or Intake  or TDM application goes under Manual_Steps. Steps belongs to Clearance, RxP, RPH and CRM application goes under Test_Automation **
    **Understand the user story very carefully and its steps which needs to perform mentioned in QA requirement scenario or steps which is in the scope of user story only.
      Based on user story and each application functionality (manual or automation), parse the given user story and provide standard template in this format:
    **Use words like verify, check, click, enter etc in the steps where needed**
    **End to End Scenario refers to testing scenario across multiple applications based on the scenario. Like for example Direct Patient will Intake, Clearance, Rxp, CRM, Trend. For scenarios with Integrated Patient in Biosimilar sometimes it will be Intake,RxP,Trend, CRM.**
    **DO NOT HALLUCINATE
    
    - **Objective**: What is the main goal or objective of running this test scenario?
    - **Test Summary**: Brief description of what needs to be tested
    - **Acceptance Criteria**: List of specific criteria that must be met
    - **Applications Involved**: Which applications are part of this workflow
    - **Manual_Steps**:Manual_Steps should be blank if no 'DaaS' or 'TDM'. All Intake Steps are automated except dummy fax ingestion.
    - **Test Automation Steps**:Infer Automation steps based on the given user story.DO NOT HALLUCINATE.


    User Story: {user_story}

    **Use the input values provided in the User story in steps except for Patient ID and common intake ID**
    
    Make sure everything is in bulleted points except Objective. Respond in JSON format. If any information is missing, keep them as empty in the JSON."""
    
    prompt = parse_prompt.format(user_story=state['user_story'])
    
    print(f"🔍 DEBUG: Sending prompt to LLM:")
    print(f"  Prompt length: {len(prompt)} characters")
    print(f"  User story: {state['user_story'][:200]}...")
    
    # Call the llm function directly since it's not a LangChain object
    content_str = llm(prompt)
    
    # Handle the response as a string directly
    if isinstance(content_str, list):
        content_str = " ".join(str(item) for item in content_str)
    elif not isinstance(content_str, str):
        content_str = str(content_str)
    
    print(f"🔍 DEBUG: LLM Response:")
    print(f"  Response type: {type(content_str)}")
    print(f"  Content length: {len(content_str)} characters")
    print(f"  Content preview: {content_str[:500]}...")
    
    try:
        # Clean the content - remove markdown code blocks if present
        cleaned_content = content_str.strip()
        if cleaned_content.startswith('```json'):
            cleaned_content = cleaned_content[7:]  # Remove ```json
        if cleaned_content.startswith('```'):
            cleaned_content = cleaned_content[3:]  # Remove ```
        if cleaned_content.endswith('```'):
            cleaned_content = cleaned_content[:-3]  # Remove trailing ```
        
        cleaned_content = cleaned_content.strip()
        print(f"🔍 DEBUG: Cleaned content preview: {cleaned_content[:200]}...")
        
        parsed_story = json.loads(cleaned_content)
        workflow_status = "parsing complete"
        state = add_workflow_step(state, "parse_user_story", "completed", "User story parsed successfully")
        print(f"✅ JSON parsing successful!")
        print(f"  Parsed story keys: {list(parsed_story.keys())}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        print(f"  Raw content: {content_str}")
        print(f"  Cleaned content: {cleaned_content if 'cleaned_content' in locals() else 'Not available'}")
        parsed_story = {}
        workflow_status = "user story could not be parsed"
        state = add_workflow_step(state, "parse_user_story", "failed", error=f"JSON parsing failed: {e}")
  
    response_lines = content_str.splitlines()
    parsed_story_ = "\n".join(response_lines)
    
    # Add result message
    state = add_message_to_state(
        state, 
        "assistant", 
        f"Parsed user story: {parsed_story_}",
        {"node": "parse_user_story", "status": "completed"}
    )
    
    result = {**state, "parsed_story": parsed_story, "workflow_status": workflow_status}
    print("\n=== [PARSING NODE] Finished user story parsing ===\n")
    return result

def check_missing_fields(state: GraphState) -> GraphState:
    """Check for missing fields in parsed story"""
    print("\n=== [CHECK MISSING FIELDS NODE] Checking for missing fields ===\n")
    print("\n" + "="*40)
    print(f"### 🔄 Running node: `CHECKING MISSING FIELDS`")
    print("="*40 + "\n")
    
    # Add workflow step
    state = add_workflow_step(state, "check_missing_fields", "in_progress")
    
    parsed = state["parsed_story"]
    required = ["Objective", "Test Summary", "Acceptance Criteria", "Manual_Steps", "Applications Involved"]
    missing = [field for field in required if field not in parsed or not parsed[field]]
    
    if len(missing) > 0:
        workflow_status = "missing fields"
        state = add_workflow_step(state, "check_missing_fields", "completed", f"Found {len(missing)} missing fields")
        state["awaiting_human_input"] = True
    else:
        workflow_status = "No missing fields found"
        missing = []
        state = add_workflow_step(state, "check_missing_fields", "completed", "All required fields present")
        state["awaiting_human_input"] = True  # Always trigger human feedback
    
    print(f"### 🚦 Output: ", missing)
    
    # Add message to state
    state = add_message_to_state(
        state, 
        "assistant", 
        f"Missing fields check completed. Missing: {missing}",
        {"node": "check_missing_fields", "missing_fields": missing}
    )
    
    result = {**state, "missing_fields": missing, "workflow_status": workflow_status}
    #print(f"\n=== [CHECK MISSING FIELDS NODE] Finished checking. Missing: {missing} ===\n")
    return result

def fill_missing_with_llm(state: GraphState) -> GraphState:
    """Fill missing fields using LLM suggestions"""
    print("\n=== [FILL MISSING FIELDS NODE] Filling missing fields with LLM ===\n")
    print(f"### 🚦 Running node: `FILL MISSING FIELDS`")
    
    # Add workflow step
    state = add_workflow_step(state, "fill_missing_with_llm", "in_progress")
    
    if not state["missing_fields"]:
        state = add_workflow_step(state, "fill_missing_with_llm", "completed", "No missing fields to fill")
        print("\n=== [FILL MISSING FIELDS NODE] Finished filling missing fields ===\n")
        return state
    
    missing_fields_prompt = "Identify missing fields in the user story. Update the {parsed_story} by filling the {missing_fields} appropriately and ask human to review.Do not suggest any new fields on your own."
    prompt = missing_fields_prompt.format(parsed_story=state['parsed_story'], missing_fields=state['missing_fields'])
    content_str = llm(prompt)
    
    # Add message to state
    state = add_message_to_state(
        state, 
        "assistant", 
        content_str,
        {"node": "fill_missing_with_llm", "action": "suggestion"}
    )
    
    state = add_workflow_step(state, "fill_missing_with_llm", "completed", "LLM suggestions generated")
    
    print("\n=== [FILL MISSING FIELDS NODE] Finished filling missing fields ===\n")
    return {
        **state,
        "llm_suggestion": content_str,
        "message": f"{content_str}. Do you want to accept or edit?",
        "workflow_status": "Awaiting QA team input",
        "validation_step": "missing_fields"
    } 

async def run_playwright_workflow():
    # from playwright.async_api import async_playwright
    # async with async_playwright() as p:
    #     browser = await p.chromium.launch(headless=False)
    #     page = await browser.new_page()
    #     await run_clearance_workflow(page)
    #     await browser.close() 
    pass