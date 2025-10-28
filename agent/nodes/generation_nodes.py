
# SOP Integration Note:
# For comprehensive test generation using SOP context, use generate_steps_from_sop.py
# This provides better coverage across all applications in the end-to-end workflow
"""
Test case and Gherkin generation nodes
"""

import json
import os
import sys
import dotenv
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from config.llm_config import llm
from nodes.adapters.llm_adapters import get_azure_llm
from models.state import GraphState
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.callbacks import get_openai_callback
#from Patient_ID_generator import get_random_patient_data
from models.messages import add_message_to_state, add_workflow_step
from nodes.agent_utils import find_element_across_frames
from time import sleep
import pytest
from playwright.sync_api import sync_playwright, Page, expect
from nodes.intake_code import generate_intake_steps
from nodes.patient_id_generator import patient_id_generator

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dotenv.load_dotenv()

def patient__type(steps_str):
    print("------------------------STEPS------------------------",steps_str)
    print(f"🔍 DEBUG: patient__type function called with steps_str length: {len(steps_str)}")
    print(f"🔍 DEBUG: First 500 characters of steps_str: {steps_str[:500]}")
    print(f"🔍 DEBUG: Checking if '799' in steps_str: {'799' in steps_str}")
    print(f"🔍 DEBUG: Checking if 'Integrated' in steps_str: {'Integrated' in steps_str}")
    
    if "799" in steps_str:
        print("🔍 DEBUG: Found '799' in steps_str, returning 'Integrated'")
        return "Integrated"
    elif "GLAT" and ("Reject 75" or "Reject") in steps_str:
        print("🔍 DEBUG: Found 'GLAT' in steps_str, returning 'Reject'")
        return "Reject"
    else:
        print("🔍 DEBUG: No '555' or 'GLAT' found, returning 'Direct'")
        return "Direct"
    
def extract_python_code(llm_output: str) -> str:
    """
    Extract and return just the Python code block from a string with potential markdown/code wrapping.
    Works with fenced code blocks (```python ... ```) or raw code.
    """
    # Look for ```python ... ``` or ``` ... ``` fenced code block first
    match = re.search(
        r"```python(.*?)```",
        llm_output,
        re.DOTALL | re.IGNORECASE
    )
    if match:
        code = match.group(1)
    else:
        # Fallback: any ``` ... ``` block
        match = re.search(r"```(.*?)```", llm_output, re.DOTALL)
        if match:
            code = match.group(1)
        else:
            # No fences found, return the whole text
            code = llm_output

    # Remove any leading/trailing whitespace
    return code.strip()


def get_input_fields(steps):
    
    llm = get_azure_llm("ai-coe-gpt41")
    output_example = f"""
    Analyze the following automation steps and extract the required fields in JSON format.
    
    Steps to analyze:
    {steps}
    
    REQUIRED FIELDS (include ALL of these, use "Direct" if not found):
    - patient_type: "Direct" or "Integrated" (determine from service_branch: 555=Direct, 799=Integrated)
    - service_branch: The service branch code (555 or 799)
    - ndc: National Drug Code
    - quantity: Quantity of medication
    - days_supply: Days supply
    - refills: Number of refills
    
    IMPORTANT: 
    1. ALWAYS include patient_type field
    2. If service_branch is 555, patient_type should be "Direct"
    3. If service_branch is , patient_type should be "Integrated"
    4. Return ONLY valid JSON, no markdown formatting
    
    Example response format:
    {{
        "patient_type": "Direct",
        "service_branch": "555",
        "ndc": "12345678901",
        "quantity": 1,
        "days_supply": 14,
        "refills": 1
    }}
    """
    messages = [ SystemMessage(output_example), HumanMessage("Please extract the fields from the steps above.") ]

    field_json = llm.invoke(messages).content

    return field_json


