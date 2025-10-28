#from adapters.llm_adapters import get_azure_llm
from nodes.adapters.llm_adapters import get_azure_llm
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from pprint import pprint
import re
import dotenv
#from nodes.rxp_agent_utils import iterative_search_for_element
from langchain_community.callbacks import get_openai_callback
import oracledb


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

def generate_rxp_code_reject(patient_id,steps):
    
    llm = get_azure_llm("ai-coe-gpt41",temperature=0.0)

    output_example = """
    You are an expert Python Playwright automation engineer. Your job is to generate a complete Python Playwright function that automates a given scenario. You must follow all instructions and best practices outlined below.

    **Instructions:**
	1) Read the given {steps} and extract only steps for RxP application.
    2) Use {steps} only for input fields.DO NOT ANY NEW STEP in element_reference_code.
    3) ALWAYS Verify the input fields in the {steps} for example check values for SIG,NDC etc. and use it in the script.
    4) These input will change in the automation script according to the scenario but the element_reference_code logic will be the same- DO NOT use the patient id given in {steps}
    5) ALWAYS Replace patient id given in the {steps} with {patient_id} passed as input in this function. DO NOT PUT ANY PLACEHOLDERS. The {patient_id} will be replaced with the actual value later.
    6) ALWAYS USE element_reference_code as it is except the input fields. DO NOT ADD YOUR OWN LOGIC.DO NOT HALLUCINATE
    7) DO NOT CHANGE ANYTHING in the element_reference_code logic except the input values that are already there and replace according to the above given instructions.DO NOT HALLUCINATE.
    8) element_reference_code is your working template to fill in the input values give in the {steps} that is passed as input. FOLLOW THE FUNCTION SIGNATURE EXACTLY AS SHOWN IN THE ELEMENT_REFERENCE_CODE.
    9) Generate a Python function named `def test_step_rxp(page_with_video): ...` that performs the scenario steps provided. DO NOT add any parameters to the function signature.
    10) Always begin the function by navigating to the initial page using `page.goto(initial_url)` (the initial_url will be given as a variable).
    11)For any element that could be inside a frame, always use ONLY the provided `find_element_across_frames` utility. Never use `page.locator()` or access frames directly.
    12)ALWAYS Use appropriate logs and wait time as given in the element_reference_code
    13)For Advanced search always use advanced_search and post_order_entry_advanced_search from the import rxp_agent_utils
    14)element_reference_code is an working playwright code given as reference for latest elements in the application.
    15)If an element is not found, raise an Exception with a clear message.
    16)ALWAYS use the same wait/sleep time as given in the element_reference_code.DO NOT CHANGE while generating automation scripts.
    17)ALWAYS add screenshots similar to how it is given in element_reference_code.DO NOT SKIP THIS.
	18)Only output valid Python code for the full function (imports plus function) and nothing else -- no explanation or markdown.
    19)Use selector path or logic has been provided to you in 'SELECTOR CHANGES'. Use given selector paths or logic for respective selector only.
    20)** IMPORTANT ** DO NOT INCLUDE ADDITIONAL FUNCTION FOR SCREENSHOTS. THESE UTILIIY FUNCTIONS WILL BE ADDED AS IMPORTS LATER MANUALLY.
    21)** DO NOT INCLUDE THESE STEPS** - This SHOULD NOT BE PART OF AUTOMATION SCRIPT for any scenario.

    # Step 5: Prescriber Section - Clear, Search NPI, Select Phone/Fax, Submit
    prescriber_clear_btn = find_element_across_frames(page, "//button[normalize-space()='Clear']")
    if prescriber_clear_btn:
        robust_click(page, prescriber_clear_btn)
        print("[LOG] Clicked 'Clear' in Prescriber section")
        sleep(2)
        screenshot(page, "RxP_step_22_prescriber_clear_clicked.png")

    npi_input = find_element_across_frames(page, "//input[@name='$PPrescriberSearch$ppySearchText']")
    if npi_input:
        robust_fill(page, npi_input, "1336183888")
        print("[LOG] Entered NPI '1336183888'")
        sleep(2)
        screenshot(page, "RxP_step_23_npi_entered.png")

    prescriber_search_btn = find_element_across_frames(page, "//button[normalize-space(text())='Search']")
    if prescriber_search_btn:
        robust_click(page, prescriber_search_btn)
        print("[LOG] Clicked 'Search' in Prescriber section")
        page.wait_for_load_state("networkidle")
        sleep(5)
        screenshot(page, "RxP_step_24_prescriber_search_clicked.png")

    phone_radio = find_element_across_frames(page, "//input[@type='radio' and contains(@name, 'Phone')]")
    if phone_radio:
        robust_click(page, phone_radio)
        print("[LOG] Selected phone radio button")
        sleep(1)
        screenshot(page, "RxP_step_25_phone_radio_selected.png")

    fax_radio = find_element_across_frames(page, "//input[@type='radio' and contains(@name, 'Fax')]")
    if fax_radio:
        robust_click(page, fax_radio)
        print("[LOG] Selected fax radio button")
        sleep(1)
        screenshot(page, "RxP_step_26_fax_radio_selected.png")

    prescriber_submit_btn = find_element_across_frames(page, "//button[normalize-space()='Submit']")
    if prescriber_submit_btn:
        robust_click(page, prescriber_submit_btn)
        print("[LOG] Clicked 'Submit' in Prescriber section")
        page.wait_for_load_state("networkidle")
        sleep(5)
        screenshot(page, "RxP_step_27_prescriber_submit_clicked.png")
	    
    11. **LOGIN**
    * USERNAME will be always LAN_ID and password is always LAN_PASSWORD

    12.  **Output Format**: Only output valid, complete Python code that includes the necessary imports and the full function definition. Do not add any explanations or markdown formatting.
    13. ** IMPORTANT ** DO NOT INCLUDE ADDITIONAL LOGIC FOR SCREENSHOTS, Sleep etc. 
    ---

    ### **EXAMPLE**

    **Given:**

    `initial_url` = "https://example.com/login"

    USERNAME = LAN_ID
    PASSWORD = LAN_PASSWORD

    PATIENT_ID = {patient_id}
    
    `Selectors Mapping:`
    *   `userName`: `input[name="UserIdentifier"]`
    *   `password`: `input[name="Password"]`
    *   `login`: `button#sub`

    `Scenario Steps:`
    1.  Go to the login page.
    2.  Enter Username and Password, then click Login.
    3.  Click Search Cases.

    ---

    **Required Output:**

    from nodes.rxp_agent_utils import find_element_across_frames, robust_fill, robust_click, robust_select_option, switch_to_window_by_index, switch_to_window_by_title, wait_for_new_window


    def test_step_rxp(page_with_video):

        USERNAME = LAN_ID
        PASSWORD = LAN_PASSWORD

        PATIENT_ID = {patient_id}

        # Step 1: Navigate to the login page (NAVIGATION - REQUIRES WAIT)
		page = page_with_video
        page.goto("https://example.com/login")
        print("[LOG] Navigated to https://example.com/login")
        page.wait_for_load_state("networkidle")
        sleep(2)
        screenshot(page,"step_1_navigate_to_login.png")

        # Step 2: Fill username (FORM FILL - MINIMAL WAIT)
        username_input = find_element_across_frames(page, 'input[name="UserIdentifier"]')
        if not username_input:
            print("[ERROR] 'Username' not found")
            raise Exception("Element 'Username' not found")
        robust_fill(page, username_input, USERNAME)
        print("[LOG] Filled 'Username'")
        sleep(0.5)
        screenshot(page,"step_2_fill_username.png")

        # Step 3: Fill password (FORM FILL - MINIMAL WAIT)
        password_input = find_element_across_frames(page, 'input[name="Password"]')
        if not password_input:
            print("[ERROR] 'Password' not found")
            raise Exception("Element 'Password' not found")
        robust_fill(page, password_input, PASSWORD)
        print("[LOG] Filled 'Password'")
        sleep(0.5)
        screenshot(page,"step_3_fill_password.png")

        # Step 4: Click login button (NAVIGATION - REQUIRES WAIT)
        login_btn = find_element_across_frames(page, 'button#sub')
        if not login_btn:
            print("[ERROR] 'Login Button' not found")
            raise Exception("Element 'Login Button' not found")
        robust_click(page, login_btn)
        print("[LOG] Clicked the 'Login' button")
        page.wait_for_load_state("networkidle")
        sleep(2)
        screenshot(page,"step_4_after_login_click.png")

        # Step 5: Click Search Cases link (NAVIGATION - REQUIRES WAIT)
        search_cases_link = find_element_across_frames(page, 'a[name="SearchUtilities_pyDisplayHarness_5"]')
        if not search_cases_link:
            print("[ERROR] 'Search Cases' not found")
            raise Exception("Element 'Search Cases' not found ")
        robust_click(page, search_cases_link)
        print("[LOG] Clicked the 'Search Cases' link")
        page.wait_for_load_state("networkidle")
        sleep(2)
        screenshot(page,"step_5_after_search_click.png")
    """
    system_prompt_script_generation = f"""{output_example}"""

    rxp_elements = """# Essential RxP Selectors

    ## Login Elements
    - Username: input#txtUserID
    - Password: input#txtPassword  
    - Login Button: button#sub

    ## Advanced Search
    - Advanced Search Link: //*[text()='Advanced Search']
    - RxHome ID Field: [data-test-id="20180715225236062436158"]
    - Search Button: //*[@node_name='DisplayAdvanceSearchParameters']//following::*[@name='DisplaySearchWrapper_D_AdvanceSearch_15']
    - Open Case Button: [data-test-id='20201119155820006856367']

    ## Order Entry
    - Begin Button: [data-test-id='201609091025020567152987']
    - Link Image Button: //button[normalize-space(.)='Link Image in Viewer']
    - DAW Dropdown: //*[normalize-space(text())='DAW Code']/ancestor-or-self::*[contains(@class,'dataLabelFor')]/following-sibling::*//select
    - Search Drug Button: [data-test-id='20170901173456065136464']
    - NDC Dropdown: [data-test-id='20200925062850019643650']
    - Drug Search Input: //input[@name='$PDrugSearch$ppySearchText']
    - Drug Search Button: //button[normalize-space(text())='Search']
    - Drug Result Row: //*[@id="$PDrugSearchResults$ppxResults$l1"]/td[3]
    - Submit Drug Button: //button[@data-test-id='201707060845020891147506' and normalize-space()='Submit']

    ## Prescription Details
    - Common SIG Button: //button[normalize-space(.)='Common SIG']
    - SIG Option: //span[normalize-space(text())='INJECT 40 MG (0.4 ML) UNDER THE SKIN EVERY 2 WEEKS']
    - Quantity Input: input[data-test-id="2019062103515309648629"]
    - Days Supply Input: input[data-test-id="20190621040342079260489"]
    - Doses Input: input[data-test-id="20190621040342079263702"]
    - Refills Input: input[data-test-id="2019062104034207926431"]
    - Apply Rules Button: //button[normalize-space(.)='Apply Rules']
    - Reviewed Button: //button[normalize-space(.)='Reviewed']

    ## Validation Checkboxes
    - Patient Checkbox: //input[@data-test-id='202303231536300910155360']
    - Medication Checkbox: //input[@data-test-id='20230324144929033857959']
    - Rx Details Checkbox: //input[@data-test-id='20230324171608002687320']
    - Prescriber Checkbox: //input[@data-test-id='202303271403440493899139']

    ## Navigation
    - Next Button: //button[normalize-space()='Next >>']
    - Close Button: //button[normalize-space() = 'Close']
    - Submit Button: //button[normalize-space()='Submit' or normalize-space()='submit']

    ## RPh Verification
    - Verify Buttons: //button[normalize-space()='Verify']
    - DUR Resolution: "RPh Approved Professional Judgement"

    # Key Validation Fields

    ## Patient Section
    - Full Name: //span[normalize-space()='Full name']/following-sibling::div/span
    - DOB: //span[normalize-space()='DOB']/following-sibling::div/span
    - Gender: //span[normalize-space()='Gender']/following-sibling::div/span
    - Age: //span[normalize-space()='Age']/following-sibling::div/span
    - Address: //span[normalize-space()='Address']/following-sibling::div/span
    - Phone: //span[normalize-space()='Phone']/following-sibling::div/span

    ## Medication Section
    - Prescribed Drug: //span[normalize-space()='Prescribed Drug']/following-sibling::div/span
    - Dispensed Drug: //span[normalize-space()='Dispensed Drug']/following-sibling::div/span
    - Comments: //span[normalize-space()='Dispensed Drug Comments']/following-sibling::div/span

    ## Rx Details Section
    - SIG Text: //span[normalize-space()='SIG Text']/following-sibling::div/span
    - Prescribed Qty: //span[normalize-space()='Prescribed Quantity']/following-sibling::div/span
    - Prescribed Days: //span[normalize-space()='Prescribed Days Supply']/following-sibling::div/span
    - Prescribed Doses: //span[normalize-space()='Prescribed Doses']/following-sibling::div/span
    - Prescribed Refills: //span[normalize-space()='Prescribed Refills']/following-sibling::div/span
    - Dispensed Qty: //span[normalize-space()='Dispensed Quantity']/following-sibling::div/span
    - Dispensed Days: //span[normalize-space()='Dispensed Days Supply']/following-sibling::div/span
    - Dispensed Doses: //span[normalize-space()='Dispensed Doses']/following-sibling::div/span
    - Dispensed Refills: //span[normalize-space()='Dispensed Refills']/following-sibling::div/span
    - Date Written: //span[normalize-space()='Date Written']/following-sibling::div/span
    - Rx Expires: //span[normalize-space()='Rx Expires']/following-sibling::div/span
    - DAW Code: //span[normalize-space()='DAW Code']/following-sibling::div/span
    - Rx Origin: //span[normalize-space()='Rx Origin Code']/following-sibling::div/span

    ## Prescriber Section
    - Prescriber: //span[@data-test-id='202008271512120392583911']
    - Prescriber ID: //div[normalize-space()='Prescriber ID']/following-sibling::div//span[@class='esitextinput']
    - Address: //span[normalize-space()='Address']/following-sibling::div//span[contains(@class, 'esitextinput')]
    - Phone: //span[normalize-space()='Phone']/following-sibling::div/span[contains(@class, 'esitextinput')]
    - NPI: //span[normalize-space()='NPI']/following-sibling::div/span
    - DEA: //span[normalize-space()='DEA']/following-sibling::div/span
    - Fax: //span[normalize-space()='Fax']/following-sibling::div/span
    - Fax N/A Checkbox: //span[normalize-space()='Fax N/A']/following::input[@type='checkbox'][1]""" 

    element_reference_code = """

from nodes.rxp_agent_utils import wait_for_new_window,find_element_across_frames, robust_fill, advanced_search, robust_click, post_order_entry_advanced_search, robust_select_option, switch_to_window_by_index, find_and_click_begin_button_with_retry, validate_section_and_check
from time import sleep

def post_edit_advance_search(page,PATIENT_ID):
    adv_search_link = find_element_across_frames(page, "a[data-test-id='201807151828330613289695']")
    if not adv_search_link:
        raise Exception("Element 'Advanced Search' link not found")
    
    # Use wait_for_new_window to properly handle the new window opening
    def click_advanced_search():
        robust_click(page, adv_search_link)
        print("[LOG] Clicked Advanced Search")
    
    try:
        adv_search_page = wait_for_new_window(page, click_advanced_search, timeout=15000)
        print(f"[LOG] Advanced Search window opened with URL: {adv_search_page.url}")
        sleep(15)
    except Exception as e:
        print(f"[ERROR] Failed to open Advanced Search window: {e}")
        raise Exception("Advanced Search window did not open properly")
    sleep(10)

    rxhome_id_field = find_element_across_frames(adv_search_page, '[data-test-id="20180715225236062436158"]')
    if not rxhome_id_field:
        raise Exception("Element 'RxHome ID' field not found")
    robust_fill(adv_search_page, rxhome_id_field, PATIENT_ID)
    print(f"[LOG] Entered Patient ID: {PATIENT_ID}")
    print(f"[LOG] Current Advanced Search page URL: {adv_search_page.url}")
    sleep(10)

    for attempt in range(20):

        try:

            search_btn = find_element_across_frames(
            adv_search_page, "//*[@node_name='DisplayAdvanceSearchParameters']//following::*[@name='DisplaySearchWrapper_D_AdvanceSearch_15']")
            if not search_btn:
                raise Exception("Element 'Search Button' not found")
            robust_click(adv_search_page, search_btn)
            print("[LOG] Clicked Search button in Advanced Search window")
            adv_search_page.wait_for_load_state("networkidle")
            print(f"[LOG] After search, Advanced Search page URL: {adv_search_page.url}")
            sleep(2)
            
            open_case_xpath = "[data-test-id='20201119155820006856367']"
            open_case_btn = find_element_across_frames(adv_search_page, open_case_xpath)
            print("*******",open_case_btn)
            if open_case_btn:
                robust_click(adv_search_page, open_case_btn)
                print("[LOG] Clicked Open Case button row")
                print(f"[LOG] After clicking open case, Advanced Search page URL: {adv_search_page.url}")
                sleep(13)
                break
            else:
                print(f"[LOG] Open Case button not found. Retrying after 30 seconds... attempt {attempt+1}")
                sleep(30)
        except Exception as e:
            print(f"[LOG] Error on attempt {attempt+1}: {e}")
            sleep(30)
        
    if not open_case_btn:
        raise Exception("Open Case button not found after maximum attempts")

    adv_search_page.close()
    print("[LOG] Closed Advanced Search window. Switching back to main window")
    switch_to_window_by_index(page, 0)
    sleep(20)    

def test_rxp_code(page_with_video):

    PATIENT_ID = {patient_id}
    USERNAME = LAN_ID
    PASSWORD = LAN_PASSWORD

    page = page_with_video

    # Step 1: Login to RxP
    page.goto("https://sprxp-qa.express-scripts.com/sprxp")
    print("[LOG] Navigated to RxP login page")
    page.wait_for_load_state("networkidle")
    sleep(5)
    screenshot(page, "RxP_step_1_login_page.png")

    username_input = find_element_across_frames(page, "input#txtUserID")
    if not username_input:
        print("[ERROR]  Element Username Input not found")
        raise Exception("Element 'Username Input' not found")
    robust_fill(page, username_input, USERNAME)
    print("[LOG] Username filled")
    sleep(5)
    screenshot(page, "RxP_step_2_username_filled.png")

    password_input = find_element_across_frames(page, "input#txtPassword")
    if not password_input:
        print("[ERROR]  Element Password Input not found")
        raise Exception("Element 'Password Input' not found")
    robust_fill(page, password_input, PASSWORD)
    print("[LOG] Password filled")
    sleep(5)
    screenshot(page, "RxP_step_3_password_filled.png")

    login_button = find_element_across_frames(page, "button#sub")
    if not login_button:
        print("[ERROR]  Element Login Input not found")
        raise Exception("Element 'Login' button not found")
    robust_click(page, login_button)
    print("[LOG] Clicked Login button")
    page.wait_for_load_state("networkidle")
    sleep(5)
    screenshot(page, "RxP_step_4_after_login.png")
    print("[LOG] Logged Successfully in RxP")

    # Step 2: Advanced Search for Patient Case
    print("[LOG] Order Entry Step in Progress")
    element_name = "[data-test-id='20201119155820006856367']"
    status_name = "Pending-OrderEntry"
    advanced_search(page, element_name, status_name, PATIENT_ID)
    screenshot(page, "RxP_step_5_advanced_search.png")
    sleep(10)

    # Step 3: Open Case and Begin Order Entry
    find_and_click_begin_button_with_retry(page, "Begin")
    sleep(10)

    # Step 4: Order Entry - Link Image, DAW, Drug, SIG, Details
    link_image_btn = find_element_across_frames(page, "//button[normalize-space(.)='Link Image in Viewer']")
    if not link_image_btn:
        print("[ERROR]  Element Link Image in Viewer button not found")
        raise Exception("Element 'Link Image in Viewer' button not found")
    robust_click(page, link_image_btn)
    print("[LOG] Clicked 'Link Image in Viewer'")
    page.wait_for_load_state("networkidle")
    sleep(5)
    screenshot(page, "RxP_step_10_link_image_in_viewer.png")

    daw_dropdown = find_element_across_frames(page, "//*[normalize-space(text())='DAW Code']/ancestor-or-self::*[contains(@class,'dataLabelFor')]/following-sibling::*//select")
    if not daw_dropdown:
        print("[ERROR]  Element DAW Code Dropdown not found")
        raise Exception("Element 'DAW Code Dropdown' not found")
    robust_select_option(page, daw_dropdown, "0 - No Product Selection Indicated")
    print("[LOG] Selected DAW code '0 - No Product Selection Indicated'")
    sleep(5)
    screenshot(page, "RxP_step_11_daw_code_selected.png")

    search_drug_btn = find_element_across_frames(page, "[data-test-id='20170901173456065136464']")
    if not search_drug_btn:
        print("[ERROR]  Element Search Drug not found")
        raise Exception("Element 'Search Drug' button not found")
    robust_click(page, search_drug_btn)
    print("[LOG] Clicked 'Search Drug' button")
    page.wait_for_load_state("networkidle")
    sleep(5)
    screenshot(page, "RxP_step_12_search_drug_clicked.png")

    ndc_dropdown = find_element_across_frames(page, "[data-test-id='20200925062850019643650']")
    if not ndc_dropdown:
        print("[ERROR]  Element NDC Dropdown not found")
        raise Exception("Element 'NDC Dropdown' not found")
    robust_select_option(page, ndc_dropdown, "NDC")
    print("[LOG] Selected NDC search option")
    sleep(5)
    screenshot(page, "RxP_step_13_ndc_selected.png")

    drug_search_input = find_element_across_frames(page, "//input[@name='$PDrugSearch$ppySearchText']")
    if not drug_search_input:
        print("[ERROR]  Element Drug Search Input not found")
        raise Exception("Element 'Drug Search Input' not found")
    robust_fill(page, drug_search_input, "00378696093")
    print("[LOG] Entered NDC '00378696093'")
    sleep(5)
    screenshot(page, "RxP_step_14_drug_ndc_entered.png")

    modal_search_btn = find_element_across_frames(page, "//button[normalize-space(text())='Search']")
    if not modal_search_btn:
        print("[ERROR]  Element Modal Search Button not found")
        raise Exception("Element 'Modal Search Button' not found")
    robust_click(page, modal_search_btn)
    print("[LOG] Clicked Drug Search in modal")
    page.wait_for_load_state("networkidle")
    sleep(5)
    screenshot(page, "RxP_step_15_modal_search_clicked.png")

    drug_row = find_element_across_frames(page, '//*[@id="$PDrugSearchResults$ppxResults$l1"]/td[3]')
    if not drug_row:
        print("[ERROR]  Drug result row not found")
        raise Exception("Drug result row not found")
    robust_click(page, drug_row)
    print("[LOG] Selected GLAT drug row by NDC")
    sleep(5)
    screenshot(page, "RxP_step_16_humira_ndc_selected.png")

    submit_drug_btn = find_element_across_frames(
        page, "//button[@data-test-id='201707060845020891147506' and normalize-space()='Submit']"
    )
    if not submit_drug_btn:
        print("[ERROR]  Element Submit button in modal not found")
        raise Exception("Element 'Submit' button in modal not found")
    robust_click(page, submit_drug_btn)
    print("[LOG] Clicked 'Submit' in drug search modal")
    page.wait_for_load_state("networkidle")
    sleep(20)
    screenshot(page, "RxP_step_17_submit_modal.png")

    # Common SIG
    common_sig_btn = find_element_across_frames(page, "//button[normalize-space(.)='Common SIG']")
    if not common_sig_btn:
        print("[ERROR]  Common SIG button not found")
        raise Exception("Common SIG button not found")
    robust_click(page, common_sig_btn)
    print("[LOG] Clicked 'Common SIG' button")
    sleep(5)
    screenshot(page, "RxP_step_18_common_sig_clicked.png")

    sig_option = find_element_across_frames(page, "//span[normalize-space(text())='INJECT 20 MG (1 ML) UNDER THE SKIN DAILY']")
    if not sig_option:
        print("[ERROR]  SIG option not found")
        raise Exception("SIG option not found")
    robust_click(page, sig_option)
    print("[LOG] SIG option selected")
    sleep(5)
    screenshot(page, "RxP_step_19_sig_selected.png")

    qty_input = find_element_across_frames(page, 'input[data-test-id="2019062103515309648629"]')
    if not qty_input:
        print("[ERROR]  Qty input not found")
        raise Exception("Qty input not found")
    robust_fill(page, qty_input, "1")
    print("[LOG] Qty set to 1")
    sleep(5)
    screenshot(page, "RxP_step_20_qty_entered.png")

    days_input = find_element_across_frames(page, 'input[data-test-id="20190621040342079260489"]')
    if not days_input:
        print("[ERROR]  Days Supply input not found")
        raise Exception("Days Supply input not found")
    robust_fill(page, days_input, "14")
    print("[LOG] Days Supply set to 14")
    sleep(5)
    screenshot(page, "RxP_step_21_days_supply_entered.png")

    doses_input = find_element_across_frames(page, 'input[data-test-id="20190621040342079263702"]')
    if not doses_input:
        print("[ERROR]  Doses input not found")
        raise Exception("Doses input not found")
    robust_fill(page, doses_input, "1")
    print("[LOG] Doses set to 1")
    sleep(5)
    screenshot(page, "RxP_step_22_doses_entered.png")

    refills_input = find_element_across_frames(page, 'input[data-test-id="2019062104034207926431"]')
    if not refills_input:
        print("[ERROR]  Refills input not found")
        raise Exception("Refills input not found")
    robust_fill(page, refills_input, "1")
    print("[LOG] Refills set to 1")
    sleep(5)
    screenshot(page, "RxP_step_23_refills_entered.png")

    apply_rules_btn = find_element_across_frames(page, "//button[normalize-space(.)='Apply Rules']")
    if not apply_rules_btn:
        print("[ERROR]  Element Apply Rules button not found")
        raise Exception("Element 'Apply Rules' button not found")
    robust_click(page, apply_rules_btn)
    print("[LOG] Clicked 'Apply Rules'")
    page.wait_for_load_state("networkidle")
    sleep(30)
    screenshot(page, "RxP_step_24_apply_rules_clicked.png")

    reviewed_btn = find_element_across_frames(page, "//button[normalize-space(.)='Reviewed']")
    if not reviewed_btn:
        print("[ERROR]  Element Reviewed button not found")
        raise Exception("Element 'Reviewed' button not found")
    robust_click(page, reviewed_btn)
    print("[LOG] Clicked 'Reviewed'")
    page.wait_for_load_state("networkidle")
    sleep(5)
    screenshot(page, "RxP_step_25_reviewed_clicked.png")

    accept_changes_btn = find_element_across_frames(page, "//button[normalize-space(.)='Accept Changes']")
    if accept_changes_btn:
        robust_click(page, accept_changes_btn)
        print("[LOG] Clicked 'Accept Changes'")
        page.wait_for_load_state("networkidle")
        sleep(5)
        screenshot(page, "RxP_step_26_accept_changes_clicked.png")
    
    # A new reviewed button was added here.
    reviewed_btn = find_element_across_frames(page, "//button[normalize-space(.)='Reviewed']")
    if not reviewed_btn:
        pass
        # raise Exception("Element 'Reviewed' button not found")
    else:
        robust_click(page, reviewed_btn)
        print("[LOG] Clicked 'Reviewed'")
        page.wait_for_load_state("networkidle")
        sleep(5)

    # Step 5: Validate Auto populated data for Each Section
    print("[LOG] Validating Auto populated data in Patient Section")
    # Patient Section
    patient_fields = [
        ("Full Name", "//span[normalize-space()='Full name']/following-sibling::div/span"),
        ("DOB", "//span[normalize-space()='DOB']/following-sibling::div/span"),
        ("Gender", "//span[normalize-space()='Gender']/following-sibling::div/span"),
        ("Age", "//span[normalize-space()='Age']/following-sibling::div/span"),
        ("Address", "//span[normalize-space()='Address']/following-sibling::div/span"),
        ("Phone", "//span[normalize-space()='Phone']/following-sibling::div/span"),
    ]
    patient_checkbox = "//input[@data-test-id='202303231536300910155360']"
    validate_section_and_check(page, patient_fields, patient_checkbox)
    ## screenshot(page, "RxP_step_27_patient_section_checked.png")
    sleep(5)

    # Medication Section
    print("[LOG] Validating Auto populated data in Medication Section")
    med_fields = [
        ("Prescribed Drug", "//span[normalize-space()='Prescribed Drug']/following-sibling::div/span"),
        ("Dispensed Drug", "//span[normalize-space()='Dispensed Drug']/following-sibling::div/span"),
        ("Dispensed Drug Comments", "//span[normalize-space()='Dispensed Drug Comments']/following-sibling::div/span"),
    ]
    opt_med_fields = ["Dispensed Drug Comments"]
    med_checkbox = "//input[@data-test-id='20230324144929033857959']"
    validate_section_and_check(page, med_fields, med_checkbox, opt_med_fields)
    ## screenshot(page, "RxP_step_28_med_section_checked.png")
    sleep(5)

    # Rx Details Section
    print("[LOG] Validating Auto populated data in Rx Details Section")
    rx_details_fields = [
        ("SIG Text", "//span[normalize-space()='SIG Text']/following-sibling::div/span"),
        ("Prescribed Quantity", "//span[normalize-space()='Prescribed Quantity']/following-sibling::div/span"),
        ("Prescribed Days Supply", "//span[normalize-space()='Prescribed Days Supply']/following-sibling::div/span"),
        ("Prescribed Doses", "//span[normalize-space()='Prescribed Doses']/following-sibling::div/span"),
        ("Prescribed Refills", "//span[normalize-space()='Prescribed Refills']/following-sibling::div/span"),
        ("Dispensed Quantity", "//span[normalize-space()='Dispensed Quantity']/following-sibling::div/span"),
        ("Dispensed Days Supply", "//span[normalize-space()='Dispensed Days Supply']/following-sibling::div/span"),
        ("Dispensed Doses", "//span[normalize-space()='Dispensed Doses']/following-sibling::div/span"),
        ("Dispensed Refills", "//span[normalize-space()='Dispensed Refills']/following-sibling::div/span"),
        ("Date Written", "//span[normalize-space()='Date Written']/following-sibling::div/span"),
        ("Rx Expires", "//span[normalize-space()='Rx Expires']/following-sibling::div/span"),
        ("DAW Code", "//span[normalize-space()='DAW Code']/following-sibling::div/span"),
        ("Rx Origin Code", "//span[normalize-space()='Rx Origin Code']/following-sibling::div/span"),
    ]
    rx_details_checkbox = "//input[@data-test-id='20230324171608002687320']"
    validate_section_and_check(page, rx_details_fields, rx_details_checkbox)
    ## screenshot(page, "RxP_step_29_rx_details_checked.png")
    sleep(5)

    # Prescriber Section
    print("[LOG] Validating Auto populated data in Prescriber Section")
    prescriber_fields = [
        ("Prescriber", "//span[@data-test-id='202008271512120392583911']"),
        ("Prescriber ID", "//div[normalize-space()='Prescriber ID']/following-sibling::div//span[@class='esitextinput']"),
        ("Address", "//span[normalize-space()='Address']/following-sibling::div//span[contains(@class, 'esitextinput')]"),
        ("Phone", "//span[normalize-space()='Phone']/following-sibling::div/span[contains(@class, 'esitextinput')]"),
        ("NPI", "//span[normalize-space()='NPI']/following-sibling::div/span"),
        ("DEA", "//span[normalize-space()='DEA']/following-sibling::div/span"),
    ]
    prescriber_checkbox = "//input[@data-test-id='202303271403440493899139']"
    validate_section_and_check(page, prescriber_fields, prescriber_checkbox)
    screenshot(page, "RxP_step_30_prescriber_section_checked.png")
    sleep(5)

    # Fax N/A (if Fax is blank)
    fax_element = find_element_across_frames(page, "//span[normalize-space()='Fax']/following-sibling::div/span")
    if fax_element and not fax_element.inner_text().strip():
        fax_na_checkbox = find_element_across_frames(page, "//span[normalize-space()='Fax N/A']/following::input[@type='checkbox'][1]")
        if fax_na_checkbox:
            robust_click(page, fax_na_checkbox)
            print("[LOG] Clicked Fax N/A checkbox")
        screenshot(page, "RxP_step_31_fax_na_checked.png")
        sleep(5)

    # Step 6: Next (Trend Processing)
    
    next_btn = find_element_across_frames(page, "//button[normalize-space()='Next >>']")
    if not next_btn:
        print("[ERROR]  Next button not found")
        raise Exception("Next button not found")
    sleep(2)
    robust_click(page, next_btn)
    print("[LOG] Clicked Next for Trend Processing")
    page.wait_for_load_state("networkidle")
    screenshot(page, "RxP_step_32_next_clicked.png")
    print("[LOG] Completed Order Entry")
    sleep(10)

    close_btn = find_element_across_frames(page, "[name='pyCaseHeader_pyWorkPage_33']")
    robust_click(page, close_btn)
    print("[LOG] Clicked close button")
    sleep(30)

    
    element_name ="//span[contains(text(), 'Pending-EditMessages')]/ancestor::tr//button[@data-test-id='20201119155820006856367']"
    status_name = "Order Entry Pending Edits"
    post_order_entry_advanced_search(page,element_name,status_name,PATIENT_ID)
    screenshot(page, "RxP_step_35_advanced_search.png")
    sleep(10)
    print("[LOG] Pending Order Entry Open Case")

    # Step 4: Begin Order Entry
    find_and_click_begin_button_with_retry(page, "Begin")
    sleep(10)
    
    submit_btn = find_element_across_frames(page, "[data-test-id='201503030125200963285390']")
    robust_click(page, submit_btn)
    print("[LOG] Clicked 'Submit' button")
    screenshot(page, "RxP_step_37_submit_btn_clicked.png")
    sleep(30)
    print("[LOG] Submitted Order Entry")

    close_btn = find_element_across_frames(page, "[name='pyCaseHeader_pyWorkPage_33']")
    robust_click(page, close_btn)
    print("[LOG] Clicked close button")
    sleep(30)

    print("[LOG] Validating Reject 75 Status")
    element_name = "[data-test-id='20201119155820006856367']"
    status_name = "Rph Verification In Progress"
    post_order_entry_advanced_search(page, element_name, status_name, db_status_name,PATIENT_ID)
    screenshot(page, "RxP_step_38_advanced_search.png")
    sleep(10)

    #NEW CODE
    post_edit_advance_search(page,PATIENT_ID)

    adv_search_link = find_element_across_frames(page, "a[data-test-id='201807151828330613289695']")
    
    # Use wait_for_new_window to properly handle the new window opening
    def click_advanced_search():
        robust_click(page, adv_search_link)
        print("[LOG] Clicked Advanced Search")
    
    try:
        adv_search_page = wait_for_new_window(page, click_advanced_search, timeout=15000)
        print(f"[LOG] Advanced Search window opened with URL: {adv_search_page.url}")
        sleep(15)
    except Exception as e:
        print(f"[ERROR]  Failed to open Advanced Search window: {e}")
    sleep(10)

    rxhome_id_field = find_element_across_frames(adv_search_page, '[data-test-id="20180715225236062436158"]')
    robust_fill(adv_search_page, rxhome_id_field, PATIENT_ID)
    print(f"[LOG] Entered Patient ID: {PATIENT_ID}")
    print(f"[LOG] Current Advanced Search page URL: {adv_search_page.url}")
    sleep(10)

    screenshot(adv_search_page, "clicked_submit_button.png")

    adv_search_page.close()

    print("[LOG] Completed Reject Flow")"""

    user_input = f"""
    
    {rxp_elements}
    
    {element_reference_code}

    Application name : Rxp
    <INFO>
    patient id:{patient_id}
    </INFO>

    USERNAME: LAN_ID 
    PASSWORD: PASSWORD

    <Your task>
    {steps}
    </Your Task>
"""
    messages = [ SystemMessage(system_prompt_script_generation), HumanMessage(user_input) ]
    with get_openai_callback() as cb:
        llm_code = llm.invoke(messages).content
        print("---")
    print()

    print(f"Script - RxP Total Tokens: {cb.total_tokens}")
    print(f"Script - RxP Prompt Tokens: {cb.prompt_tokens}")
    print(f"Script - RxP Completion Tokens: {cb.completion_tokens}")
    parsed_code = extract_python_code(llm_code)
    
    # Replace the placeholder values with actual patient_id
    parsed_code = parsed_code.replace("{patient_id}", f'"{patient_id}"')
    
    return parsed_code
