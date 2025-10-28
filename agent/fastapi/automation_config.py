"""
Automation Configuration File
This file contains all selector strategies and can be easily updated without changing the main code.
"""

from dotenv import load_dotenv
import os
from pathlib import Path

dotenv_path = Path(__file__).resolve().parents[1]/"config"/".env"
load_dotenv(dotenv_path)


# Application URLs
APPLICATION_URLS = {
    "Clearance": "https://clearance-qa.express-scripts.com/spclr",
    "Intake": "https://spcia-qa.express-scripts.com/spcia",
    "RxP": "https://sprxp-qa.express-scripts.com/sprxp/",
    "Trend": "https://trend-qa.express-scripts.com/trend/app/Trend/SVFxeQ1KxRV42HP7Gy_AIT3R1dTRC6gM*/!STANDAR",
    "CRM": "https://crm-qa.express-scripts.com/crm/app/CRM/SVFxeQ1KxRV42HP7Gy_AIT3R1dTRC6gM*/!STANDAR"
}

# Default Login Credentials (can be overridden in instructions)
DEFAULT_USERNAME = os.getenv(LAN_ID)
DEFAULT_PASSWORD = os.getenv(LAN_PASSWORD)

# Legacy support (for backward compatibility)
CLEARANCE_URL = APPLICATION_URLS["Clearance"]
INTAKE_URL = APPLICATION_URLS["Intake"]
CLEARANCE_USERNAME = DEFAULT_USERNAME
CLEARANCE_PASSWORD = DEFAULT_PASSWORD
USERNAME = DEFAULT_USERNAME
PASSWORD = DEFAULT_PASSWORD

# Test Data
PATIENT_ID = "17045256"
INTAKE_ID = "CMNINTAKE07292025113208122766172"

# Selector Strategies - Ordered by preference (most specific first)
USERNAME_SELECTORS = [
    'input#txtUserID',  # Current working selector
    'input[name="UserIdentifier"]',
    'input[name="username"]',
    'input[name="USERNAME"]',
    'input[type="text"]',
    'input[placeholder*="username" i]',
    'input[placeholder*="user" i]',
    'input[placeholder*="login" i]',
    'input[id*="user" i]',
    'input[id*="login" i]'
]

PASSWORD_SELECTORS = [
    'input#txtPassword',  # Current working selector
    'input[name="Password"]',
    'input[name="password"]',
    'input[name="PASSWORD"]',
    'input[type="password"]',
    'input[placeholder*="password" i]',
    'input[placeholder*="pass" i]',
    'input[id*="password" i]',
    'input[id*="pass" i]'
]

LOGIN_BUTTON_SELECTORS = [
    'button#btnLogin',  # Current working selector
    'button[type="submit"][id="sub"]',
    'button[type="submit"]:has-text("Log in")',
    'button[type="submit"]:has-text("Login")',
    'button[type="submit"][name="pyActivity=Code-Security.Login"]',
    'button.loginButton',
    'button[type="submit"]',
    'input[type="submit"]',
    'button:has-text("Sign In")',
    'button:has-text("Submit")',
    'button[id*="login" i]',
    'button[id*="submit" i]'
]

SEARCH_BOX_SELECTORS = [
    'input[aria-label="Search"]',  # Current working selector
    'input[placeholder="Common Intake ID"]',
    'input[placeholder="Search by Intake ID"]',
    'input[placeholder="Search by Intake ID or Patient Name"]',
    'input[placeholder*="Intake ID" i]',
    'input[placeholder*="Search" i]',
    'input[placeholder*="Intake" i]',
    'input[placeholder*="Patient" i]',
    'input[aria-label*="search" i]',
    'input[aria-label*="intake" i]',
    'input[type="search"]',
    'input[name*="search" i]',
    'input[name*="intake" i]',
    'input[id*="search" i]',
    'input[id*="intake" i]'
]

# Intake Application Selectors
INTAKE_USERNAME_SELECTORS = [
    'input[name="UserIdentifier"]',
    'input[name="username"]',
    'input[name="USERNAME"]',
    'input[type="text"]',
    'input[placeholder*="username" i]',
    'input[placeholder*="user" i]',
    'input[placeholder*="login" i]',
    'input[id*="user" i]',
    'input[id*="login" i]'
]

INTAKE_PASSWORD_SELECTORS = [
    'input[name="Password"]',
    'input[name="password"]',
    'input[name="PASSWORD"]',
    'input[type="password"]',
    'input[placeholder*="password" i]',
    'input[placeholder*="pass" i]',
    'input[id*="password" i]',
    'input[id*="pass" i]'
]