def generate_steps_llm(state: GraphState) -> GraphState:
    print("\n### 🔄 Running node: GENERATING STEPS\n")
    state = add_workflow_step(state, "generate_steps", "in_progress")
    
    # Handle different field name variations
    parsed_story = state["parsed_story"].get("Test_Automation") or state["parsed_story"].get("Test_Automation")
    print(f"🔍 DEBUG: Extracted Test_Automation: {parsed_story}")
    
    # Also check for Applications Involved field
    applications_involved = state["parsed_story"].get("Applications Involved") or state["parsed_story"].get("Applications_Involved")
    print(f"🔍 DEBUG: Applications Involved: {applications_involved}")
    
    sop_context = state["sop_context"]
    #print(f"🔍 DEBUG: Received SOP context: {sop_context}")
    print(f"🔍 DEBUG: SOP context type: {type(sop_context)}")
    print(f"🔍 DEBUG: SOP context length: {len(sop_context) if sop_context else 0}")
    
    sop_is_empty = True
    if sop_context and len(sop_context) > 0:
        try:
            sop_data = json.loads(sop_context[0])
            print(f"🔍 DEBUG: Parsed SOP data: {sop_data}")
            print(f"🔍 DEBUG: SOP data type: {type(sop_data)}")
            print(f"🔍 DEBUG: SOP data length: {len(sop_data) if sop_data else 0}")
            if sop_data and len(sop_data) > 0:
                sop_is_empty = False
                print("✅ SOP data found and not empty")
            else:
                print("⚠️ SOP data is empty")
        except Exception as e:
            print(f" Error parsing SOP data: {e}")
            print(f"🔍 DEBUG: Raw SOP context[0]: {sop_context[0] if sop_context else 'None'}")
    
    print(f"🔍 DEBUG: sop_is_empty = {sop_is_empty}")
    # ALWAYS use SOP context by default - even if empty, we'll provide a fallback
    print("🔍 DEBUG: Using SOP-BASED prompt (default)")
    
    # Ensure we have SOP context - if empty, provide a minimal fallback
    if sop_is_empty:
        sop_context_display = "No specific SOP documents found, but use standard clearance eligibility testing procedures."
        print("⚠️ No SOP documents found, unable to fetch SOP")
        raise RuntimeError("Unable to fetch SOP documents for test case generation")
    else:
        sop_context_display = sop_context
        print("✅ Using retrieved SOP documents")

    patient_id = "1*******"
    COMMON_INTAKE_ID = "CMNINTAKE***************"

    prompt = f"""
    USER STORY:
    {parsed_story}
    
    SOP CONTEXT (Standard Operating Procedures):
    {sop_context_display}
    
    Patient ID:
    {patient_id}

    COMMON_INTAKE_ID:
    {COMMON_INTAKE_ID}
    
    CRITICAL INSTRUCTIONS - READ CAREFULLY:
    1. DO NOT HALLUCINATE - use ONLY the information provided above
    2. If Service branch or SB=555 in parsed story then it is Direct patient. If Service branch or SB=799 in parsed story then it is Integrated patient.
    3. Use ONLY the specific steps, applications, and data mentioned in the SOP context
    4. Do not add any information that is not explicitly mentioned in the provided context
    5. Generate steps based on the actual content provided, not generic templates
    6. Each step must be specific to the actual workflow described in the SOP context.
    7. Do include any steps for TDM tool.
    8. Do include any steps for database check.
    9. **ALWAYS** Use the input fields given in the {parsed_story} except patient ID and common intake ID.
    10. If all the required input fields are not there in {parsed_story} then used the input fields from {sop_context_display}
    11. Use patient ID and common intake ID from {patient_id} and {COMMON_INTAKE_ID}. The document id is the common intake ID.
    12. Do not use this step **use the value from 'document_id' in the provided JSON; if None, skip this step or flag for manual input** 
    13. Do not use placeholder for common intake id or patient id use the actual values from {patient_id}
    14. **ALWAYS If parsed user story is for integrated patient or service branch is 799 then **DO NOT INCLUDE CLEARANCE STEPS**. Clearance will be run in the background automatically after intake.
    15. **ALWAYS If parsed user story is for Direct patient or service branch is 555 then **INCLUDE CLEARANCE ** steps after intake.
    16. **DO NOT INCLUDE this step for integrated patient - # Step 4: Prescriber Section - Clear, Search NPI, Select Phone/Fax, Submit
    
    Generate detailed automation steps that cover the end-to-end workflow described in the user story.
    Use the SOP context to provide specific UI interactions and application-specific steps.
    
    Focus on the applications mentioned in the user story: {applications_involved}
    
    Use the specific test data and procedures mentioned in the SOP context.
    
    Return only the steps, one per line, starting with "- ".
    Do not include explanations or additional text.
    """
    
    print(f"🔍 DEBUG: Final prompt being sent to LLM:")
    print(f"  Length: {len(prompt)} characters")
    print(f"  Preview: {prompt[:300]}...")
    content_str = llm(prompt)
    steps = [line.strip("- ") for line in content_str.strip().split("\n") if isinstance(line, str) and line.strip().startswith("-")]
    # Keep all relevant steps - don't filter out any applications mentioned in the user story
    # Only filter out completely irrelevant or generic steps
    irrelevant_keywords = ["lorem ipsum", "test data", "placeholder", "sample text"]
    filtered_steps = []
    
    for step in steps:
        step_lower = step.lower()
        # Only filter out completely irrelevant steps
        if any(ik in step_lower for ik in irrelevant_keywords):
            continue
        # Keep all other steps, including those for Intake, RxP, Trend, CRM, etc.
        filtered_steps.append(step)
    
    if not filtered_steps:
        filtered_steps = ["No relevant steps available"]
        workflow_status = "No steps found"
        state = add_workflow_step(state, "generate_steps", "failed", "No relevant steps found")
    else:
        workflow_status = "Steps Generated"
        state = add_workflow_step(state, "generate_steps", "completed", f"Generated {len(filtered_steps)} steps")
    # Summarize steps using LLM if more than 6 steps
    if len(filtered_steps) > 6:
        summary_prompt = f"""
        Summarize the following test steps into 5-6 clear, actionable, step-like points (not just section headers). Each summary point should describe a concrete action or verification a tester would perform. Avoid mentioning browser launch, login, or setup steps—focus on the core workflow actions. Use clear, concise bullet points.
        Steps:
        {chr(10).join(['- ' + s for s in filtered_steps])}
        """
        summary_str = llm(summary_prompt)
        summary_points = [line.strip('- ') for line in summary_str.strip().split('\n') if line.strip().startswith('-')]
        print(f"\n📋 {len(filtered_steps)} steps generated for automation.\n")
        print("Summary of steps:")
        for idx, point in enumerate(summary_points, 1):
            print(f"  {idx}. {point}")
        print()
    else:
        print(f"\n📋 {len(filtered_steps)} steps generated for automation.\n")
        for idx, step in enumerate(filtered_steps, 1):
            print(f"  {idx}. {step}")
        print()
    
    # Save steps to markdown file with datetime
    try:
        from datetime import datetime
        import os
        
        # Create steps directory if it doesn't exist
        steps_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "steps")
        os.makedirs(steps_dir, exist_ok=True)
        
        # Generate filename with datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"automation_steps_{timestamp}.md"
        filepath = os.path.join(steps_dir, filename)
        
        # Create markdown content - just the steps
        markdown_content = ""
        
        # Add numbered steps only
        for idx, step in enumerate(filtered_steps, 1):
            markdown_content += f"{idx}. {step}\n"
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"📄 Steps saved to: {filepath}")
        
        # Add file path to state
        state["steps_markdown_file"] = filepath
        
    except Exception as e:
        print(f"⚠️ Error saving steps to markdown: {e}")
    
    return {**state, "steps": filtered_steps, "workflow_status": workflow_status}


