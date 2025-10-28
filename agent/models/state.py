"""
State models for the workflow
"""

from typing import TypedDict, Optional, List, Dict, Any, Union
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

class GraphState(TypedDict):
    """Main state for the workflow graph"""
    RunID: str
    input: str  # Add input field for markdown reporting
    user_story: str
    parsed_story: dict
    missing_fields: Optional[List[str]]
    updated_info: Optional[dict]
    steps: Optional[List[str]]
    validated: Optional[bool]
    updated_steps: Optional[List[str]]
    gherkins_scenario: Optional[str]
    message: Optional[str]
    messages: Optional[List[Union[HumanMessage, AIMessage, SystemMessage]]]
    llm_suggestion: Optional[str]
    llm_feedback: Optional[str]
    accept: Optional[bool]
    edited_fields: Optional[dict]
    sop_context: List[str]
    workflow_status: str
    Test_case: Optional[str]
    last: Optional[Dict[str, Any]]
    
    # Human validation fields
    awaiting_human_input: Optional[bool]
    human_input: Optional[Dict[str, Any]]
    validation_step: Optional[str]
    
    # Playwright code generation fields
    playwright_code: Optional[str]

class WorkflowStep(TypedDict):
    """Individual workflow step tracking"""
    step_name: str
    status: str  # "completed", "failed", "in_progress"
    timestamp: str
    details: Optional[str]
    error: Optional[str]

class AuditEntry(TypedDict):
    """Audit trail entry"""
    action: str
    timestamp: str
    user: Optional[str]
    details: str
    data: Optional[Dict[str, Any]]

class Message(TypedDict):
    """Custom message structure"""
    role: str  # "user", "assistant", "system", "human"
    content: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] 