INTAKE_LOGIN_BUTTON_SELECTORS = [
    'button#sub',
    'button[type="submit"][id="sub"]',
    'button[type="submit"]:has-text("Log in")',
    'button[type="submit"]:has-text("Login")',
    'button[type="submit"]',
    'input[type="submit"]',
    'button:has-text("Sign In")',
    'button:has-text("Submit")',
    'button[id*="login" i]',
    'button[id*="submit" i]'
]

INTAKE_SEARCH_SELECTORS = [
    'input[name="$PpyDisplayHarness$ppySearchText"]',
    'input[placeholder="Enter text to search"]',
    'span.primary_search input',
    'input[placeholder*="Intake ID" i]',
    'input[placeholder*="Search" i]',
    'input[placeholder*="Intake" i]',
    'input[placeholder*="Patient" i]',
    'input[aria-label*="search" i]',
    'input[aria-label*="intake" i]',
    'input[type="search"]',
    'input[name*="search" i]',
    'input[name*="intake" i]',
    'input[id*="search" i]',
    'input[id*="intake" i]'
]

# Intake Drug Lookup Selectors
INTAKE_DRUG_LOOKUP_SELECTORS = [
    '(//td[@data-attribute-name=".pyTemplateInputBox"]/div/span/i/img)[1]',
    '//img[contains(@data-click,"DrugLookup")]'
]

INTAKE_DRUG_CLEAR_SELECTORS = [
    '//button[@name="TherapyAndDrugLookup_pyWorkPage.Document.DrugList(1)_17"]'
]

INTAKE_DRUG_SEARCH_INPUT_SELECTORS = [
    '//input[@id="7a12dd37"]'
]

INTAKE_DRUG_SEARCH_BUTTON_SELECTORS = [
    '//button[@name="TherapyAndDrugLookup_pyWorkPage.Document.DrugList(1)_18"]'
]

INTAKE_DRUG_RADIO_SELECTORS = [
    '//table[contains(@grid_ref_page,".DrugList")]/tbody/tr/td//input[@type="radio"]'
]

INTAKE_DRUG_SUBMIT_SELECTORS = [
    '//*[@name="DrugLookUpModalTabUI_pyWorkPage.Document.DrugList(1)_96"]',
    'button[text()="Submit"]'
]

# Intake Patient Lookup Selectors
INTAKE_PATIENT_LOOKUP_SELECTORS = [
    'img[data-template=""][data-click*="PatientLookUp"]',
    'select[name="PatientDetailsTab_pyWorkPage.Document_45"]'
]

INTAKE_PATIENT_CLEAR_SELECTORS = [
    '//button[@name="PatientLookUp_pyWorkPage.Document.Patient_26"]'
]

INTAKE_PATIENT_ID_INPUT_SELECTORS = [
    'input[name="$PpyTempPage$pPatientID"]'
]

INTAKE_PATIENT_SEARCH_BUTTON_SELECTORS = [
    '//button[contains(text(),"Search")]'
]

INTAKE_PATIENT_SUBMIT_SELECTORS = [
    '#ModalButtonSubmit',
    'button#ModalButtonSubmit',
    '//button[@id="ModalButtonSubmit"]'
]

# Intake Form Field Selectors
INTAKE_THERAPY_TYPE_SELECTORS = [
    'input[name="$PpyWorkPage$pDocument$pDrugList$l1$pTherapyType"]',
    'select[name="$PpyWorkPage$pDocument$pDrugList$l1$pTherapyType"]'
]

INTAKE_PLACE_OF_SERVICE_SELECTORS = [
    'input[name="$PpyWorkPage$pDocument$pDrugList$l1$pPOSDescription"]',
    'select[name="$PpyWorkPage$pDocument$pDrugList$l1$pPOSDescription"]'
]

INTAKE_TEAM_NAME_SELECTORS = [
    'input[name="$PpyWorkPage$pDocument$pTeamName"]'
]

INTAKE_ADDRESS_DROPDOWN_SELECTORS = [
    '#ded594e9'
]

# Intake Task and Navigation Selectors
INTAKE_UPDATE_TASK_SELECTORS = [
    'a[partialLinkText="Update Task (Intake)"]',
    'a:has-text("Update Task (Intake)")',
    'a.Update Task (Intake)'
]

INTAKE_PATIENT_DETAILS_TAB_SELECTORS = [
    '(//h3[text()="Patient Details"])[1]'
]

INTAKE_PRESCRIBER_TAB_SELECTORS = [
    '//h3[text()="Prescriber / Category / Team"]'
]

