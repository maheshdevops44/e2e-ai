"""
Message handling utilities for the workflow
"""

from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from .state import GraphState
from flask import jsonify

def add_message_to_state(
    state: GraphState, 
    role: str, 
    content: str, 
    metadata: Optional[Dict[str, Any]] = None
) -> GraphState:
    """Helper function to add messages to state"""
    current_messages = state.get("messages", []) or []
    
    if role == "human":
        new_message = HumanMessage(content=content)
    elif role == "assistant":
        new_message = AIMessage(content=content)
    elif role == "system":
        new_message = SystemMessage(content=content)
    else:
        new_message = HumanMessage(content=content)
    
    # Add metadata if provided
    if metadata:
        new_message.additional_kwargs = metadata
    
    updated_messages = current_messages + [new_message]
    return {**state, "messages": updated_messages}

def add_workflow_step(
    state: GraphState, 
    step_name: str, 
    status: str, 
    details: Optional[str] = None, 
    error: Optional[str] = None
) -> GraphState:
    """Add a workflow step to the state"""
    current_steps = state.get("workflow_steps", [])
    
    new_step = {
        "step_name": step_name,
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "details": details,
        "error": error
    }
    
    updated_steps = current_steps + [new_step]
    return {**state, "workflow_steps": updated_steps, "current_step": step_name}

def add_audit_entry(
    state: GraphState, 
    action: str, 
    details: str, 
    user: Optional[str] = None, 
    data: Optional[Dict[str, Any]] = None
) -> GraphState:
    """Add an audit entry to the state"""
    current_audit = state.get("audit_trail", [])
    
    new_entry = {
        "action": action,
        "timestamp": datetime.now().isoformat(),
        "user": user,
        "details": details,
        "data": data
    }
    
    updated_audit = current_audit + [new_entry]
    return {**state, "audit_trail": updated_audit}

class MessageUtils:
    """Utility class for message operations"""
    
    @staticmethod
    def get_messages_by_role(
        state: GraphState, 
        role: str
    ) -> List[Union[HumanMessage, AIMessage, SystemMessage]]:
        """Get all messages by role"""
        messages = state.get("messages", [])
        return [msg for msg in messages if msg.__class__.__name__.lower().startswith(role.lower())]
    
    @staticmethod
    def get_last_message(state: GraphState) -> Optional[Union[HumanMessage, AIMessage, SystemMessage]]:
        """Get the last message"""
        messages = state.get("messages", [])
        return messages[-1] if messages else None
    
    @staticmethod
    def get_message_count(state: GraphState) -> int:
        """Get total message count"""
        return len(state.get("messages", []))
    
    @staticmethod
    def clear_messages(state: GraphState) -> GraphState:
        """Clear all messages"""
        return {**state, "messages": []}
    
    @staticmethod
    def format_messages_for_display(state: GraphState) -> str:
        """Format messages for display"""
        messages = state.get("messages", [])
        formatted = []
        
        for i, msg in enumerate(messages):
            role = msg.__class__.__name__.replace("Message", "").lower()
            formatted.append(f"{i+1}. [{role.upper()}] {msg.content}")
        
        return "\n".join(formatted) 

def format_state_to_ai_output(state):
    # Find the latest AIMessage in messages
    ai_message = None
    for msg in reversed(state.get("messages", [])):
        if msg.__class__.__name__ == "AIMessage":
            ai_message = msg
            break

    # Fallback if not found
    if not ai_message:
        return {
            "role": "ai",
            "message": "",
            "metadata": {}
        }

    # Build metadata from state
    metadata = {
        "steps": state.get("steps") or state.get("parsed_story", {}).get("Test_Automation", []),
        "gherkin_steps": state.get("gherkins_scenario", ""),
        "test_case": state.get("Test_case", "")
    }

    return {
        "role": "ai",
        "message": ai_message.content,
        "metadata": metadata
    } 