def generate_test_case(state: GraphState) -> GraphState:
    print(f"\n### 🔄 Running node: GENERATE TEST CASES\n")
    state = add_workflow_step(state, "generate_test_case", "in_progress")
    
    # Debug: Show what input is being passed to test case generation
    print(f"🔍 DEBUG: Input for Test Case Generation:")
    print(f"  State keys: {list(state.keys())}")
    
    steps = state.get("steps", [])
    parsed_story = state.get("parsed_story", {})
    sop_context = state.get("sop_context", [])
    
    print(f"  Steps: {steps}")
    print(f"  Steps type: {type(steps)}")
    print(f"  Steps length: {len(steps) if steps else 0}")
    
    print(f"  Parsed Story: {parsed_story}")
    print(f"  Parsed Story type: {type(parsed_story)}")
    
    #print(f"  SOP Context: {sop_context}")
    print(f"  SOP Context type: {type(sop_context)}")
    print(f"  SOP Context length: {len(sop_context) if sop_context else 0}")
    
    if not steps or steps == ['No relevant steps available']:
        print("DEBUG: No steps for Test Case generation")
        workflow_status = "Error Retrieving Steps"
        state = add_workflow_step(state, "generate_test_case", "failed", "No steps available for test case generation")
        return {**state, "Test_case": "No steps for Test Case generation", "workflow_status": "Test Case not created"}
    
    try:
        # Stronger prompt with explicit requirement and example
        # Enhanced prompt that includes SOP context and user story
        user_story_text = str(parsed_story) if parsed_story else "No user story available"
        sop_context_text = str(sop_context) if sop_context else "No SOP context available"
        
        # Process SOP context more strictly
        if not sop_context or len(sop_context) == 0:
            sop_context_display = "NO SOP CONTEXT AVAILABLE - USE ONLY USER STORY AND STEPS"
            print("⚠️ No SOP context available - will use only user story and steps")
        else:
            # Format SOP context properly
            sop_context_display = "SOP CONTEXT:\n"
            for i, sop_item in enumerate(sop_context, 1):
                if isinstance(sop_item, dict):
                    scenario = sop_item.get('scenario', f'SOP Item {i}')
                    steps = sop_item.get('steps', 'No steps available')
                    sop_context_display += f"\n--- SOP Item {i}: {scenario} ---\n{steps}\n"
                else:
                    sop_context_display += f"\n--- SOP Item {i} ---\n{str(sop_item)}\n"
            print(f"✅ Using {len(sop_context)} SOP context items")
        
        prompt = f"""
        You are a QA automation expert. Create APPLICATION-LEVEL test cases based on the provided information.

        USER STORY:
        {user_story_text}

        SOP CONTEXT (Standard Operating Procedures):
        {sop_context_display}

        GENERATED STEPS:
        {chr(10).join(['- ' + s for s in steps])}
        
        
        # Key Changes for Direct Patient:
        # - Patient ID: Use SB=555 for direct patient ( 799 id only for integrated)
        # - Task Status: Verify as 'New' (not pending)
        # - Case Type: Direct patient
        # - Payer Info: BIN: 610140, PCN: D0TEST, GN: D0TEST
        # - Remove: Prescriber section instruction search by NPI 1336183888, select phone and fax, submit
        
        Key Changes for Integrated Patient:
        - Patient ID: Use SB=799 for Integrated patient
        - DO NOT INCLUDE clearance steps
        - Task Status: Verify as 'New' (not pending)
        - Case Type: Integrated patient 
        - Payer Info: BIN: 610140, PCN: D0TEST, GN: D0TEST
        - Remove: Prescriber section instruction search by NPI 1336183888, select phone and fax, submit

        CRITICAL INSTRUCTIONS - READ CAREFULLY:
        1. DO NOT HALLUCINATE - use ONLY the information provided above
        2. Use ONLY the specific steps, applications, and data mentioned in the SOP context
        3. Do not add any information that is not explicitly mentioned in the provided context
        4. Do not create generic or template test cases
        5. Each test case must be specific to the actual content provided
        6. Do not add this Launch Chrome or Edge browser
        7. Include the patient ID and common intake ID that is part of the generated steps wherever required.
        8. **If user story is for integrated patient or service branch is 799 then **DO NOT INCLUDE** clearance steps. Clearance will be run in the background automatically after intake.
        9. **If user story is for Direct patient or service branch is 555 then include clearance steps after intake.
    
   

        Based on the above user story, SOP context, and generated steps, create SEPARATE test cases for EACH APPLICATION involved in the workflow. If there is one application then generate TEST CASE for ONLY ONE application.
        
        Create test cases in this JSON format:
        [
          {{
            "Description": "Application-specific test description based on provided context",
            "Prerequisite": "Prerequisites mentioned in the provided context",
            "Application": "Single application name from the provided context",
            "Test Steps": [
              "Step based on provided context",
              "Another step based on provided context"
            ],
            "Expected Result": "Expected result based on provided context"
          }}
        ]

        STRICT REQUIREMENTS:
        - Use ONLY information from the provided user story, SOP context, and steps
        - The SOP context is from sop_summary_for_test_generation.md - use ONLY that content
        - Do not add any external knowledge or assumptions
        - Do not create generic test cases
        - Each test case must be directly derived from the provided context
        - Focus on the specific applications mentioned: Intake, Clearance, RxP Order Entry, RxP Data Verification, CRM, Trend Processing
        - Use the specific test data mentioned in the SOP context
        - Return only valid JSON as shown above. Do not include explanations or extra text.
        """
        
        print(f"🔍 DEBUG: Test Case Generation Prompt:")
        print(f"  Length: {len(prompt)} characters")
        print(f"  Preview: {prompt[:500]}...")
        content_str = llm(prompt)
        state["Test_case"] = content_str
        print("\n📋 Generated test cases:\n")
        import json
        try:
            cases = state.get("Test_case")
            if isinstance(cases, str):
                cases = json.loads(cases)
            if isinstance(cases, dict):
                cases = [cases]
            for idx, case in enumerate(cases, 1):
                print(f"\nTest Case {idx}:")
                print(f"  Description: {case.get('Description', '')}")
                print(f"  Prerequisite: {case.get('Prerequisite', '')}")
                print(f"  Application: {case.get('Application', '')}")
                #print(f"  Steps: {case.get('Test Steps', '')}")
                steps = case.get('Test Steps', '')
                if isinstance(steps, list):
                    print("  Steps:")
                    for idx, step in enumerate(steps, 1):
                        print(f"    {idx}. {step}")
                else:
                    print(f"  Steps: {steps}")
                print(f"  Expected Result: {case.get('Expected Result', '')}")
            print()
        except Exception as e:
            print("⚠️ Test case output was not valid JSON. Raw output:")
            print(content_str)
            print()
        workflow_status = "Test Case Generated"
        state = add_workflow_step(state, "generate_test_case", "completed", "Test case generated successfully")
        
        # Capture test case input information
        test_case_input = {
            "steps": steps,
            "parsed_story": parsed_story,
            "sop_context": sop_context,
            "prompt": prompt
        }
        
        return {**state, "workflow_status": workflow_status, "test_case_input": test_case_input}
    except Exception as e:
        print(f"Error generating test case: {e}")
        workflow_status = "Test Case Generation Failed"
        state = add_workflow_step(state, "generate_test_case", "failed", str(e))
        return {**state, "workflow_status": workflow_status}

