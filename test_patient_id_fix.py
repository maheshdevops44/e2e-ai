#!/usr/bin/env python3
"""
Test script to verify that patient_id is being passed correctly in intake_code.py
"""

import sys
import os
from pathlib import Path

# Add the agent directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent / "agent"))

from nodes.intake_code import generate_intake_steps

def test_patient_id_passing():
    """Test that patient_id is properly passed and used in the generated code"""
    
    # Test parameters
    test_patient_id = "TEST_PATIENT_12345"
    test_intake_id = "TEST_INTAKE_67890"
    test_patient_type = "Direct"
    test_steps = """
    1. Go to login page
    2. Enter Username and Password, then click Login
    3. Search for intake ID
    4. Fill patient details
    """
    
    print(f"Testing with patient_id: {test_patient_id}")
    print(f"Testing with intake_id: {test_intake_id}")
    print(f"Testing with patient_type: {test_patient_type}")
    
    try:
        # Generate the automation script
        generated_code = generate_intake_steps(
            patient_id=test_patient_id,
            intake_id=test_intake_id,
            patient__type=test_patient_type,
            steps=test_steps
        )
        
        # Check if the patient_id was properly replaced
        if f'PATIENT_ID = "{test_patient_id}"' in generated_code:
            print("✅ PASS: Patient ID was properly set in the generated code")
        else:
            print("❌ FAIL: Patient ID was not properly set in the generated code")
            print(f"Expected: PATIENT_ID = \"{test_patient_id}\"")
            print("Generated code snippet:")
            lines = generated_code.split('\n')
            for i, line in enumerate(lines):
                if 'PATIENT_ID' in line:
                    print(f"Line {i+1}: {line}")
        
        # Check if the intake_id was properly replaced
        if f'COMMON_INTAKE_ID = "{test_intake_id}"' in generated_code:
            print("✅ PASS: Intake ID was properly set in the generated code")
        else:
            print("❌ FAIL: Intake ID was not properly set in the generated code")
            print(f"Expected: COMMON_INTAKE_ID = \"{test_intake_id}\"")
            print("Generated code snippet:")
            lines = generated_code.split('\n')
            for i, line in enumerate(lines):
                if 'COMMON_INTAKE_ID' in line:
                    print(f"Line {i+1}: {line}")
        
        # Check if the patient_id is used in the fill operation
        if f'patient_id_input.fill(PATIENT_ID)' in generated_code:
            print("✅ PASS: Patient ID is used in the fill operation")
        else:
            print("❌ FAIL: Patient ID is not used in the fill operation")
        
        # Check if the print statement shows the actual patient_id value
        if f'print(f"[LOG] Filled Patient ID: {test_patient_id}")' in generated_code:
            print("✅ PASS: Print statement shows the actual patient_id value")
        else:
            print("❌ FAIL: Print statement does not show the actual patient_id value")
        
        # Check if the print statement shows the actual intake_id value
        if f'print(f"[LOG] Entered Common Intake ID: {test_intake_id}")' in generated_code:
            print("✅ PASS: Print statement shows the actual intake_id value")
        else:
            print("❌ FAIL: Print statement does not show the actual intake_id value")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing patient_id passing in intake_code.py...")
    success = test_patient_id_passing()
    
    if success:
        print("\n🎉 All tests passed! Patient ID is being passed correctly.")
    else:
        print("\n💥 Some tests failed. Please check the issues above.")
    
    sys.exit(0 if success else 1)
