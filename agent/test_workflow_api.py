#!/usr/bin/env python3
"""
Test script for the LangGraph-integrated FastAPI workflow
Demonstrates the two-step workflow: initial request and approval request
"""

import requests
import json
import time

# API endpoint
BASE_URL = "http://localhost:8000"

def test_workflow():
    """Test the complete workflow: initial request + approval"""
    
    # Step 1: Initial request with user story
    print("🔄 Step 1: Sending initial user story request...")
    
    user_story = """As a QA Lead validating End to End Trend Biosimilar test scenarios for Direct Patient Fax Referral workflow, I need to simulate the end-to-end journey of a dummy fax referral being ingested to the point of completing Order Scheduling So that I can validate the complete workflow across the interconnected applications User Interfaces and Backend Databases from starting with fax ingestion, Intake, Clearance, RxProcessing, and completing CRM Order Scheduling. Inputs for Test Data (General): Channel: FAX, Therapy Type: HUMA, Order: New Referral, Patient Type: Direct. Inputs for Intake Application: Common Intake ID from file: <To be provided for TC>, Therapy Type: HUMA, Drug Name: HUMIRA 40 MG/0.4 ML PEN 2'S (NDC: 00074055402), Place Of Service: Clinic (Optional), Service Branch (SB Code): 555, Team: ARTH MHS (Auto-populated). Inputs for Clearance Application: Direct Patient Id from File:<To be provided for TC>, Place of Service ID: 12, BIN: 610144, PCN: D0TEST (0-Zero), Group Number: RTA, Cardholder ID: 555123123, Person Code: 01/ 001, Insurance Effective Date: TODAY'S DATE, Relationship: 1-self, Drug Checkbox: Should be checked/ enabled, Payer ID: 71504 (Select from Drop down suggestion), Co-Pay: P. Input for RxP Application: DAW Code: 0, Prescribed Drug: HUMIRA 40 MG/0.4 ML PEN 2'S (NDC: 00074055402), Common SIG: INJECT 40 MG (0.8 ML) UNDER THE SKIN EVERY 14 DAYS, Prescribed Quantity: 1, Day's Supply: 14, Doses: 1, Refills Authorized: 1."""
    
    initial_request = {
        "input": user_story
    }
    
    try:
        response = requests.post(f"{BASE_URL}/workflow", json=initial_request)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Initial request successful!")
        print(f"  Run ID: {result.get('metadata', {}).get('run_id', 'unknown')}")
        print(f"  Awaiting human input: {result.get('metadata', {}).get('awaiting_human_input', False)}")
        print(f"  Workflow status: {result.get('metadata', {}).get('workflow_status', 'unknown')}")
        
        # Extract run_id for the approval request
        run_id = result.get('metadata', {}).get('run_id')
        
        if not run_id:
            print("❌ No run_id received in response")
            return
            
        print("\n" + "="*60)
        print("📋 PARSED USER STORY:")
        print("="*60)
        print(result.get('message', 'No message received'))
        print("="*60)
        
        # Step 2: Approval request
        print("\n🔄 Step 2: Sending approval request...")
        
        approval_request = {
            "input": "approve",
            "run_id": run_id
        }
        
        print(f"  Sending approval for run_id: {run_id}")
        
        response = requests.post(f"{BASE_URL}/workflow", json=approval_request)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Approval request successful!")
        print(f"  Run ID: {result.get('metadata', {}).get('run_id', 'unknown')}")
        print(f"  Awaiting human input: {result.get('metadata', {}).get('awaiting_human_input', False)}")
        print(f"  Workflow status: {result.get('metadata', {}).get('workflow_status', 'unknown')}")
        
        # Check if test artifacts were generated
        metadata = result.get('metadata', {})
        test_case = metadata.get('test_case')
        gherkin_scenario = metadata.get('gherkin_scenario')
        playwright_script = metadata.get('playwright_script')
        steps = metadata.get('steps', [])
        
        print(f"\n📊 TEST GENERATION RESULTS:")
        print(f"  Test case generated: {bool(test_case)}")
        print(f"  Gherkin scenario generated: {bool(gherkin_scenario)}")
        print(f"  Playwright script generated: {bool(playwright_script)}")
        print(f"  Steps generated: {len(steps)}")
        
        if test_case:
            print(f"\n📋 TEST CASE PREVIEW:")
            print(f"  Length: {len(str(test_case))} characters")
            print(f"  Preview: {str(test_case)[:200]}...")
            
        if gherkin_scenario:
            print(f"\n🥒 GHERKIN SCENARIO PREVIEW:")
            print(f"  Length: {len(gherkin_scenario)} characters")
            print(f"  Preview: {gherkin_scenario[:200]}...")
            
        if playwright_script:
            print(f"\n🎭 PLAYWRIGHT SCRIPT PREVIEW:")
            print(f"  Length: {len(playwright_script)} characters")
            print(f"  Preview: {playwright_script[:200]}...")
            
        if steps:
            print(f"\n📝 STEPS GENERATED:")
            for i, step in enumerate(steps[:5], 1):  # Show first 5 steps
                print(f"  {i}. {step}")
            if len(steps) > 5:
                print(f"  ... and {len(steps) - 5} more steps")
                
        # Show markdown report if available
        markdown = result.get('markdown')
        if markdown:
            print(f"\n📄 MARKDOWN REPORT:")
            print(f"  Length: {len(markdown)} characters")
            print(f"  Preview: {markdown[:300]}...")
        
        print("\n✅ Workflow test completed successfully!")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        result = response.json()
        print("✅ Health check successful!")
        print(f"  Status: {result.get('status')}")
        print(f"  LangGraph workflow: {result.get('langgraph_workflow')}")
        print(f"  Timestamp: {result.get('timestamp')}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing LangGraph-integrated FastAPI Workflow")
    print("="*60)
    
    # First check if the API is running
    if not test_health():
        print("\n❌ API is not running. Please start the FastAPI server first:")
        print("   cd agent/fastapi")
        print("   python fastapi_workflow_api.py")
        exit(1)
    
    print("\n" + "="*60)
    test_workflow()

