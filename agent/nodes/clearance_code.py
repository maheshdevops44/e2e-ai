#from nodes.adapters.llm_adapters import get_azure_llm
from nodes.adapters.llm_adapters import get_azure_llm
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from pprint import pprint
import re
import dotenv
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

#llm = get_azure_llm("ai-coe-gpt41")
def generate_clearance_steps(patient_id,steps):
    
    llm = get_azure_llm("ai-coe-gpt41",temperature=0.0)
    
    output_example = """
    You are an expert Python Playwright automation engineer. You will be given snippets of java selenium code. Your job is to generate playwright code for the given scenario.

    Instructions:
    
    1) Read the given {steps} and extract only steps for clearance application.
    2) Identify the fields given in {steps} as input like Place of Service,BIN,PCN,Group Number,Cardholder ID,Person Code,Primary Payer for Service(s)  etc.
    3) These input will change in the automation script according to the scenario but the element_reference_code logic will be the same- DO NOT use the patient id given in {steps}
    4) ALWAYS Replace patient id given in the {steps} with {patient_id} passed as input in this function. DO NOT PUT ANY PLACEHOLDERS. The {patient_id} will be replaced with the actual value later.
    6) DO NOT change anything in the element_reference_code logic except the input values according to the above given instructions.DO NOT HALLUCINATE.
    7) element_reference_code is your working template to fill in the input values according to the {steps} that is passed as input. FOLLOW THE FUNCTION SIGNATURE EXACTLY AS SHOWN IN THE ELEMENT_REFERENCE_CODE.
    8) Generate a Python function named `def test_step_clearance(page_with_video): ...` that performs the scenario steps provided. DO NOT add any parameters to the function signature.
    9) Always begin the function by navigating to the initial page using `page.goto(initial_url)`.
    10)ALWAYS use "https://clearance-qa.express-scripts.com/spclr" as inital_url.
    11)For any element that could be inside a frame, always use ONLY the provided `find_element_across_frames` utility. Never use `page.locator()` or access frames directly.
    12)ALWAYS Use appropriate logs,exception and wait time as given in the element_reference_code
    13)Use the selectors exactly as provided in the selector mapping. Do not invent or modify selectors. If a selector is named "searchCases" with a value from the mapping, use that as the string.
    14)element_reference_code is an working playwright code given as reference for latest elements in the application.
    15)If an element is not found, raise an Exception with a clear message.
    16)ALWAYS use the same wait/sleep time as given in the element_reference_code.DO NOT CHANGE while generating automation scripts.
    17)Only output valid Python code for the full function (imports plus function) and nothing else -- no explanation or markdown.
    18)Use selector path or logic has been provided to you in 'SELECTOR CHANGES'. Use given selector paths or logic for respective selector only.
    19)After click login button 'login_btn' use sleep(8).
    20)** IMPORTANT ** DO NOT INCLUDE ADDITIONAL FUNCTION FOR SCREENSHOTS. THESE UTILIIY FUNCTIONS WILL BE ADDED AS IMPORTS LATER MANUALLY.
  
    EXAMPLE

    Given:
    initial_url = "https://example.com/login"
    USERNAME = LAN_ID
    PASSWORD = LAN_PASSWORD
    PATIENT_ID = {patient_id}
    Selectors Mapping:
   
    login: button#sub
    searchCases: a[name="SearchUtilities_pyDisplayHarness_5"]

    Scenario Steps:
    1. Go to login page
    2. Enter Username and Password, then click Login
    3. Click Search Cases

    Output:

    from nodes.agent_utils import find_element_across_frames
    from time import sleep
    def test_step_clearance(page_with_video):
        page.goto("https://example.com/login")
        username = find_element_across_frames(page, 'input[name="UserIdentifier"]')
        if not username:
            print("[ERROR]  'Username' not found")
            raise Exception("Username input not found")
        username.fill(USER_NAME)
        print("[LOG] Filled username with LAN_ID")
        screenshot(page, "Clearance_step_2_clearance_filled_username")
        sleep(2)

        password = find_element_across_frames(page, 'input[name="Password"]')
        if not password:
            print("[ERROR]  'Password' not found")
            raise Exception("Password input not found")
        password.fill(PASSWORD)
        print("[LOG] Filled username with PASSWORD")
        screenshot(page, "Clearance_step_3_clearance_filled_password")
        sleep(2)

        login_btn = find_element_across_frames(page, 'button#sub')
        if not login_btn:
            print("[ERROR]  'Login' not found")
            raise Exception("Login button not found")
        login_btn.click()
        print("[LOG] Login Successful with credentials")
        screenshot(page, "Clearance_step_4_clearance_login")
        sleep(2)

        search_cases = find_element_across_frames(page, 'a[name="SearchUtilities_pyDisplayHarness_5"]')
        if not search_cases:
            print("[ERROR]  'Search Cases' not found")
            raise Exception("Search Cases link not found")
        search_cases.click()
        screenshot(page, "Clearance_step_5_clearance_search_cases")
        sleep(2)

    END EXAMPLE
    """

    system_prompt_script_generation = f"""{output_example}"""

    element_reference_code = """ 
    def test_step_clearance(page_with_video):
    
        print("[LOG] TESTING INITIATED FOR CLEARANCE APPLICAION")

        USERNAME = LAN_ID
        PASSWORD = LAN_PASSWORD
        initial_url = "https://clearance-qa.express-scripts.com/spclr"
        PATIENT_ID = {patient_id}
        page = page_with_video

        page.goto(initial_url)
        sleep(2)

        # Step 1: Login to Clearance
        username = find_element_across_frames(page, 'input[name="UserIdentifier"]')
        if not username:
            print("[ERROR]  Username input not found")
            raise Exception("Username input not found")
        username.fill(USERNAME)
        screenshot(page, "Clearance_step_1_clearance_filled_username")
        print("[LOG] Filled username with LAN_ID")
        sleep(1)

        password = find_element_across_frames(page, 'input[name="Password"]')
        if not password:
            print("[ERROR]  Password input not found")
            raise Exception("Password input not found")
        password.fill(PASSWORD)
        screenshot(page, "Clearance_step_2_clearance_filled_password")
        print("[LOG] Filled password wit LAN_PASSWORD")
        sleep(1)

        login_btn = find_element_across_frames(page, 'button#sub')
        if not login_btn:
            print("[ERROR]  Login button not found")
            raise Exception("Login button not found")
        login_btn.click()
        screenshot(page, "Clearance_step_3_clearance_login")
        print("[LOG] Clicked Login button")
        sleep(4)
        print("[LOG] Logged in Clearance Application Successfully")

        # Step 2: Search for Patient Case
        search_cases = find_element_across_frames(page, 'a[name="SearchUtilities_pyDisplayHarness_5"]')
        if not search_cases:
            print("[ERROR]  Search Cases button not found")
            raise Exception("Search Cases button not found")
        search_cases.click()
        screenshot(page, "Clearance_step_4_clearance_search_cases")
        print("[LOG] Search Cases button clicked")
        sleep(3)

        patient_id_input = find_element_across_frames(page, 'input[name="$PpyDisplayHarness$pCaseSearchCriteria$pPatient$pPatientIDNumeric"]')
        if not patient_id_input:
            print("[ERROR]  Patient ID input not found")
            raise Exception("Patient ID input not found")
        patient_id_input.fill(PATIENT_ID)
        screenshot(page, "Clearance_step_5_clearance_patient_id_input")
        print("[LOG] Entering Patient ID")
        sleep(1)

        max_attempts = 10
        attempt = 0
        while attempt < max_attempts:
            print("[LOG] Waiting for IE case creation. Attempt {attempt}")
            search_btn = find_element_across_frames(page, 'button[name="SearchCases_pyDisplayHarness.CaseSearchCriteria_14"]')
            if not search_btn:
                print("[ERROR]  Search button not found")
                raise Exception("Search button not found")
            search_btn.click()
            sleep(30)

            ie_task_link = find_element_across_frames(page, "//table[@pl_prop='D_GetWorkCases.pxResults']/tbody/tr[2]/td[1]//a")
            if ie_task_link:
                ie_task_link.click()
                sleep(13)
                screenshot(page, "Clearance_step_6_clearance_search_button_input")
                print("[LOG] Found IE case Link for the Patient ID")
                break

            attempt += 1

        if attempt >= max_attempts:
            print("[ERROR]  IE Task ID link not found after maximum attempts")
            raise Exception("IE Task ID link not found after maximum attempts")
        sleep(10)

        # Step 4: Enter Place of Service (POS)
        print("[LOG] Filling in Payer Details")
        pos_input = find_element_across_frames(page, 'input[name="$PpyWorkPage$pPlaceOfService"]')
        if not pos_input:
            print("[ERROR]  Place of Service input not found")
            raise Exception("Place of Service input not found")
        pos_input.fill("12")
        screenshot(page, "Clearance_step_7_clearance_POS")
        print("[LOG] Filled Place of Service")
        sleep(1)

        # Step 5: Enter New Payer 1 - Payer Information
        bin_input = find_element_across_frames(page, 'input[name="$PpyWorkPage$pAdditionalPayers$l1$pBankIDNumber"]')
        if not bin_input:
            print("[ERROR]  BIN input not found")
            raise Exception("BIN input not found")
        bin_input.fill("610140")
        screenshot(page, "Clearance_step_8_clearance_BIN")
        print("[LOG] Filled BIN Input")
        sleep(2)

        pcn_input = find_element_across_frames(page, 'input[name="$PpyWorkPage$pAdditionalPayers$l1$pPCN"]')
        if not pcn_input:
            print("[ERROR]  PCN input not found")
            raise Exception("PCN input not found")
        pcn_input.click()
        sleep(2)
        pcn_input.fill("D0TEST")
        screenshot(page, "Clearance_step_8_clearance_PCN")
        print("[LOG] Filled PCN Input")
        sleep(2)

        group_number_input = find_element_across_frames(page, 'input[name="$PpyWorkPage$pAdditionalPayers$l1$pGroupNumber"]')
        if not group_number_input:
            print("[ERROR]  Group Number input not found")
            raise Exception("Group Number input not found")
        group_number_input.click()
        sleep(2)
        group_number_input.fill("D0TEST")
        print("[LOG] Filled Group Number Input")
        screenshot(page, "Clearance_step_8_clearance_GroupNumber")
        sleep(2)

        save_payee_btn = find_element_across_frames(page, 'button[data-test-id="PayerInfoScreen-Button-Search"]')
        if not save_payee_btn:
            print("[ERROR]  Save Payee button not found")
            raise Exception("Save Payee button not found")
        save_payee_btn.click()
        screenshot(page, "Clearance_step_8_clearance_save_payee")
        print("[LOG] Clicked Save Payee Button")
        sleep(3)

        # Step 6: Enter Policy Information
        print("[LOG] Filling in Policy Details")
        cardholder_input = find_element_across_frames(page, '//span/input[@id="6a329411"]')
        if not cardholder_input:
            print("[ERROR]  Cardholder ID input not found")
            raise Exception("Cardholder ID input not found")
        cardholder_input.fill("555123123")
        screenshot(page, "Clearance_step_8_clearance_cardholder")
        print("[LOG] Entered Cardholder ID input")
        sleep(1)

        person_code_input = find_element_across_frames(page, '//div/input[@id="a451c2d0"]')
        if not person_code_input:
            print("[ERROR]  Person Code input not found")
            raise Exception("Person Code input not found")
        person_code_input.fill("01")
        screenshot(page, "Clearance_step_8_clearance_person_code_input")
        print("[LOG] Entered Person code input")
        sleep(2)

        effective_date_input = find_element_across_frames(page, '//span/input[@class="inactvDtTmTxt"]')
        if not effective_date_input:
            print("[ERROR]  Insurance Effective Date input not found")
            raise Exception("Insurance Effective Date input not found")
        today = datetime.now().strftime("%m/%d/%Y")
        effective_date_input.fill(today)
        screenshot(page, "Clearance_step_8_clearance_effective_date_input")
        print("[LOG] Entered Effective Data input")
        sleep(1)

        end_date_input = find_element_across_frames(page, 'input[data-test-id="20171109141147048668261"]')
        if not end_date_input:
            print("[ERROR]  End Date input not found")
            raise Exception("End Date input not found")
        end_date = (datetime.now() + timedelta(days=2)).strftime("%m/%d/%Y")
        end_date_input.fill(end_date)
        screenshot(page, "Clearance_step_8_clearance_end_date_input")
        print("[LOG] Entered End Date input")
        sleep(1)

        relationship_dropdown = find_element_across_frames(page, '//div/select[@data-test-id="20171115143211077239541"]')
        if not relationship_dropdown:
            print("[ERROR]  Relationship dropdown not found")
            raise Exception("Relationship dropdown not found")
        relationship_dropdown.select_option(label="1 - Self")
        screenshot(page, "Clearance_step_8_clearance_relationship_dropdown")
        print("[LOG] Clicked Relationship Dropdown")
        sleep(1)

        save_policy_btn = find_element_across_frames(page, 'button[data-test-id="20200305121820016323290"]')
        save_policy_btn.click()
        screenshot(page, "Clearance_step_8_clearance_save_policy_btn")
        print("[LOG] Clicked Saved Policy Button")
        sleep(10)
        
        # Step 7: Confirm Insurance Banner
        next_btn = find_element_across_frames(page, 'button[name="CommonFlowActionButtons_pyWorkPage_32"]')
        if not next_btn:
            print("[ERROR]  Next button not found")
            raise Exception("Next button not found")
        next_btn.click()
        screenshot(page, "Clearance_step_8_clearance_next_btn")
        print("[LOG] Verify Insurance Banner and clicked Next")
        sleep(60)
        print("[LOG] Successfully Saved Payer and Policy Details")

        # Step 8: CoPay and Billing Split Setup
        print("[LOG] CoPay and Billing Split Setup")
        drug_checkbox = find_element_across_frames(page, '//span[@class="checkbox"]//input[@type="checkbox"]')
        if not drug_checkbox:
            print("[ERROR]  Drug field checkbox not found")
            raise Exception("Drug field checkbox not found")
        if not drug_checkbox.is_checked():
            drug_checkbox.check()
        screenshot(page, "Clearance_step_8_clearance_drug_checkbox")
        print("[LOG] Clicked Drug Checkbox and waiting for primary payer details")
        print("[LOG] Waiting for Page load")
        sleep(60)


        primary_payer_input = find_element_across_frames(page, 'input[data-test-id="202006170412060535921"]')
        if not primary_payer_input:
            print("[ERROR]  Primary Payer Service input not found")
            raise Exception("Primary Payer Service input not found")
        primary_payer_input.clear()
        primary_payer_input.fill("1730")
        print("[LOG] Filled Primary Payer Input")
        sleep(3)
        page.keyboard.press("ArrowDown")
        sleep(2)
        page.keyboard.press("Enter")
        screenshot(page, "Clearance_step_8_clearance_primary_payer_input")
        sleep(5)

        # Step 9: Co-Pay Split Setup
        copay_input = find_element_across_frames(page, 'select[data-test-id="20200313110855039235493"]')
        if not copay_input:
            copay_input = find_element_across_frames(page, 'select[name="$PpyWorkPage$pBillingSplitServices$l1$pCoPay$l1$pAssignCoPayTo"]')
            if not copay_input:
                print("[ERROR]  CoPay input not found")
                raise Exception("CoPay input not found")
        copay_input.select_option(value="P")
        screenshot(page, "Clearance_step_8_clearance_copay_input")
        print("[LOG] Completed Co-Pay split setup")
        sleep(3)

        # Step 10: Complete the Clearance Task
        finish_btn = find_element_across_frames(page, '//span/button[text()="Finish"]')
        if not finish_btn:
            print("[ERROR]  Finish button not found")
            raise Exception("Finish button not found")
        finish_btn.click()
        print("[LOG] Clicked finish button")
        screenshot(page, "Clearance_step_8_clearance_finish")
        print("[LOG] Waiting for Page load")
        sleep(15)
        print("[LOG] Completed Clearance Task Sucessfully")
    """

    user_input = f"""

    <element_reference_code>
    {element_reference_code}
    </element_reference_code>

    Application name : clearance
    <INFO>
    Url -> https://clearance-qa.express-scripts.com/spclr
    patient id:{patient_id}
    </INFO>


    <Your task>
    {steps}
    </Your task>
    """

    messages = [ SystemMessage(system_prompt_script_generation), HumanMessage(user_input) ]

    with get_openai_callback() as cb:
        llm_code = llm.invoke(messages).content
        print("---")
    print()
    print(f"Script - Clearance Total Tokens: {cb.total_tokens}")
    print(f"Script - Clearance Prompt Tokens: {cb.prompt_tokens}")
    print(f"Script - Clearance Completion Tokens: {cb.completion_tokens}")


    parsed_code = extract_python_code(llm_code)

    # Replace the placeholder values with actual patient_id
    parsed_code = parsed_code.replace("{patient_id}", f'"{patient_id}"')

    return parsed_code