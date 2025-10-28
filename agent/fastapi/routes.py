"""
API routes for the workflow
"""

from flask import Flask, request, jsonify
from typing import Dict, Any
from flask import jsonify
import uuid
from datetime import datetime
from workflow.builder import build_workflow
from models.state import GraphState
from config.settings import settings
from models.messages import format_state_to_ai_output
import json

app = Flask(__name__)

# Global workflow instance
workflow = None

def get_workflow():
    """Get or create workflow instance"""
    global workflow
    if workflow is None:
        workflow = build_workflow()
    return workflow

def get_next_actions(validation_step: str) -> Dict[str, Any]:
    """Get available actions for the current validation step"""
    if validation_step == "missing_fields":
        return {
            "approve": {
                "description": "Accept LLM suggestions for missing fields",
                "input_format": {"action": "approve"}
            },
            "update": {
                "description": "Update missing fields with custom values",
                "input_format": {
                    "action": "update",
                    "fields": {
                        "Objective": "Your objective here",
                        "Test Summary": "Your test summary here",
                        "Acceptance Criteria": "Your acceptance criteria here",
                        "Manual_Steps": "Your manual steps here",
                        "Applications Involved": "Your applications here"
                    }
                }
            }
        }
    elif validation_step == "steps_validation":
        return {
            "approve": {
                "description": "Accept the generated steps",
                "input_format": {"action": "approve"}
            },
            "edit": {
                "description": "Edit the generated steps",
                "input_format": {
                    "action": "edit",
                    "steps": [
                        "Step 1: Your custom step",
                        "Step 2: Another custom step"
                    ]
                }
            }
        }
    else:
        return {}

@app.route("/workflow", methods=["POST"])
def handle_workflow():
    """
    Single endpoint to handle workflow operations:
    - Start new workflow
    - Continue workflow with human input
    - Get workflow status
    """
    data = request.get_json()
    action = data.get("action")  # "start", "continue", "status"
    
    if action == "start":
        result = print(start_workflow(data))
        print(result)
        return start_workflow(data)
    elif action == "continue":
        return continue_workflow(data)
    elif action == "status":
        return get_workflow_status(data)
    else:
        return jsonify({"error": "Invalid action. Use 'start', 'continue', or 'status'"}), 400

def start_workflow(data: Dict[str, Any]):
    """Start a new workflow"""
    user_story = data.get("user_story")
    if not user_story:
        return jsonify({"error": "user_story is required"}), 400
    
    # Create initial state
    initial_state = {
        "RunID": f"session-{uuid.uuid4()}",
        "user_story": user_story,
        "awaiting_human_input": False,
        "workflow_status": "started",
        "timestamp": datetime.now().isoformat(),
        "messages": [],
        "workflow_steps": [],
        "audit_trail": []
    }
    
    try:
        workflow_instance = get_workflow()
        result = workflow_instance.invoke(initial_state)
        
        # Check if workflow is waiting for human input
        if result.get("awaiting_human_input"):
            output = format_state_to_ai_output(result)
            print(output)
            print(json.dumps(output, indent=2))
            try:
                return jsonify(output)
            except Exception as e:
                print("Serialization error:", e)
                return jsonify({"error": str(e)}), 500
            # return jsonify({
            #     "status": "awaiting_human_input",
            #     "run_id": result["RunID"],
            #     "message": result.get("message"),
            #     "validation_step": result.get("validation_step"),
            #     "current_data": {
            #         "parsed_story": result.get("parsed_story"),
            #         "missing_fields": result.get("missing_fields"),
            #         "llm_suggestion": result.get("llm_suggestion"),
            #         "steps": result.get("steps"),
            #         "llm_feedback": result.get("llm_feedback")
            #     },
            #     "next_actions": get_next_actions(result.get("validation_step"))
            # })
        else:
            return jsonify({
                "status": "completed",
                "run_id": result["RunID"],
                "result": {
                    "gherkins_scenario": result.get("gherkins_scenario"),
                    "Test_case": result.get("Test_case"),
                    "workflow_status": result.get("workflow_status")
                }
            })
            
    except Exception as e:
        return jsonify({"error": f"Workflow failed: {str(e)}"}), 500

def continue_workflow(data: Dict[str, Any]):
    """Continue workflow with human input"""
    run_id = data.get("run_id")
    human_input = data.get("human_input")
    
    if not run_id:
        return jsonify({"error": "run_id is required"}), 400
    if not human_input:
        return jsonify({"error": "human_input is required"}), 400
    
    try:
        workflow_instance = get_workflow()
        
        # Get current state from checkpoint
        current_state = workflow_instance.get_state(run_id)
        if not current_state:
            return jsonify({"error": f"No workflow found with run_id: {run_id}"}), 404
        
        # Update state with human input
        updated_state = {**current_state, "human_input": human_input}
        
        # Continue workflow
        result = workflow_instance.invoke(updated_state, config={"configurable": {"thread_id": run_id}})
        
        # Check if workflow is waiting for more human input
        if result.get("awaiting_human_input"):
            output = format_state_to_ai_output(result)
            print(output)
            print(json.dumps(output, indent=2))
            try:
                return jsonify(output)
            except Exception as e:
                print("Serialization error:", e)
                return jsonify({"error": str(e)}), 500
            # return jsonify({
            #     "status": "awaiting_human_input",
            #     "run_id": run_id,
            #     "message": result.get("message"),
            #     "validation_step": result.get("validation_step"),
            #     "current_data": {
            #         "parsed_story": result.get("parsed_story"),
            #         "missing_fields": result.get("missing_fields"),
            #         "llm_suggestion": result.get("llm_suggestion"),
            #         "steps": result.get("steps"),
            #         "llm_feedback": result.get("llm_feedback")
            #     },
            #     "next_actions": get_next_actions(result.get("validation_step"))
            # })
        else:
            return jsonify({
                "status": "completed",
                "run_id": run_id,
                "result": {
                    "gherkins_scenario": result.get("gherkins_scenario"),
                    "Test_case": result.get("Test_case"),
                    "workflow_status": result.get("workflow_status")
                }
            })
            
    except Exception as e:
        return jsonify({"error": f"Workflow continuation failed: {str(e)}"}), 500

def get_workflow_status(data: Dict[str, Any]):
    """Get current workflow status"""
    run_id = data.get("run_id")
    
    if not run_id:
        return jsonify({"error": "run_id is required"}), 400
    
    try:
        workflow_instance = get_workflow()
        current_state = workflow_instance.get_state(run_id)
        
        if not current_state:
            return jsonify({"error": f"No workflow found with run_id: {run_id}"}), 404
        
        return jsonify({
            "run_id": run_id,
            "workflow_status": current_state.get("workflow_status"),
            "awaiting_human_input": current_state.get("awaiting_human_input"),
            "validation_step": current_state.get("validation_step"),
            "message": current_state.get("message"),
            "timestamp": current_state.get("timestamp"),
            "current_data": {
                "parsed_story": current_state.get("parsed_story"),
                "missing_fields": current_state.get("missing_fields"),
                "llm_suggestion": current_state.get("llm_suggestion"),
                "steps": current_state.get("steps"),
                "llm_feedback": current_state.get("llm_feedback")
            },
            "workflow_steps": current_state.get("workflow_steps", []),
            "audit_trail": current_state.get("audit_trail", [])
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get status: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(
        host=settings.API_HOST,
        port=settings.API_PORT,
        debug=settings.API_DEBUG
    ) 