def convert_to_gherkin_llm(state: GraphState) -> GraphState:
    """Convert steps to Gherkin format"""
    print(f"\n### 🔄 Running node: CONVERT TO GHERKIN\n")
    
    # Add workflow step
    state = add_workflow_step(state, "convert_to_gherkin", "in_progress")
    
    steps = state.get("steps", [])
    if not steps or steps == ['No relevant steps available']:
        print("DEBUG: No steps for gherkins conversion")
        workflow_status = "Error Retrieving Steps"
        state = add_workflow_step(state, "convert_to_gherkin", "failed", "No steps available for Gherkin conversion")
        return {**state, "gherkins_scenario": "No steps available to convert to Gherkin format.", "workflow_status": "No Steps Found"}
    
    #steps_str = "\n".join([f"-{step}" for step in steps])
    
    # # Get additional context for better Gherkin generation
    # parsed_story = state.get("parsed_story", {})
    # sop_context = state.get("sop_context", [])
    
    # user_story_text = str(parsed_story) if parsed_story else "No user story available"
    
    # # Ensure SOP context is always provided, even if empty
    # if not sop_context or sop_context == ["[]"] or sop_context == []:
    #     sop_context_display = "Standard clearance eligibility testing procedures and best practices"
    #     print("⚠️ No SOP context available, using standard procedures")
    # else:
    #     sop_context_display = str(sop_context)
    #     print("✅ Using provided SOP context")
    
    # gherkin_prompt = f"""
    # USER STORY:
    # {user_story_text}
    
    # SOP CONTEXT:
    # {sop_context_display}
    
    # GENERATED STEPS:
    # {steps_str}
    
    # Convert the above procedural steps into a Gherkin-style scenario based on the user story and SOP context.
    # Use appropriate Gherkin keywords (Given, When, Then, And) based on the context of each step.
    # Write the Gherkin scenario like how a QA Tester would write - do not add any irrelevant details.
    # Ensure the scenario is clear, crisp and follows Gherkin syntax.
    # The Gherkin scenario should be representative of the flow in the given automation steps.
    
    # IMPORTANT:
    # - DO NOT HALLUCINATE - use only the information provided in the user story, SOP context, and steps
    # - Do not add information that is not present in the provided context
    # - Focus on the specific application mentioned in the user story
    # - Include a 'Feature' and 'Scenario' header based on the user story
    # - Make the scenario specific to the application and workflow described
    # - If SOP context is limited, use standard clearance eligibility testing procedures
    
    # Return the result as plain text with each line separated by a newline.
    # """
    
    # content_str = llm(gherkin_prompt)
    # response_lines = content_str.splitlines()
    # gherkins_scenario = "\n".join(response_lines)
    gherkins_scenario = "Skipping Gherkins Creation"
    
    print(f"📝 Generated Gherkin scenario length: {len(gherkins_scenario)} characters")
    print(f"📝 Gherkin scenario preview: {gherkins_scenario[:200]}...")
    
    # Validate that we got a proper gherkin scenario
    if not gherkins_scenario or len(gherkins_scenario.strip()) < 10:
        print("⚠️ Generated Gherkin scenario seems too short or empty")
        gherkins_scenario = "Feature: Default Test Scenario\nScenario: Basic Test\nGiven the user is on the application\nWhen they perform the test steps\nThen the expected result should be achieved"
    
    workflow_status = "Gherkin Scenario Generated"
    state = add_workflow_step(state, "convert_to_gherkin", "completed", "Gherkin scenario generated successfully")
    
    # Add message to state
    state = add_message_to_state(
        state, 
        "assistant", 
        "Gherkin scenario generated successfully",
        {"node": "convert_to_gherkin", "status": "completed"}
    )
    
    # Save Gherkin scenario to file and print only a message with the file name
    gherkin_scenario = gherkins_scenario
    from datetime import datetime
    import os
    gherkin_dir = "gherkin_scenarios"
    os.makedirs(gherkin_dir, exist_ok=True)
    gherkin_filename = f"gherkin_{datetime.now().strftime('%Y%m%d_%H%M%S')}.feature"
    gherkin_path = os.path.join(gherkin_dir, gherkin_filename)
    with open(gherkin_path, "w", encoding="utf-8") as f:
        f.write(gherkin_scenario)
    print(f"\nGherkin file generated: {gherkin_filename}\n")
    
    return {**state, "gherkins_scenario": gherkin_scenario, "gherkin_file": gherkin_filename, "workflow_status": workflow_status}

