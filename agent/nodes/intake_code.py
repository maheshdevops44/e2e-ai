from nodes.adapters.llm_adapters import get_azure_llm
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from pprint import pprint
import re
import dotenv
import httpx
from nodes.clearance_code import generate_clearance_steps
from nodes.crm_code import generate_crm_code
from nodes.rxp_code import generate_rxp_code
from nodes.rxp_code_reject import generate_rxp_code_reject
from nodes.patient_id_generator import patient_id_generator
from langchain_community.callbacks import get_openai_callback


dotenv.load_dotenv()


def extract_python_code(llm_output: str) -> str:
    """
    Extract and return just the Python code block from a string with potential markdown/code wrapping.
    Works with fenced code blocks (```python ... ```) or raw code.
    """
    # Look for ```python ... ``` or ``` ... ``` fenced code block first
    match = re.search(
        r"```python(.*?)```",
        llm_output,
        re.DOTALL | re.IGNORECASE
    )
    if match:
        code = match.group(1)
    else:
        # Fallback: any ``` ... ``` block
        match = re.search(r"```(.*?)```", llm_output, re.DOTALL)
        if match:
            code = match.group(1)
        else:
            # No fences found, return the whole text
            code = llm_output

    # Remove any leading/trailing whitespace
    return code.strip()


