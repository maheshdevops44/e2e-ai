import pandas as pd
import os

# Handle file path for both local and Docker environments
direct_patient_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'Direct Patient.xlsx')
integrated_patient_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'Integrated Patient.xlsx')
reject_patient_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'Direct Patient for ref reject.xlsx')

try:
    direct_patient_data = pd.read_excel(direct_patient_file)
    integrated_patient_data = pd.read_excel(integrated_patient_file)
    reject_patient_data = pd.read_excel(reject_patient_file)
except FileNotFoundError:
    print(f"Error: Excel file not found at {direct_patient_file}")
    raise
except ImportError as e:
    print(f"Error: Missing required dependency for Excel support. Please install openpyxl: {e}")
    raise

def patient_id_generator(type='Direct'):
    if type == 'Direct':
        data = direct_patient_data
        unused_data = data[data['comment']!='used']
        
        # # Check if there are any unused patient IDs available
        # if unused_data.empty:
        #     print("⚠️ No unused patient IDs available. Using fallback values.")
        #     # Reset all comments to unused to allow reuse
        #     data['comment'] = data['comment'].replace('used', '')
        #     unused_data = data[data['comment']!='used']
            
        # If still empty, use the first available patient ID
        if unused_data.empty:
            print("⚠️ No patient data available. Using first available patient ID.")
            # patient_id = data['Patient ID'].iloc[0]
            # intake_id = data[data['Patient ID']==patient_id]['Document Id'].iloc[0]
            # return patient_id, intake_id
        
        # Sample from available unused data
        patient_id = unused_data['Patient ID'].sample(n=1).iloc[0]
        intake_id = unused_data[unused_data['Patient ID']==patient_id]['Document Id'].iloc[0]
        print(patient_id)
        print(intake_id)
        data.loc[data['Patient ID']==patient_id, 'comment'] = 'used'
        try:
            data.to_excel(direct_patient_file, index=False, sheet_name='sheet_1')
        except PermissionError:
            print(f"Warning: Could not write to {direct_patient_file}. Changes not saved.")
        except Exception as e:
            print(f"Error saving Excel file: {e}")
    elif type == 'Integrated':
        data = integrated_patient_data
        unused_data = data[data['comment']!='used']
        
        # # Check if there are any unused patient IDs available
        # if unused_data.empty:
        #     print("⚠️ No unused patient IDs available for Integrated. Using fallback values.")
        #     # Reset all comments to unused to allow reuse
        #     data['comment'] = data['comment'].replace('used', '')
        #     unused_data = data[data['comment']!='used']
            
        # If still empty, use the first available patient ID
        if unused_data.empty:
            print("⚠️ No patient data available for Integrated.")
            # patient_id = data['Patient ID'].iloc[0]
            # intake_id = data[data['Patient ID']==patient_id]['Document Id'].iloc[0]
            # return patient_id, intake_id
        
        # Sample from available unused data
        patient_id = unused_data['Patient ID'].sample(n=1).iloc[0]
        intake_id = unused_data[unused_data['Patient ID']==patient_id]['Document Id'].iloc[0]
        print(patient_id)
        print(intake_id)
        data.loc[data['Patient ID']==patient_id, 'comment'] = 'used'
        try:
            data.to_excel(integrated_patient_file, index=False, sheet_name='sheet_1')
        except PermissionError:
            print(f"Warning: Could not write to {integrated_patient_file}. Changes not saved.")
        except Exception as e:
            print(f"Error saving Excel file: {e}")
    else:
        data = reject_patient_data
        unused_data = data[data['comment']!='used']
        
        # # Check if there are any unused patient IDs available
        # if unused_data.empty:
        #     print("⚠️ No unused patient IDs available for Reject. Using fallback values.")
        #     # Reset all comments to unused to allow reuse
        #     data['comment'] = data['comment'].replace('used', '')
        #     unused_data = data[data['comment']!='used']
            
        # If still empty, use the first available patient ID
        if unused_data.empty:
            print("⚠️ No patient data available for Reject.")
            # patient_id = data['Patient ID'].iloc[0]
            # intake_id = data[data['Patient ID']==patient_id]['Document Id'].iloc[0]
            # return patient_id, intake_id
        
        # Sample from available unused data
        patient_id = unused_data['Patient ID'].sample(n=1).iloc[0]
        intake_id = unused_data[unused_data['Patient ID']==patient_id]['Document Id'].iloc[0]
        print(patient_id)
        print(intake_id)
        data.loc[data['Patient ID']==patient_id, 'comment'] = 'used'
        try:
            data.to_excel(reject_patient_file, index=False, sheet_name='sheet_1')
        except PermissionError:
            print(f"Warning: Could not write to {reject_patient_file}. Changes not saved.")
        except Exception as e:
            print(f"Error saving Excel file: {e}")

        
    return patient_id, intake_id