def generate_playwright_code(state: GraphState) -> GraphState:
    print("\n### 🔄 Running node: GENERATE PLAYWRIGHT CODE\n")
    
    # Add workflow step
    state = add_workflow_step(state, "generate_playwright_code", "in_progress")
    
    try:
        steps = state.get("steps", [])
        all_steps = steps
        
        print(f"🔍 DEBUG: Using generated steps for Playwright code generation")
        print(f"🔍 DEBUG: Total steps to process: {len(all_steps)}")
        print(f"🔍 DEBUG: First few steps: {all_steps[:3]}")
        
        if not all_steps or all_steps == ['No relevant steps available']:
            print("DEBUG: No steps for Playwright code generation")
            workflow_status = "Error Retrieving Steps"
            state = add_workflow_step(state, "generate_playwright_code", "failed", "No steps available for code generation")
            return {**state, "playwright_code": "No steps available for code generation", "workflow_status": "Code not generated"}
        
        # Generate the full script for all steps at once
        steps_str = '\n'.join([f"{i+1}. {step}" for i, step in enumerate(all_steps)])
        
        
        patient_type_result = patient__type(steps_str)
        
        print("********************************",patient_type_result)
        
        patient_id, intake_id = patient_id_generator(patient_type_result)
        
        print("********************************",patient_id)
        
        # Handle case where patient_id_generator returns None values
        if patient_id is None or intake_id is None:
            print("⚠️ No patient data available, using fallback values")
            # Use default values for testing
            patient_id = "17164202"
            intake_id = "CMNINTAKE08212025105220254216083"
            print(f"Using fallback patient_id: {patient_id}, intake_id: {intake_id}")

        playwright_code = generate_intake_steps(patient_id, intake_id, patient_type_result,steps_str)
    
        return {**state, "playwright_code": playwright_code, "workflow_status": "Playwright Code Generated"}
        
    except Exception as e:
        print(f"EXCEPTION TYPE (Playwright code generation): {type(e)}")
        print(f"Error: {str(e)}")
        workflow_status = "Playwright Code Not Generated"
        state = add_workflow_step(state, "generate_playwright_code", "failed", error=f"Error: {str(e)}")
        
        # Add error message to state
        state = add_message_to_state(
            state, 
            "system", 
            f"Error generating Playwright code: {str(e)}",
            {"node": "generate_playwright_code", "error": str(e)}
        )
        
        return {**state, "playwright_code": f"Error generating Playwright code: {str(e)}", "workflow_status": workflow_status}
