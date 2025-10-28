"""
Workflow graph builder
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from models.state import GraphState

# Import all nodes
from nodes.parsing_nodes import parse_user_story_llm, check_missing_fields, fill_missing_with_llm
from nodes.validation_nodes import human_feedback, update_missing_fields
from nodes.sop_nodes import fetch_sop_agent
from nodes.generation_nodes import generate_steps_llm, generate_test_case, convert_to_gherkin_llm, generate_playwright_code

def build_workflow():
    """Build the complete workflow graph"""
    builder = StateGraph(GraphState)
    
    # Set entry point
    builder.set_entry_point("parse_user_story")
    
    # Add all nodes
    builder.add_node("parse_user_story", parse_user_story_llm)
    builder.add_node("check_missing_fields", check_missing_fields)
    builder.add_node("fill_missing_with_llm", fill_missing_with_llm)
    builder.add_node("human_input_missing_fields", human_feedback)
    builder.add_node("update_missing_fields", update_missing_fields)
    builder.add_node("fetch_sop_agent", fetch_sop_agent)
    builder.add_node("generate_steps", generate_steps_llm)
    builder.add_node("generate_test_case", generate_test_case)
    builder.add_node("convert_to_gherkin", convert_to_gherkin_llm)
    builder.add_node("generate_playwright_code", generate_playwright_code)
    
    # Add edges
    builder.add_edge("parse_user_story", "check_missing_fields")
    
    # Add conditional edge for missing fields check
    builder.add_conditional_edges(
        "check_missing_fields",
        has_missing_fields,
        {
            "missing": "fill_missing_with_llm",
            "not_missing": "human_input_missing_fields"
        }
    )
    
    # After LLM suggests missing fields, go to human validation
    builder.add_edge("fill_missing_with_llm", "human_input_missing_fields")
    
    # After human validation, check if we need to pause for human input
    builder.add_conditional_edges(
        "human_input_missing_fields",
        check_awaiting_human_input,
        {
            "awaiting": END,  # Pause workflow
            "continue": "update_missing_fields"
        }
    )
    
    # After updating missing fields, continue to SOP
    builder.add_edge("update_missing_fields", "fetch_sop_agent")
    
    # Continue with existing flow
    builder.add_edge("fetch_sop_agent", "generate_steps")
    # After generate_steps, go directly to generate_test_case (skip step validation)
    builder.add_edge("generate_steps", "generate_test_case")
    builder.add_edge("generate_test_case", "convert_to_gherkin")
    builder.add_edge("convert_to_gherkin", "generate_playwright_code")
    builder.add_edge("generate_playwright_code", END)
    
    # Compile with checkpointing
    saver = InMemorySaver()
    workflow = builder.compile(checkpointer=saver)
    return workflow

def has_missing_fields(state: GraphState) -> str:
    """Returns 'missing' if there are missing fields, otherwise 'not_missing'"""
    if state.get("missing_fields"):
        return "missing"
    else:
        return "not_missing"

def check_awaiting_human_input(state: GraphState) -> str:
    """Returns 'awaiting' if workflow should pause for human input, otherwise 'continue'"""
    if state.get("awaiting_human_input", False):
        return "awaiting"
    else:
        return "continue"

def human_feedback_status(state: GraphState) -> str:
    """Returns status for human feedback routing"""
    if state.get("workflow_status") == "Awaiting QA team input":
        return "Awaiting QA team input"
    else:
        return "Human Input Received"

def update_fields(state: GraphState) -> bool:
    """Returns True if workflow_status is 'Update Fields', otherwise False"""
    return state.get("workflow_status") == "Update Fields" 