INTAKE_TASK_SUBMIT_SELECTORS = [
    'button[name="CommonFlowActionButtons_pyWorkPage_17"]',
    '//button[@title="Complete this assignment"]',
    '//button[text()="Submit"]'
]

# Intake Verification Selectors
INTAKE_CASE_SUMMARY_SELECTORS = [
    '//div[text()="Case summary"]'
]

INTAKE_TTASK_STATUS_SELECTORS = [
    '(//*[@id="bodyTbl_right"]/tbody/tr[2]/td[3]/div/span)'
]

# Clearance Application Selectors
CLEARANCE_SEARCH_CASES_SELECTORS = [
    'button:has-text("Search Cases")',
    'button[title*="Search Cases"]',
    'button[id*="search"]',
    'button[id*="cases"]',
    'a:has-text("Search Cases")',
    'input[value="Search Cases"]',
    '*:has-text("Search Cases")',
    '[data-test-id*="search"]:has-text("Search Cases")',
    '[class*="pyharness"]:has-text("Search Cases")',
    '[class*="pega"]:has-text("Search Cases")'
]

CLEARANCE_PATIENT_SEARCH_SELECTORS = [
    'input[placeholder*="Patient ID"]',
    'input[placeholder*="patient"]',
    'input[name*="patient"]:not([name*="RxHome"]):not([name*="RxP"])',
    'input[id*="patient"]:not([id*="RxHome"]):not([id*="RxP"])',
    'input[aria-label*="Patient"]',
    'input[type="text"]:not([name*="RxHome"]):not([name*="RxP"]):not([id*="RxHome"]):not([id*="RxP"])'
]

CLEARANCE_SEARCH_BUTTON_SELECTORS = [
    'button:has-text("Search")',
    'button[type="submit"]',
    'input[type="submit"]',
    'button[id*="search"]',
    'button[title*="Search"]'
]

CLEARANCE_IE_CASE_SELECTORS = [
    'a:has-text("IE-")',
    'tr:has-text("IE-")',
    'td:has-text("IE-")',
    '[data-id*="IE-"]',
    'a[id*="IE-"]'
]

CLEARANCE_PLACE_OF_SERVICE_SELECTORS = [
    'select[name*="place"]',
    'select[name*="service"]',
    'select[id*="place"]',
    'select[id*="service"]',
    'select[aria-label*="Place"]',
    'select'
]

CLEARANCE_PAYER_FIELD_SELECTORS = {
    'bin': ['input[name*="bin"]', 'input[id*="bin"]', 'input[placeholder*="BIN"]'],
    'pcn': ['input[name*="pcn"]', 'input[id*="pcn"]', 'input[placeholder*="PCN"]'],
    'group_number': ['input[name*="group"]', 'input[id*="group"]', 'input[placeholder*="Group"]'],
    'adjudication_group': ['input[name*="adjudication"]', 'input[id*="adjudication"]', 'select[name*="adjudication"]']
}

CLEARANCE_POLICY_FIELD_SELECTORS = {
    'cardholder_id': ['input[name*="cardholder"]', 'input[id*="cardholder"]', 'input[placeholder*="Cardholder"]'],
    'person_code': ['input[name*="person"]', 'input[id*="person"]', 'input[placeholder*="Person"]'],
    'effective_date': ['input[name*="effective"]', 'input[id*="effective"]', 'input[type="date"]']
}

CLEARANCE_SAVE_BUTTON_SELECTORS = [
    'button:has-text("Save")',
    'button[type="submit"]:has-text("Save")',
    'input[value="Save"]',
    'button[id*="save"]',
    'button[title*="Save"]'
]

CLEARANCE_NEXT_BUTTON_SELECTORS = [
    'button:has-text("Next")',
    'button[id*="next"]',
    'button[title*="Next"]',
    'a:has-text("Next")'
]

CLEARANCE_COPAY_SELECTORS = [
    'select[name*="copay"]',
    'select[id*="copay"]',
    'input[name*="copay"]',
    'select[aria-label*="Co-pay"]'
]

CLEARANCE_FINISH_BUTTON_SELECTORS = [
    'button:has-text("Finish")',
    'button[id*="finish"]',
    'button[title*="Finish"]',
    'input[value="Finish"]'
]

# Timing Configuration
PAGE_LOAD_WAIT = 2
LOGIN_WAIT = 3
SEARCH_WAIT = 2
COMPLETION_WAIT = 2

# Retry Configuration
MAX_RETRIES = 3
RETRY_DELAY = 2

# Security Challenge Configuration
SECURITY_CHALLENGE_WAIT = 30 