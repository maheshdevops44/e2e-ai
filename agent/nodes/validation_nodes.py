"""
Human validation nodes for the workflow
"""

import json
from datetime import datetime
from typing import Dict, Any
from models.state import GraphState
from models.messages import add_message_to_state, add_workflow_step, add_audit_entry
from config.llm_config import llm


def human_feedback(state: GraphState) -> GraphState:
    """Node that awaits human feedback"""
    print(f"### 🔄 Running node: `HUMAN FEEDBACK`")
    print(">>> Entered human_feedback node")
    
    # Add workflow step
    state = add_workflow_step(state, "human_feedback", "in_progress")
    
    human_input = state.get("human_input")
    print("human_input value:", human_input)
    # Treat empty string or empty dict as no input
    if not human_input or human_input == "" or human_input == {}:
        print(">>> Awaiting human input, returning interruption to client")
        # Show current parsed story and missing fields
        parsed_story = state.get("parsed_story", {})
        missing_fields = state.get("missing_fields", [])
        
        # Create a formatted message showing the parsed story
        story_summary = ""
        if parsed_story:
            story_summary = "📋 Parsed User Story:\n"
            if 'Objective' in parsed_story and parsed_story['Objective']:
                story_summary += f"• Objective: {parsed_story['Objective']}\n"
            if 'Test Summary' in parsed_story and parsed_story['Test Summary']:
                story_summary += f"• Test Summary: {parsed_story['Test Summary']}\n"
            if 'Acceptance Criteria' in parsed_story and parsed_story['Acceptance Criteria']:
                story_summary += "• Acceptance Criteria:\n"
                for i, crit in enumerate(parsed_story['Acceptance Criteria'], 1):
                    story_summary += f"  {i}. {crit}\n"
            if 'Applications Involved' in parsed_story and parsed_story['Applications Involved']:
                story_summary += f"• Applications Involved: {', '.join(parsed_story['Applications Involved'])}\n"
            if 'Manual_Steps' in parsed_story and parsed_story['Manual_Steps']:
                story_summary += "• Manual Steps:\n"
                for i, step in enumerate(parsed_story['Manual_Steps'], 1):
                    story_summary += f"  {i}. {step}\n"
            if 'Test_Automation' in parsed_story and parsed_story['Test_Automation']:
                story_summary += "• Test Automation Steps:\n"
                for i, step in enumerate(parsed_story['Test_Automation'], 1):
                    story_summary += f"  {i}. {step}\n"
        missing_fields = state.get("missing_fields", [])
        feedback_message = f"{story_summary}\n\n Please review the parsed user story above and provide feedback."
        
        # Add message to state indicating human feedback is needed
        state = add_message_to_state(
            state, 
            "assistant", 
            feedback_message,
            {"node": "human_feedback", "status": "awaiting_input"}
        )
        
        state = add_workflow_step(state, "human_feedback", "completed", "Awaiting human feedback")
        
        # Set flag to indicate human input is needed
        return {
            **state,
            "awaiting_human_input": True,
            "workflow_status": "Awaiting Human Feedback"
        }
    
    # Handle both string and dict types for human_input
    if isinstance(human_input, str):
        human_input = {"feedback": human_input}
    parsed_story = state.get("parsed_story", {})

    if human_input:
        # Compose a prompt for the LLM
        prompt = f"""
        You are a QA assistant. Here is the current parsed user story:
        {parsed_story}

        The following feedback was received from a human reviewer:
        '''{human_input}'''

        - If the feedback is an approval, return the story as is.
        - If the feedback suggests changes, update the story fields as described in the feedback.
        - Return the updated user story as a JSON object.
        - If the feedback is ambiguous, do your best to interpret and update the story.

        Only return the JSON object, no explanations.
        """
        updated_story = llm(prompt)
        try:
            import json
            updated_story_json = json.loads(updated_story)
        except Exception:
            updated_story_json = parsed_story  # fallback if LLM output is not valid JSON

        state["parsed_story"] = updated_story_json
        state = add_workflow_step(state, "human_feedback", "completed", "LLM processed free text human feedback")
        # Clear human_input so the workflow proceeds
        if "human_input" in state:
            del state["human_input"]
        return {
            **state,
            "awaiting_human_input": False
        }
    
    print(">>> Awaiting human input, returning interruption to client")
    # Show current parsed story and missing fields
    parsed_story = state.get("parsed_story", {})
    missing_fields = state.get("missing_fields", [])
    
    # Create a formatted message showing the parsed story
    story_summary = ""
    if parsed_story:
        story_summary = " Parsed User Story:\n"
        if 'Objective' in parsed_story and parsed_story['Objective']:
            story_summary += f"• Objective: {parsed_story['Objective']}\n"
        if 'Test Summary' in parsed_story and parsed_story['Test Summary']:
            story_summary += f"• Test Summary: {parsed_story['Test Summary']}\n"
        if 'Acceptance Criteria' in parsed_story and parsed_story['Acceptance Criteria']:
            story_summary += "• Acceptance Criteria:\n"
            for i, crit in enumerate(parsed_story['Acceptance Criteria'], 1):
                story_summary += f"  {i}. {crit}\n"
        if 'Applications Involved' in parsed_story and parsed_story['Applications Involved']:
            story_summary += f"• Applications Involved: {', '.join(parsed_story['Applications Involved'])}\n"
        if 'Manual_Steps' in parsed_story and parsed_story['Manual_Steps']:
            story_summary += "• Manual Steps:\n"
            for i, step in enumerate(parsed_story['Manual_Steps'], 1):
                story_summary += f"  {i}. {step}\n"
        if 'Test_Automation' in parsed_story and parsed_story['Test_Automation']:
            story_summary += "• Test Automation Steps:\n"
            for i, step in enumerate(parsed_story['Test_Automation'], 1):
                story_summary += f"  {i}. {step}\n"
    
    feedback_message = f"{story_summary} \n\nPlease review the parsed user story above and provide feedback."
    
    # Add message to state indicating human feedback is needed
    state = add_message_to_state(
        state, 
        "assistant", 
        feedback_message,
        {"node": "human_feedback", "status": "awaiting_input"}
    )
    
    state = add_workflow_step(state, "human_feedback", "completed", "Awaiting human feedback")
    
    # Set flag to indicate human input is needed
    return {
        **state,
        "awaiting_human_input": True,
        "workflow_status": "Awaiting Human Feedback"
    }