def generate_intake_steps(patient_id,intake_id,patient__type,steps):

    llm = get_azure_llm("ai-coe-gpt41", temperature=0.0)

    output_example = """
    You are an expert Python Playwright automation engineer.

    Instructions:
    1) Read the given {steps} and extract only steps for intake application
    2) Identify the fields given in {steps} as input like SB(service branch),Drug Name,NDC,Therapy Type, Place of Service,NPI, Fax input,Team, etc.
    3) These input will change in the automation script according to the scenario but the element_reference_code logic will be the same- DO NOT use the patient or intake id given in {steps}
    4) ALWAYS Replace patient_id value with 1*******.
    5) ALWAYS Replace common_intake_id value with CMNINTAKE***************.
    6) ALWAYS USE element_reference_code as it is except the input fields. DO NOT ADD YOUR OWN LOGIC.DO NOT HALLUCINATE
    7) DO NOT change anything in the element_reference_code logic except the input values according to the above given instructions.DO NOT HALLUCINATE.
    8) element_reference_code is your working template to fill in the input values according to the {steps} that is passed as input.
    9) Generate a Python function named `def test_step_intake(page_with_video): ...` that performs the scenario steps provided. DO NOT HALLUCINATE.
    10) **ALWAYS** pass ONLY page_with_video as input to the function `def test_step_intake(page_with_video): ...`
    10) Always begin the function by navigating to the initial page using `page.goto(initial_url)` (the initial_url will be given as a variable).
    11)For any element that could be inside a frame, always use ONLY the provided `find_element_across_frames` utility. Never use `page.locator()` or access frames directly.
    12)ALWAYS Use appropriate logs and wait time as given in the element_reference_code
    13)Use the selectors exactly as provided in the selector mapping. Do not invent or modify selectors. If a selector is named "searchCases" with a value from the mapping, use that as the string.
    14)element_reference_code is an working playwright code given as reference for latest elements in the application.
    15)If an element is not found, raise an Exception with a clear message.
    16)** ALWAYS ** use NDC code instead of Drug Name for searching as given in the element_reference_code.
    17)ALWAYS use the same wait/sleep time as given in the element_reference_code.DO NOT CHANGE while generating automation scripts.
    18)Only output valid Python code for the full function (imports plus function) and nothing else -- no explanation or markdown.
    19)Use selector path or logic has been provided to you in 'SELECTOR CHANGES'. Use given selector paths or logic for respective selector only.
    20)After patient_tab_elem if you are seeing patient_tab_elem then click it again else pass. make such changes with patient_tab_elem.
    21)After click login button 'login_btn' use sleep(8).
    22)New popup window only comes after 'update_task_elem' and 'update_task_link' ('Update Task (Intake)' step) steps so use handle_popups function only after with sleep(5).
    23)After 'Update Task (Intake)' step take sleep(5). Also, after 'Go to Patient tab' take sleep(1).
    24)Focus on the format given in EXAMPLE. 
    257)Focus on elements and logic given in element_reference_code
    26)DO NOT CREATE any function for taking screenshot.
    27)In Intake Application, whenever we have instruction 'Go to Drug tab' you can avoid it as its default page.
    28)** IMPORTANT ** DO NOT INCLUDE ADDITIONAL FUNCTION FOR SCREENSHOTS. THESE UTILIIY FUNCTIONS WILL BE ADDED AS IMPORTS LATER MANUALLY.
    
    EXAMPLE

    Given:
    initial_url = "https://example.com/login"
    Selectors Mapping:
    USERNAME = LAN_ID
    PASSWORD = LAN_PASSWORD
    login: button#sub
    searchCases: a[name="SearchUtilities_pyDisplayHarness_5"]

    Scenario Steps:
    1. Go to login page
    2. Enter Username and Password, then click Login
    3. Click Search Cases


    Output:

    page = page_with_video
    page.goto("https://example.com/login")
    username = find_element_across_frames(page, 'input[name="UserIdentifier"]')
    if not username:
        print("[ERROR]  'Username' not found")
        raise Exception("Username input not found")
    username.fill(USER_NAME)
    print("[LOG] Filled username with demo")
    screenshot(page, "step_1_filled_username")
    sleep(2)

    password = find_element_across_frames(page, 'input[name="Password"]')
    if not password:
        print("[ERROR]  'Password' not found")
        raise Exception("Password input not found")
    password.fill(PASSWORD)
    print("[LOG] Filled password with PASSWORD")
    screenshot(page, "step_2_filled_password")
    sleep(2)

    login_btn = find_element_across_frames(page, 'button#sub')
    if not login_btn:
        print("[ERROR]  'Login' not found")
        raise Exception("Login button not found")
    login_btn.click()
    print("[LOG] Clicked on Login button")
    screenshot(page, "step_3_clicked_on_login_button")
    sleep(2)

    search_cases = find_element_across_frames(page, 'a[name="SearchUtilities_pyDisplayHarness_5"]')
    if not search_cases:
        print("[ERROR]  'Search Cases' not found")
        raise Exception("Search Cases link not found")
    search_cases.click()
    print("[LOG] Clicked search case link")
    screenshot(page, "step_4_clicked_search_Case_link")
    sleep(2)

    END EXAMPLE

    SELECTOR CHANGES:

    - For Search Intake ID in top-right search box, use:  '(//input[@id="24dbd519"])[1]'
    - For Try to find first T-ID link in search result table, use: '(//*[@id="bodyTbl_right"]/tbody/tr[2]/td[3]/div/span)')
    - To handle any new popup window define below function outside the def step(page) and call it in def step(page) where its require using  'handle_popups(page)'.
    def handle_popups(page):
        try:
            # Look for and close any modal dialogs
            modal_close_btn = page.locator('button[aria-label="Close"], .modal-close, .dialog-close').first
            if modal_close_btn and modal_close_btn.is_visible():
                modal_close_btn.click(timeout=3000)
                print("Closed modal dialog")
                sleep(1)
        except:
            pass
    - For Drug Lookup popup - clear button, use: '//button[@name="TherapyAndDrugLookup_pyWorkPage.Document.DrugList(1)_17"]'  
    - For Drug Lookup popup - search button, use: '//button[@name="TherapyAndDrugLookup_pyWorkPage.Document.DrugList(1)_18"]'     
    - For humira radio button: use: '//table[contains(@grid_ref_page,".DrugList")]/tbody/tr/td//input[@type="radio"]'      
    - For drug submit button, use: "//*[@name='DrugLookUpModalTabUI_pyWorkPage.Document.DrugList(1)_96']") or "//button[text()='Submit']")
    - For therapy type, use:"input[name='$PpyWorkPage$pDocument$pDrugList$l1$pTherapyType']"
    - For Place of service, use : "select[name='$PpyWorkPage$pDocument$pDrugList$l1$pPOSDescription']" or "input[name='$PpyWorkPage$pDocument$pDrugList$l1$pPOSDescription']"
    - For Patient search icon, use: 'img[data-template=""][data-click*="PatientLookUp"]'
    - For Search clear button, use: "//button[@name='PatientLookUp_pyWorkPage.Document.Patient_26']"
    - For Patient search button, use: "//button[contains(text(),'Search')]"
    - For Select the record with SB = 555, use: "//table[contains(@grid_ref_page,'pyWorkPage.Document.Patient')]/tbody/tr[./td[4]//span[text()='555']]/td[2]//input[@type='radio']" or "//table[contains(@grid_ref_page,'pyWorkPage.Document.Patient')]/tbody/tr[contains(@class,'Row')]/td[4]/div/span[text()='555']/ancestor::tr/td[2]//input[@type='radio']"
            
    - For submit button i.e., submit_patient_btn, use: "//button[@id='ModalButtonSubmit']"
    - For From Address List, select any address, use: "#ded594e9", Also for selecting first row you can use: address_dropdown.select_option(index=1)
    - For Team dropdown, use: "input[name='$PpyWorkPage$pDocument$pTeamName']"
    - In Team dropdown select first non-blank team if blank:
        options = team_dropdown.locator("option:not([value=''])") ##needed

        if options.count() > 0: # Check if there are any non-blank options
            first_option_value = options.first.get_attribute("value") #
            team_dropdown.select_option(first_option_value) #
            # print(f"Selected team: {first_option_value}")
        else:
            print("No non-blank team options found.")
        sleep(1)    
    - For task_submit_btn, use: "button[name='CommonFlowActionButtons_pyWorkPage_17']"

    """

    system_prompt_script_generation = f"""{output_example}"""
    
    element_reference_code = """
    
    def test_step_intake(page_with_video):
    
        print("[LOG] TESTING INITIATED FOR INTAKE APPLICAION")
    
        initial_url = "https://spcia-qa.express-scripts.com/spcia"
        COMMON_INTAKE_ID = {intake_id}
        PATIENT_ID = {patient_id}
        USERNAME = LAN_ID
        PASSWORD = LAN_PASSWORD

        page = page_with_video
        page.goto(initial_url)
        sleep(5)

        # Step 1: Login
        username_elem = find_element_across_frames(page, 'input[name="UserIdentifier"]')
        if not username_elem:
            print("[ERROR]  Username input not found")
            raise Exception(" Username input not found")
        username_elem.fill(USERNAME)
        print("[LOG] Filled username with LAN_ID")
        screenshot(page, "Intake_step_1_filled_username")
        sleep(2)

        password_elem = find_element_across_frames(page, 'input[name="Password"]')
        if not password_elem:
            print("[ERROR]  Password input not found")   
            raise Exception("Password input not found")
        password_elem.fill(PASSWORD)
        print("[LOG] Filled password with PASSWORD")
        screenshot(page, "Intake_step_1_filled_password")
        sleep(2)

        login_btn = find_element_across_frames(page, 'button#sub')
        if not login_btn:
            print("[ERROR]  Login button not found")   
            raise Exception("Login button not found")
        login_btn.click()
        print("[LOG] Clicked on Login button")
        screenshot(page, "Intake_step_1_clicked_login")
        print("[LOG] Logged in Intake Application Successfully")
        sleep(8)

        # Step 2: Search Intake ID in top-right search box
        search_box = find_element_across_frames(page, '(//input[@id="24dbd519"])[1]')
        if not search_box:
            print("[ERROR]  search box for Intake ID not found")
            raise Exception("Top-right search box for Intake ID not found")
        search_box.fill(COMMON_INTAKE_ID)
        print(f"[LOG] Entered Common Intake ID: {COMMON_INTAKE_ID}")
        screenshot(page, "Intake_step_2_filled_common_intake_id")
        sleep(10)
        search_box.press("Enter")
        print("[LOG] Pressed Enter in intake search box")
        screenshot(page, "Intake_step_2_pressed_enter_searchbox")
        sleep(20)

        # Step 3: Click first T-ID link in search result table
        t_id_link = find_element_across_frames(page, '(//*[@id="bodyTbl_right"]/tbody/tr[2]/td[3]/div/span)')
        if not t_id_link:
            print("[ERROR]   T-ID link in search result table not found")
            raise Exception("First T-ID link in search result table not found")
        t_id_link.click()
        print(f"[LOG] Clicked T-ID link")
        screenshot(page, "Intake_step_3_clicked_tid_link")
        sleep(10)

        # Step 4: Click 'Update Task (Intake)'
        update_task_elem = find_element_across_frames(page, '//a[contains(text(),"Update Task (Intake)")]')
        if not update_task_elem:
            update_task_elem = find_element_across_frames(page, '//span[contains(text(),"Update Task (Intake)")]')
        else:
            print("[ERROR]   Update Task (Intake) link not found. Intake is already Resolved for this Patient ID")
            raise Exception("Update Task (Intake) link not found")
        update_task_elem.click()
        print("[LOG] Clicked Update Task (Intake)")
        screenshot(page, "Intake_step_4_clicked_update_task_intake")
        sleep(5)
        handle_popups(page)
        sleep(5)

        # Step 5: Close EIS Image Window (close modal)
        handle_popups(page)
        print("[LOG] Closed EIS Image Window if present")
        screenshot(page, "Intake_step_5_closed_eis_image_window")
        sleep(5)

        # Step 6: Drug Lookup (Drug tab is default page)
        drug_search_icon = find_element_across_frames(page, '//img[contains(@data-click,"DrugLookup")]')
        if not drug_search_icon:
            print("[ERROR]   Drug Lookup search icon not found")
            raise Exception("Drug Lookup search icon not found")
        drug_search_icon.click()
        print("[LOG] Clicked Drug Lookup search icon")
        screenshot(page, "Intake_step_6_clicked_drug_lookup_search_icon")
        sleep(5)

        # Step 7: Drug Lookup popup - clear button
        clear_btn = find_element_across_frames(page, '//button[@name="TherapyAndDrugLookup_pyWorkPage.Document.DrugList(1)_17"]')
        if not clear_btn:
            print("[ERROR]   Drug Lookup popup - clear button not found")
            raise Exception("Drug Lookup popup - clear button not found")
        clear_btn.click()
        print("[LOG] Clicked clear in Drug Lookup popup")
        screenshot(page, "Intake_step_7_clicked_clear_drug_lookup")
        sleep(2)

        # Drug Lookup popup - enter NDC and Search
        drug_name_input = find_element_across_frames(page, "input[name='$PpyTempPage$pDrugName']")
        if not drug_name_input:
            print("[ERROR]   Drug name input not found in Drug Lookup popup")
            raise Exception("Drug name input not found in Drug Lookup popup")
        drug_name_input.fill("00074055402")
        print("[LOG] Filled NDC Name: 00074055402")
        screenshot(page, "Intake_step_8_filled_drug_name")
        sleep(2)

        search_btn = find_element_across_frames(page, '//button[@name="TherapyAndDrugLookup_pyWorkPage.Document.DrugList(1)_18"]')
        if not search_btn:
            print("[ERROR]   Drug Lookup popup - search button not found")
            raise Exception("Drug Lookup popup - search button not found")
        search_btn.click()
        print("[LOG] Clicked Search in Drug Lookup popup")
        screenshot(page, "Intake_step_9_clicked_search_drug_lookup")
        sleep(5)

        # Select first radio option (humira radio)
        humira_radio = find_element_across_frames(page, '//table[contains(@grid_ref_page,".DrugList")]/tbody/tr/td//input[@type="radio"]')
        if not humira_radio:
            print("[ERROR]   Drug selection radio button not found")
            raise Exception("Drug selection radio button not found")
        humira_radio.click()
        print("[LOG] Selected first radio for searched drug")
        screenshot(page, "Intake_step_10_selected_drug_radio")
        sleep(2)

        # Drug submit button
        drug_submit_btn = find_element_across_frames(page, "//*[@name='DrugLookUpModalTabUI_pyWorkPage.Document.DrugList(1)_96']")
        if not drug_submit_btn:
            drug_submit_btn = find_element_across_frames(page, "//button[text()='Submit']")
        if not drug_submit_btn:
            print("[ERROR]   Drug submit button not found")
            raise Exception("Drug submit button not found")
        drug_submit_btn.click()
        print("[LOG] Clicked Submit in Drug Lookup popup")
        screenshot(page, "Intake_step_11_clicked_submit_drug_lookup")
        sleep(5)

        # Step 8: Open Task Again (Update Task (Intake) with status "Pending Progress")
        update_task_link = find_element_across_frames(page, '//a[contains(text(),"Update Task (Intake)")]')
        if not update_task_link:
            update_task_link = find_element_across_frames(page, '//span[contains(text(),"Update Task (Intake)")]')
        if not update_task_link:
            print("[ERROR]   Update Task (Intake) link not found for open task again")
            raise Exception("Update Task (Intake) link not found for open task again")
        update_task_link.click()
        print("[LOG] Clicked Update Task (Intake) again for Pending Progress")
        screenshot(page, "Intake_step_12_clicked_update_task_again")
        sleep(5)
        handle_popups(page)
        sleep(5)

        # Step 9: Fill Therapy Type and Place of Service in Drug tab
        therapy_type_input = find_element_across_frames(page, "input[name='$PpyWorkPage$pDocument$pDrugList$l1$pTherapyType']")
        if not therapy_type_input:
            print("[ERROR]   Therapy Type input not found")
            raise Exception("Therapy Type input not found")
        therapy_type_input.fill("HUMA")
        print("[LOG] Filled Therapy Type with HUMA")
        screenshot(page, "Intake_step_13_filled_therapy_type")
        sleep(2)

        place_of_service_dropdown = find_element_across_frames(page, "select[name='$PpyWorkPage$pDocument$pDrugList$l1$pPOSDescription']")
        if not place_of_service_dropdown:
            place_of_service_dropdown = find_element_across_frames(page, "input[name='$PpyWorkPage$pDocument$pDrugList$l1$pPOSDescription']")
        if not place_of_service_dropdown:
            print("[ERROR]   Place of Service dropdown not found")
            raise Exception("Place of Service dropdown not found")
        try:
            place_of_service_dropdown.select_option(label="Home")
            print("[LOG] Selected Place of Service: Home")
        except Exception:
            place_of_service_dropdown.fill("Home")
            print("[LOG] Filled Place of Service: Home (fallback input)")
        screenshot(page, "Intake_step_14_selected_place_of_service")
        sleep(2)

        # Step 10: Link Patient Record
        patient_tab_elem = find_element_across_frames(page, "(//h3[text()='Patient Details'])[1]")
        if patient_tab_elem:
            patient_tab_elem.click()
            print("[LOG] Clicked Patient Details tab")
            screenshot(page, "step_10_clicked_patient_tab")
            sleep(1)
            patient_tab_elem2 = find_element_across_frames(page, "(//h3[text()='Patient Details'])[1]")
            if patient_tab_elem2:
                try:
                    patient_tab_elem2.click()
                    print("[LOG] Clicked Patient Details tab again")
                except Exception:
                    pass
        else:
            print("[LOG] Patient Details tab not found, continuing.")
        sleep(1)

        patient_search_icon = find_element_across_frames(page, 'img[data-template=""][data-click*="PatientLookUp"]')
        if not patient_search_icon:
            print("[ERROR]   Patient search icon not found")
            raise Exception("Patient search icon not found")
        patient_search_icon.click()
        print("[LOG] Clicked Patient search icon")
        screenshot(page, "Intake_step_15_clicked_patient_search_icon")
        sleep(2)

        patient_clear_btn = find_element_across_frames(page, "//button[@name='PatientLookUp_pyWorkPage.Document.Patient_26']")
        if not patient_clear_btn:
            print("[ERROR]   Patient search clear button not found")
            raise Exception("Patient search clear button not found")
        patient_clear_btn.click()
        print("[LOG] Clicked clear in Patient search")
        screenshot(page, "Intake_step_16_clicked_patient_clear")
        sleep(2)

        patient_id_input = find_element_across_frames(page, "input[name='$PpyTempPage$pPatientID']")
        if not patient_id_input:
            print("[ERROR]   Patient ID input not found in Patient search")
            raise Exception("Patient ID input not found in Patient search")
        patient_id_input.fill(PATIENT_ID)
        print(f"[LOG] Filled Patient ID: {PATIENT_ID}")
        screenshot(page, "Intake_step_17_filled_patient_id")
        sleep(2)

        patient_search_btn = find_element_across_frames(page, "//button[contains(text(),'Search')]")
        if not patient_search_btn:
            print("[ERROR]   Patient search button not found")
            raise Exception("Patient search button not found")
        patient_search_btn.click()
        print("[LOG] Clicked Search in Patient search popup")
        screenshot(page, "Intake_step_18_clicked_patient_search")
        
        sleep(5)

        patient_radio = find_element_across_frames(page, "//table[contains(@grid_ref_page,'pyWorkPage.Document.Patient')]/tbody/tr[./td[4]//span[text()='799']]/td[2]//input[@type='radio']")
        if not patient_radio:
            patient_radio = find_element_across_frames(page, "//table[contains(@grid_ref_page,'pyWorkPage.Document.Patient')]/tbody/tr[contains(@class,'Row')]/td[4]/div/span[text()='799']/ancestor::tr/td[2]//input[@type='radio']")
        if not patient_radio:
            print("[ERROR]   Patient record radio with SB=799 not found")
            raise Exception("Patient record radio with SB=799 not found")
        patient_radio.click()
        print("[LOG] Selected patient record with SB=799")
        screenshot(page, "Intake_step_19_selected_patient_record")
        sleep(2)

        submit_patient_btn = find_element_across_frames(page, "//button[@id='ModalButtonSubmit']")
        if not submit_patient_btn:
            print("[ERROR]   Submit button not found in patient search popup")
            raise Exception("Submit button not found in patient search popup")
        submit_patient_btn.click()
        print("[LOG] Clicked Submit in Patient search popup")
        screenshot(page, "Intake_step_20_clicked_submit_patient")
        sleep(5)

        address_dropdown = find_element_across_frames(page, "#ded594e9")
        if not address_dropdown:
            print("[ERROR]   Address dropdown not found")
            raise Exception("Address dropdown not found")
        try:
            address_dropdown.select_option(index=1)
            print("[LOG] Selected address from Address List (index 1)")
        except Exception:
            print("[LOG]  Could not select from address dropdown, trying fallback click.")
            address_dropdown.click()
        screenshot(page, "Intake_step_21_selected_address")
        sleep(2)

        # Step 11: Complete Prescriber/Category Team tab
        prescriber_tab_elem = find_element_across_frames(page, "(//h3[text()='Prescriber / Category / Team'])[1]")
        if prescriber_tab_elem:
            prescriber_tab_elem.click()
            print("[LOG] Clicked Prescriber / Category / Team tab")
            screenshot(page, "Intake_step_22_clicked_prescriber_category_team_tab")
            sleep(2)
        team_dropdown = find_element_across_frames(page, "input[name='$PpyWorkPage$pDocument$pTeamName']")
        if not team_dropdown:
            print("[ERROR]   Team dropdown not found")
            raise Exception("Team dropdown not found")
        try:
            if hasattr(team_dropdown, "input_value") and team_dropdown.input_value().strip() == "":
                options = team_dropdown.locator("option:not([value=''])")
                if options.count() > 0:
                    first_option_value = options.first.get_attribute("value")
                    team_dropdown.select_option(first_option_value)
                    print(f"[LOG] Selected team: {first_option_value}")
                else:
                    print("No non-blank team options found.")
                sleep(1)
            else:
                team_dropdown.fill("ARTH MHS")
                print("[LOG] Filled ARTH MHS in Team dropdown")
        except Exception:
            try:
                team_dropdown.fill("ARTH MHS")
                print("[LOG] Filled ARTH MHS in Team dropdown (fallback)")
            except Exception:
                print("[ERROR]  Could not fill/select Team in Team dropdown")
        screenshot(page, "Intake_step_22_filled_team")
        sleep(2)

        # Step 12: Click Submit
        task_submit_btn = find_element_across_frames(page, "button[name='CommonFlowActionButtons_pyWorkPage_17']")
        if not task_submit_btn:
            print("[ERROR]  Task Submit button not found")
            raise Exception("Task Submit button not found")
        task_submit_btn.click()
        sleep(15)
        print("[LOG] Clicked Submit to complete Intake T-Task id")
        sleep(10)
        screenshot(page, "Intake_step_23_clicked_submit")
        print("[LOG] Automation completed for Intake test scenario.")

    """
    user_input = f"""
    
    {element_reference_code}

    Application name : Intake
    <INFO>
    Url -> https://spcia-qa.express-scripts.com/spcia
    intake id :{intake_id}
    patient id:{patient_id}
    </INFO>

    <Your task>
    {steps}
    </Your task>
    """

    messages = [ SystemMessage(system_prompt_script_generation), HumanMessage(user_input) ]

    
    with get_openai_callback() as cb:
        llm_code = llm.invoke(messages).content
        print(llm_code)
        print("---")
    print()

    print(f"Script - Intake Total Tokens: {cb.total_tokens}")
    print(f"Script - Intake Prompt Tokens: {cb.prompt_tokens}")
    print(f"Script - Intake Completion Tokens: {cb.completion_tokens}")

    parsed_code = extract_python_code(llm_code)

    clearance_parsed_code = generate_clearance_steps(patient_id,steps)
    rxp_parsed_code = generate_rxp_code(patient_id,steps)
    rxp_parsed_code_reject = generate_rxp_code_reject(patient_id,steps)
    crm_parsed_code = generate_crm_code(patient_id,steps)
    
    script_import = """ 
 
import sys
import os
from pathlib import Path

# Add the parent directory to Python path so we can import from nodes
parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))

from nodes.agent_utils import find_element_across_frames, robust_fill
from time import sleep
from datetime import datetime,timedelta
from playwright.sync_api import sync_playwright
import sys
import os
import pytest
from playwright.sync_api import Page, expect


from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables from .env file
# The .env file is in the root config directory
dotenv_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path)

# Get environment variables
LAN_ID = os.getenv("LAN_ID")
LAN_PASSWORD = os.getenv("LAN_PASSWORD")

def retry_find_and_click_element(page, selector, max_attempts=90, delay=2, element_name="element"):

    print(f"[RETRY] Starting retry mechanism for {element_name} (will try for 3 minutes)")
    print(f"[RETRY] Using selector: {selector}")
    
    for attempt in range(1, max_attempts + 1):
        print(f"[RETRY] Attempt {attempt}/{max_attempts} - Looking for {element_name}")
        
        try:
            element = find_element_across_frames(page, selector)
            if element:
                print(f"[RETRY] Success! Found {element_name} on attempt {attempt}")
                print(f"[RETRY] Element text: '{element.text_content()}'")
                print(f"[RETRY] Element tag: {element.tag_name}")
                print(f"[RETRY] Element visible: {element.is_visible()}")
                sleep(60)
                element.click()
                print(f"[RETRY] Clicked on {element_name}")
                return True
            else:
                print(f"[RETRY] {element_name} not found on attempt {attempt}")
        except Exception as e:
            print(f"[RETRY] Error on attempt {attempt}: {str(e)}")
        
        if attempt < max_attempts:
            print(f"[RETRY] Waiting {delay} seconds before next attempt...")
            sleep(delay)
    
    print(f"[RETRY] Failed to find {element_name} after {max_attempts} attempts (3 minutes)")
    return False



@pytest.fixture
def page_with_video(browser):
    video_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),"..", 'videos'))
    os.makedirs(video_dir, exist_ok=True)
    print("****************************",video_dir)
    context = browser.new_context(record_video_dir=video_dir)
    page = context.new_page()
    yield page
    page.close()
    context.close()

def screenshot(page, name):
    screenshot_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),"..", 'screenshots'))
    os.makedirs(screenshot_dir, exist_ok=True)
    print(f"[SCREENSHOT] {name}.png")
    page.screenshot(path=os.path.join(screenshot_dir, f"{name}.png"))



    """
    
        # Initialize final_parsed_code with default value
    final_parsed_code = ""

        # Replace the placeholder values with actual patient_id and intake_id
    parsed_code = parsed_code.replace("{patient_id}", f'"{patient_id}"')
    parsed_code = parsed_code.replace('"1*******"', f'"{patient_id}"')
    parsed_code = parsed_code.replace('"CMNINTAKE***************"', f'"{intake_id}"')


    if patient__type == "Direct":
        final_parsed_code = script_import + "\n\n" + parsed_code + "\n\n" + clearance_parsed_code + "\n\n" + rxp_parsed_code + "\n\n" + crm_parsed_code
    elif patient__type == "Integrated":
        final_parsed_code = script_import + "\n\n" + parsed_code + "\n\n" + rxp_parsed_code + "\n\n" + crm_parsed_code
    else:
        final_parsed_code = script_import + "\n\n" + parsed_code + "\n\n" + clearance_parsed_code + "\n\n" + rxp_parsed_code_reject
    # final_parsed_code = script_import + "\n\n" + parsed_code + "\n\n" + clearance_parsed_code + "\n\n" + rxp_parsed_code

    with open("output.py", "w", encoding="utf-8") as f:
        f.write(final_parsed_code)

    return final_parsed_code

# if __name__ == "__main__":
#     print(generate_intake_steps("17098051","CMNINTAKE08132025121915582328346","Direct"))