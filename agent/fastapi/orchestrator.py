#!/usr/bin/env python3
"""
Clean Orchestrator for RAG + Automation
Simplified orchestrator that uses the enhanced agent.py with Playwright integration.
"""

import asyncio
import os
import sys
import subprocess
import time
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))


async def main():
    """
    Simple orchestrator for automation execution with application-aware system.
    """
    print("🚀 Starting Application-Aware Automation Orchestrator")
    print("="*60)
    
    # Clear sessions before starting
    clear_sessions_before_run()
    print("="*60)
    
    # Multi-Application Workflow: Intake → Clearance → RxP
    instructions = """
    Application name: Clearance Automation
    Workflow: Clearance (Primary Application)
    
    # === APPLICATION: CLEARANCE ===
    # Url -> https://clearance-qa.express-scripts.com/spclr
    # Steps:
    # 1.  Navigate to the Clearance application URL
    # 2.  Enter valid username and Password
    # 3.  Click Login button
    # 4.  Wait for page to load and handle any popups
    # 5.  Click "Advanced Search" button
    # 6.  Enter Patient ID 16984688 in the RxHome ID field
    # 7.  Click Search button
    # 8.  Verify system shows list of cases with IDs like IE-xxxxxxx
    # 9.  Select the case with ID starting with "IE-" (Insurance Entry)
    # 10. Click on the "IE-" Case (status should be 'New-Eligibility not found')
    # 11. Verify user lands on Eligibility tab with Payer information on right side
    # 12. In Payer section, select Place of Service ID: 12 (Home) from dropdown
    # 13. Under Payer Information, enter BIN: 610144, PCN: D0TEST, Group Number: RTA
    # 14. Click Search button
    # 15. In Policy Information section, enter Cardholder ID: 555123123, Person Code: 001, Insurance Effective Date: Today's Date, Insurance Expiration Date: Tomorrow's Date.
    # 16. In Policyholder Information section, enter in Relationship dropdown 1-Self.
    # 17. Click Save button
    # 18. Click Next button
    # 19. Click on Co-Pay tab
    # 20. Under Assign Co-Pay, select P
    # 21. Click Finish button
    # 22. Wait 5 seconds before proceeding to next application
    
    # === PRESCRIPTION WORKFLOW ===
    # After Clearance completion, continue with prescription workflow:
    # 23. Click Begin button in the Order Entry assignment row
    # 24. Click Link Image in Viewer
    # 25. Click DAW Code dropdown and select first option
    # 26. Click Search after DAW selection
    # 27. Click Common SIG button
    # 28. Click SIG dropdown and select: INJECT 40 MG (0.4 ML) UNDER THE SKIN EVERY 2 WEEKS
    # 29. Enter Qty = 1, Days Supply = 14, Doses = 1, Refills = 1
    # 30. Click Apply Rules
    # 31. Fill Qty and Days Supply with same value after Apply Rules
    # 32. Fill Doses and Refills with same value
    """
    
    print("📋 Instructions:")
    print(instructions)
    print("="*60)
    
    try:
        # Simple application detection - prioritize Clearance
        if "Clearance" in instructions:
            print("🎯 Detected Application: Clearance")
        elif "Intake" in instructions:
            print("🎯 Detected Application: Intake")
        elif "RxP" in instructions:
            print("🎯 Detected Application: RxP")
        else:
            print("⚠️ No specific application detected, using generic approach")
        
        # Extract basic data
        custom_data = {}
        if "CMNINTAKE" in instructions:
            import re
            intake_match = re.search(r'CMNINTAKE[0-9]+', instructions)
            if intake_match:
                custom_data['intake_id'] = intake_match.group(0)
        if "Patient ID:" in instructions:
            import re
            patient_match = re.search(r'Patient ID:([0-9]+)', instructions)
            if patient_match:
                custom_data['patient_id'] = patient_match.group(1)
        
        if custom_data:
            print(f"📋 Extracted Custom Data: {custom_data}")
        
        print("\n✅ Instructions processed successfully!")
        print("📋 Summary:")
        print("  - Instructions extracted and processed")
        if custom_data:
            print(f"  - Custom data extracted: {list(custom_data.keys())}")
        print("  - Ready to run: python run_step.py")
        
        print("\n✅ Orchestration completed successfully!")
        
    except Exception as e:
        print(f"❌ Orchestration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 