def update_missing_fields(state: GraphState) -> GraphState:
    """Process human input for missing fields"""
    print(f"### 🚦 Running node: `UPDATE MISSING FIELDS`")
    
    # Add workflow step
    state = add_workflow_step(state, "update_missing_fields", "in_progress")
    
    workflow_status = state.get("workflow_status")
    human_input = state.get("human_input")
    # Handle both string and dict types for human_input
    if isinstance(human_input, str):
        human_input = {"feedback": human_input}
    if human_input:
        action = human_input.get("action")
        if action == "approve":
            # Add approval message
            state = add_audit_entry(
                state, 
                "human_approval", 
                "QA team approved LLM suggestions",
                user="qa_team"
            )
            state = add_workflow_step(state, "update_missing_fields", "completed", "Human approved suggestions")
            return {**state, "workflow_status": "Human Input Received", "missing_fields": []}
        elif action == "update":
            user_story_fields = state.get("parsed_story", {})
            updated_fields = human_input.get("fields", {})
            merged_fields = {**user_story_fields, **updated_fields}
            # Add update message
            state = add_audit_entry(
                state, 
                "human_update", 
                f"QA team updated fields: {list(updated_fields.keys())}",
                user="qa_team",
                data=updated_fields
            )
            state = add_workflow_step(state, "update_missing_fields", "completed", "Human updated fields")
            return {**state, "workflow_status": "Updated Fields", "missing_fields": [], "parsed_story": merged_fields}
    
    print(f"### 🚦 Output :")
    print(print_readable_json(state.get("parsed_story")))
    state = add_workflow_step(state, "update_missing_fields", "completed", "No updates needed")
    return state

def validate_steps_with_llm(state: GraphState) -> GraphState:
    """Validate generated steps using LLM"""
    print(f"### 🚦 Running node: `VALIDATE STEPS`")
    
    # Add workflow step
    state = add_workflow_step(state, "validate_steps", "in_progress")
    
    from config.llm_config import llm
    
    prompt = """Review the steps {steps} and provide feedback"""
    validate_prompt = prompt.format(steps=state["steps"])
    content_str = llm(validate_prompt)
    
    # Add message to state
    state = add_message_to_state(
        state, 
        "assistant", 
        content_str,
        {"node": "validate_steps", "action": "validation"}
    )
    
    state = add_workflow_step(state, "validate_steps", "completed", "Steps validated by LLM")
    
    return {
        **state,
        "validated": False,
        "llm_feedback": content_str,
        "message": f"LLM feedback: {content_str}\nDo you accept these steps or want to edit?",
        "workflow_status": "Awaiting Validation from QA Team",
        "validation_step": "steps_validation"
    }

