# LangGraph-Integrated FastAPI Workflow API

This API integrates LangGraph workflow nodes with FastAPI, providing a two-step workflow for test generation with human validation.

## Features

- **LangGraph Integration**: Uses the workflow builder from `workflow/builder.py`
- **State Management**: Maintains workflow state between requests using LangGraph checkpointing
- **Two-Step Workflow**: Initial parsing + human approval + test generation
- **Human Validation**: Requires human approval before generating test artifacts
- **Complete Test Generation**: Generates test cases, Gherkin scenarios, and Playwright scripts

## API Endpoints

### Health Check
```bash
GET /health
```

### Workflow Handler
```bash
POST /workflow
```

## Workflow Usage

### Step 1: Initial Request (Parse User Story)

Send a POST request with your user story:

```json
{
  "input": "As a QA Lead validating End to End Trend Biosimilar test scenarios for Direct Patient Fax Referral workflow, I need to simulate the end-to-end journey of a dummy fax referral being ingested to the point of completing Order Scheduling So that I can validate the complete workflow across the interconnected applications User Interfaces and Backend Databases from starting with fax ingestion, Intake, Clearance, RxProcessing, and completing CRM Order Scheduling. Inputs for Test Data (General): Channel: FAX, Therapy Type: HUMA, Order: New Referral, Patient Type: Direct. Inputs for Intake Application: Common Intake ID from file: <To be provided for TC>, Therapy Type: HUMA, Drug Name: HUMIRA 40 MG/0.4 ML PEN 2'S (NDC: 00074055402), Place Of Service: Clinic (Optional), Service Branch (SB Code): 555, Team: ARTH MHS (Auto-populated). Inputs for Clearance Application: Direct Patient Id from File:<To be provided for TC>, Place of Service ID: 12, BIN: 610144, PCN: D0TEST (0-Zero), Group Number: RTA, Cardholder ID: 555123123, Person Code: 01/ 001, Insurance Effective Date: TODAY'S DATE, Relationship: 1-self, Drug Checkbox: Should be checked/ enabled, Payer ID: 71504 (Select from Drop down suggestion), Co-Pay: P. Input for RxP Application: DAW Code: 0, Prescribed Drug: HUMIRA 40 MG/0.4 ML PEN 2'S (NDC: 00074055402), Common SIG: INJECT 40 MG (0.8 ML) UNDER THE SKIN EVERY 14 DAYS, Prescribed Quantity: 1, Day's Supply: 14, Doses: 1, Refills Authorized: 1."
}
```

**Response**: You'll receive a parsed user story with a `run_id` and `awaiting_human_input: true`.

### Step 2: Approval Request (Generate Test Artifacts)

Send a POST request with approval and the run_id:

```json
{
  "input": "approve",
  "run_id": "workflow_20241201_143022"
}
```

**Response**: You'll receive the generated test artifacts (test cases, Gherkin scenarios, Playwright scripts).

## Example Usage

### Using curl

```bash
# Step 1: Initial request
curl -X POST "http://localhost:8000/workflow" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "As a QA Lead validating End to End Trend Biosimilar test scenarios..."
  }'

# Step 2: Approval request (use run_id from Step 1 response)
curl -X POST "http://localhost:8000/workflow" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "approve",
    "run_id": "workflow_20241201_143022"
  }'
```

### Using Python

```python
import requests

# Step 1: Initial request
initial_response = requests.post("http://localhost:8000/workflow", json={
    "input": "As a QA Lead validating End to End Trend Biosimilar test scenarios..."
})

run_id = initial_response.json()["metadata"]["run_id"]

# Step 2: Approval request
approval_response = requests.post("http://localhost:8000/workflow", json={
    "input": "approve",
    "run_id": run_id
})

# Get test artifacts
test_artifacts = approval_response.json()["metadata"]
```

## Response Format

### Step 1 Response (Awaiting Human Input)
```json
{
  "role": "ai",
  "message": "## Parsed User Story\n\n**Objective:** ...\n**Applications Involved:** ...\n...",
  "metadata": {
    "run_id": "workflow_20241201_143022",
    "workflow_status": "Awaiting Human Feedback",
    "awaiting_human_input": true,
    "parsed_story": {...},
    "missing_fields": [...]
  }
}
```

### Step 2 Response (Test Generation Complete)
```json
{
  "role": "ai",
  "message": "Test Generation Completed Successfully",
  "metadata": {
    "run_id": "workflow_20241201_143022",
    "workflow_status": "Completed",
    "awaiting_human_input": false,
    "test_case": "...",
    "gherkin_scenario": "...",
    "playwright_script": "...",
    "steps": [...],
    "applications_covered": [...]
  },
  "markdown": "# Test Generation Report\n\n..."
}
```

## Running the API

1. **Start the FastAPI server**:
   ```bash
   cd agent/fastapi
   python fastapi_workflow_api.py
   ```

2. **Test the API**:
   ```bash
   cd agent
   python test_workflow_api.py
   ```

## Workflow Nodes

The API uses the following LangGraph nodes from `workflow/builder.py`:

1. **parse_user_story_llm**: Parses the user story into structured format
2. **check_missing_fields**: Identifies missing required fields
3. **fill_missing_with_llm**: Uses LLM to fill missing fields
4. **human_feedback**: Awaits human validation
5. **update_missing_fields**: Updates fields based on human feedback
6. **fetch_sop_agent**: Retrieves SOP context from OpenSearch
7. **generate_steps**: Generates automation steps
8. **generate_test_case**: Generates test cases
9. **convert_to_gherkin**: Converts to Gherkin scenarios
10. **generate_playwright_code**: Generates Playwright scripts

## State Management

The API uses LangGraph's checkpointing to maintain state between requests:
- Each workflow gets a unique `run_id`
- State is preserved between the initial request and approval request
- The workflow can be resumed at any point using the `run_id`

## Error Handling

- Invalid requests return 400 status with error details
- Workflow errors return 500 status with error details
- The API gracefully handles missing dependencies and provides fallbacks