def human_validation_node(state: GraphState) -> GraphState:
    """Generic human validation node"""
    print(f"### 🚦 AWAITING HUMAN VALIDATION: {state.get('validation_step')}")
    
    # Add workflow step
    state = add_workflow_step(state, "human_validation", "in_progress")
    
    # Check if human input is already available
    human_input = state.get("human_input")
    if human_input:
        print(f"### 🚦 Human input already available: {human_input}")
        return {
            **state,
            "awaiting_human_input": False,
            "workflow_status": "human_input_available"
        }
    
    # If no human input available, provide default approval
    print(f"### 🚦 No human input available, providing default approval")
    default_human_input = {"action": "approve"}
    
    # Add message to state
    state = add_message_to_state(
        state, 
        "system", 
        f"Auto-approved with default values for: {state.get('validation_step')}",
        {"node": "human_validation", "validation_step": state.get('validation_step')}
    )
    
    return {
        **state,
        "human_input": default_human_input,
        "awaiting_human_input": False,
        "workflow_status": "auto_approved"
    }

def process_human_input(state: GraphState) -> GraphState:
    """Process human input and continue workflow"""
    print(f"### 🚦 Processing human input")
    
    # Add workflow step
    state = add_workflow_step(state, "process_human_input", "in_progress")
    
    human_input = state.get("human_input", {})
    validation_step = state.get("validation_step")
    
    if validation_step == "missing_fields":
        if human_input.get("action") == "approve":
            # PATCH: Fill missing fields with a default value (e.g., "N/A" or ["No manual steps required"])
            missing_fields = state.get("missing_fields", [])
            parsed_story = dict(state.get("parsed_story", {}))
            for field in missing_fields:
                # You can customize this logic as needed
                if isinstance(parsed_story.get(field), list):
                    parsed_story[field] = ["No manual steps required"]
                else:
                    parsed_story[field] = "N/A"
            state = add_audit_entry(
                state, 
                "human_approval", 
                "QA team approved missing field suggestions",
                user="qa_team"
            )
            state = add_workflow_step(state, "process_human_input", "completed", "Human approved missing fields")
            return {
                **state,
                "parsed_story": parsed_story,
                "awaiting_human_input": False,
                "workflow_status": "human_approved",
                "validation_step": None,
                "missing_fields": []
            }
        elif human_input.get("action") == "update":
            # Update the parsed story with human corrections
            updated_fields = human_input.get("fields", {})
            updated_story = {**state["parsed_story"], **updated_fields}
            
            state = add_audit_entry(
                state, 
                "human_update", 
                f"QA team updated missing fields: {list(updated_fields.keys())}",
                user="qa_team",
                data=updated_fields
            )
            
            state = add_workflow_step(state, "process_human_input", "completed", "Human updated missing fields")
            # PATCH: clear missing_fields and update parsed_story
            return {
                **state,
                "parsed_story": updated_story,
                "awaiting_human_input": False,
                "workflow_status": "human_updated",
                "validation_step": None,
                "missing_fields": []
            }
    elif validation_step == "steps_validation":
        if human_input.get("action") == "approve":
            state = add_audit_entry(
                state, 
                "human_approval", 
                "QA team approved generated steps",
                user="qa_team"
            )
            state = add_workflow_step(state, "process_human_input", "completed", "Human approved steps")
            return {
                **state,
                "awaiting_human_input": False,
                "workflow_status": "steps_approved",
                "validation_step": None
            }
        elif human_input.get("action") == "edit":
            updated_steps = human_input.get("steps", [])
            
            state = add_audit_entry(
                state, 
                "human_update", 
                f"QA team updated steps: {len(updated_steps)} steps modified",
                user="qa_team",
                data={"updated_steps": updated_steps}
            )
            
            state = add_workflow_step(state, "process_human_input", "completed", "Human updated steps")
            return {
                **state,
                "steps": updated_steps,
                "awaiting_human_input": False,
                "workflow_status": "steps_updated",
                "validation_step": None
            }
    state = add_workflow_step(state, "process_human_input", "completed", "No action taken")
    return state

def print_readable_json(data):
    """Helper function to print JSON data"""
    try:
        if isinstance(data, str):
            data = json.loads(data)
        print(json.dumps(data, indent=2))
    except Exception:
        print(data) 