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

def generate_crm_code(patient_id,steps):

	llm = get_azure_llm("ai-coe-gpt41",temperature=0.0)

	output_example = """
	You are an expert Python Playwright automation engineer. You will be given snippets of java selenium code. Your job is to generate playwright code for the given scenario.

	Instructions:
    1) Read the given {steps} and extract only steps for CRM application
    2) ALWAYS Replace patient id given in the {steps} with {patient_id} given as input in this function. DO NOT PUT ANY PLACEHOLDERS. The {patient_id} will be replaced with the actual value later.
	3) DO NOT change anything in the element_reference_code logic except the input values according to the above given instructions
    4) element_reference_code is your working template to fill in the input values according to the {steps} that is passed as input. FOLLOW THE FUNCTION SIGNATURE EXACTLY AS SHOWN IN THE ELEMENT_REFERENCE_CODE. DO NOT HALLUCINATE.
    5) ALWAYS USE logic in element_reference_code for selecting HUMIRA checkbox do not hallucinate or create on ur own.
	5) Generate a Python function named `def test_step_crm(page_with_video): ...` that performs the scenario steps provided. DO NOT add any parameters to the function signature.
    6) Always begin the function by navigating to the initial page using `page.goto(initial_url)` (the initial_url will be given as a variable).
    7)For any element that could be inside a frame, always use ONLY the provided `find_element_across_frames` utility. Never use `page.locator()` or access frames directly.
    8)ALWAYS Use appropriate logs and wait time as given in the element_reference_code
    9)Use the selectors exactly as provided in the selector mapping. Do not invent or modify selectors. If a selector is named "searchCases" with a value from the mapping, use that as the string.
    10)element_reference_code is an working playwright code given as reference for latest elements in the application.
    11)If an element is not found, raise an Exception with a clear message.
    12)ALWAYS use the same wait/sleep time as given in the element_reference_code.DO NOT CHANGE while generating automation scripts.
    13)Only output valid Python code for the full function (imports plus function) and nothing else -- no explanation or markdown.
    14)Use selector path or logic has been provided to you in 'SELECTOR CHANGES'. Use given selector paths or logic for respective selector only.
	15)After click login button 'login_btn' use sleep(8).
    16)Focus on elements and logic given in element_reference_code
    17)DO NOT CREATE any additional function for taking screenshot.
	18)** IMPORTANT ** DO NOT INCLUDE ADDITIONAL FUNCTION FOR SCREENSHOTS. THESE UTILIIY FUNCTIONS WILL BE ADDED AS IMPORTS LATER MANUALLY.
    19)Give atleast sleep(3) to each element.
	20)Use sleep(15) after confirm_add_tasks_btn 
	21)Some pages take lot of time to load. Use function rather than sleep which will wait for page to get load only then it will look for selectors.**
	22)If you are using add_task_btn.click() in for _ in range(30) then dont define add_task_btn.click() again  seperately.
	23)Focus on the format given in EXAMPLE. Apply this in final code.


	EXAMPLE

	Given:
	initial_url = "https://example.com/login"
    USERNAME = LAN_ID
    PASSWORD = LAN_PASSWORD
	login: button#sub
	searchCases: a[name="SearchUtilities_pyDisplayHarness_5"]

	Scenario Steps:
	1. Go to login page
	2. Enter Username and Password, then click Login
	3. Click Search Cases

	input_fields = {"Username": "demo", "Password": "demopass"}

	Output:

	from nodes.agent_utils import find_element_across_frames
	from time import sleep
	def test_step_crm(page_with_video):
 
		USERNAME = LAN_ID
		PASSWORD = LAN_PASSWORD
		page.goto("https://example.com/login")
		username = find_element_across_frames(page, 'input[name="UserIdentifier"]')
		if not username:
			print("[ERROR] 'Username' not found")
			raise Exception("Username input not found")
		username.fill("demo")
		print("[LOG] Filled username with demo")
		screenshot(page,"step_1_filled_username_with_demo.png")
		sleep(2)

		password = find_element_across_frames(page, 'input[name="Password"]')
		if not password:
			print("[ERROR] 'Password' not found")
			raise Exception("Password input not found")
		password.fill("demopass")
		print("[LOG] Filled password with demopass")
		screenshot(page,"step_1_filled_username_with_demo.png")
		sleep(2)

		login_btn = find_element_across_frames(page, 'button#sub')
		if not login_btn:
			print("[ERROR] 'Login' not found")
			raise Exception("Login button not found")
		login_btn.click()
		print("[LOG] Clicked on Login button")
		screenshot(page,"step_1_filled_username_with_demo.png")
		sleep(2)

		search_cases = find_element_across_frames(page, 'a[name="SearchUtilities_pyDisplayHarness_5"]')
		if not search_cases:
			print("[ERROR] 'Search Cases' not found")
			raise Exception("Search Cases link not found")
		search_cases.click()
		print("[LOG] Clicked search case link")
		screenshot(page,"step_1_filled_username_with_demo.png")
		sleep(2)

	END EXAMPLE
	"""

	system_prompt_script_generation = f"""{output_example}"""

	element_reference_code = """ 
from nodes.agent_utils import find_element_across_frames
from time import sleep

def test_step_crm(page_with_video):

    print("[LOG] TESTING INITIATED FOR CRM APPLICATION")

    PATIENT_ID = {patient_id}
    USERNAME = LAN_ID
    PASSWORD = LAN_PASSWORD
    initial_url = "https://spcrmqa-internal.express-scripts.com/spcrm88/"

    page = page_with_video

    # Step 1: Launch and Login to CRM
    page.goto(initial_url)
    print("[LOG] Navigated to CRM URL")
    screenshot(page, "CRM_step_1_navigated_to_crm_url.png")
    sleep(5)

    username = find_element_across_frames(page, "#txtUserID")
    if not username:
        print("[ERROR] Username input not found")
        raise Exception("Username input not found")
    username.fill(USERNAME)
    print("[LOG] Filled username")
    screenshot(page, "CRM_step_2_filled_username.png")
    sleep(3)

    password = find_element_across_frames(page, "#txtPassword")
    if not password:
        print("[ERROR] Password input not found")
        raise Exception("Password input not found")
    password.fill(PASSWORD)
    print("[LOG] Filled password")
    screenshot(page, "CRM_step_3_filled_password.png")
    sleep(3)

    login_btn = find_element_across_frames(page, "#sub")
    if not login_btn:
        print("[ERROR] Login button not found")
        raise Exception("Login button not found")
    login_btn.click()
    print("[LOG] Clicked Login button")
    screenshot(page, "CRM_step_4_clicked_login.png")
    sleep(8)

    # Step 2: Access Patient Verification & Caller Info
    new_btn = find_element_across_frames(page, '//a[normalize-space(.)="New"]')
    if not new_btn:
        print("[ERROR] New button not found")
        raise Exception("New button not found")
    new_btn.click()
    print("[LOG] Clicked New button")
    screenshot(page, "CRM_step_5_clicked_new.png")
    sleep(4)

    sim_ws_btn = find_element_across_frames(page, "//*[text()='Simulate Workspace Interaction']")
    if not sim_ws_btn:
        print("[ERROR] Simulate Workspace Interaction button not found")
        raise Exception("Simulate Workspace Interaction button not found")
    sim_ws_btn.click()
    print("[LOG] Clicked Simulate Workspace Interaction")
    screenshot(page, "CRM_step_6_clicked_simulate_workspace_interaction.png")
    sleep(30)

    patient_id_field = find_element_across_frames(page, 'input[id="a3f8064b"]')
    if not patient_id_field:
        print("[ERROR] Patient ID field not found")
        raise Exception("Patient ID field not found")
    try:
        patient_id_field.fill("")
        sleep(5)
    except Exception:
        pass
    patient_id_field.fill(str(PATIENT_ID))
    print(f"[LOG] Filled Patient ID with {PATIENT_ID}")
    screenshot(page, "CRM_step_7_filled_patient_id.png")
    sleep(2)

    call_intent_field = find_element_across_frames(page, 'input[id="5e9cabab"]')
    if not call_intent_field:
        print("[ERROR] Call Intent field not found")
        raise Exception("Call Intent field not found")
    try:
        call_intent_field.fill("")
        sleep(1)
    except Exception:
        pass

    prescription_no_field = find_element_across_frames(page, 'input[id="418aff81"]')
    if not prescription_no_field:
        print("[ERROR] Prescription Number field not found")
        raise Exception("Prescription Number field not found")
    try:
        prescription_no_field.fill("")
        sleep(1)
    except Exception:
        pass

    fill_no_field = find_element_across_frames(page, 'input[id="ac6e34af"]')
    if not fill_no_field:
        print("[ERROR] Fill Number field not found")
        raise Exception("Fill Number field not found")
    try:
        fill_no_field.fill("")
        sleep(1)
    except Exception:
        pass

    service_branch_field = find_element_across_frames(page, 'input[id="28d60f5c"]')
    if not service_branch_field:
        print("[ERROR] Service Branch field not found")
        raise Exception("Service Branch field not found")
    try:
        service_branch_field.fill("")
        sleep(1)
    except Exception:
        pass

    next_btn = find_element_across_frames(page, "[data-test-id='20201223000248034111750']")
    if not next_btn:
        print("[ERROR] Next button not found")
        raise Exception("Next button not found")
    next_btn.click()
    print("[LOG] Clicked Next button after entering Patient Info")
    screenshot(page, "CRM_step_8_clicked_next_patient_info.png")
    sleep(8)

    # Step 3: Verification & Medication Details
    verification_checkbox1 = find_element_across_frames(page, "(//input[@type='checkbox'])[1]")
    verification_checkbox2 = find_element_across_frames(page, "(//input[@type='checkbox'])[2]")
    verification_checkbox3 = find_element_across_frames(page, "(//input[@type='checkbox'])[3]")
    if not verification_checkbox1 or not verification_checkbox2 or not verification_checkbox3:
        print("[ERROR] required verification checkbox not found")
        raise Exception("A required verification checkbox not found")
    verification_checkbox1.check()
    print("[LOG] Checked first Verification Method checkbox")
    screenshot(page, "CRM_step_9_checked_verification_1.png")
    sleep(3)
    verification_checkbox2.check()
    print("[LOG] Checked second Verification Method checkbox")
    screenshot(page, "CRM_step_10_checked_verification_2.png")
    sleep(3)
    verification_checkbox3.check()
    print("[LOG] Checked third Verification Method checkbox")
    screenshot(page, "CRM_step_11_checked_verification_3.png")
    sleep(3)

    relationship_dropdown = find_element_across_frames(page, "//*[text()='Relationship to Patient']/ancestor-or-self::*[contains(@class,'dataLabelFor')]/following-sibling::*//select")
    if not relationship_dropdown:
        print("[ERROR] 'Relationship to Patient' dropdown not found")
        raise Exception("'Relationship to Patient' dropdown not found")
    relationship_dropdown.select_option(label="Patient")
    print("[LOG] Selected 'Patient' from Relationship to Patient dropdown")
    screenshot(page, "CRM_step_12_selected_relationship_patient.png")
    sleep(10)

    humira_checkbox = find_element_across_frames(page, "//span[@data-test-id='201710241151280460732434' and text()='HUMIRA']/ancestor::tr//input[@type='checkbox']")
    if not humira_checkbox:
        humira_checkbox = find_element_across_frames(page, "#pySelected")
    if not humira_checkbox:
        humira_checkbox = find_element_across_frames(page, "input[name='$PpyWorkPage$pTherapyList$l1$ppySelected']")
    if not humira_checkbox:
        humira_checkbox = find_element_across_frames(page, "//td[contains(@class, 'gridCell')]//input[@type='checkbox']")
    if not humira_checkbox:
        print("[ERROR] HUMIRA checkbox not found with any selector")
        raise Exception("HUMIRA checkbox not found")
    humira_checkbox.check()
    print("[LOG] Checked 'HUMIRA' medication checkbox")
    screenshot(page,"step_13_checked_humira_checkbox.png")
    sleep(5)

    risk_radio_no = find_element_across_frames(page, "(//*[text()='No'])[1]")
    if not risk_radio_no:
        print("[ERROR] No radio button for missed dose risk not found")
        raise Exception("No radio button for missed dose risk not found")
    risk_radio_no.click()
    print("[LOG] Clicked 'No' for missed dose risk")
    screenshot(page,"step_14_clicked_no_for_missed_dose.png")
    sleep(5)

    next_btn2 = find_element_across_frames(page, "[data-test-id='20201223000248034111750']")
    if not next_btn2:
        print("[ERROR] Next button after Verification and Medication not found")
        raise Exception("Next button after Verification and Medication not found")
    next_btn2.click()
    print("[LOG] Clicked Next button after Verification and Medication")
    screenshot(page, "CRM_step_15_clicked_next_verification_medication.png")
    sleep(30)

    # Step 4: Schedule Order Task
    add_task_btn = find_element_across_frames(page, "//button[@data-test-id='2014111401004903823658']")
    if not add_task_btn:
        print("[ERROR] Add Task button not found")
        raise Exception("Add Task button not found")
    add_task_btn.click()
    print("[LOG] Clicked Add Task button")
    screenshot(page, "CRM_step_16_clicked_add_task.png")
    sleep(8)

    schedule_order_option = find_element_across_frames(page, "//*[text()='Schedule Order' and @class='Add_task']")
    if not schedule_order_option:
        print("[ERROR] Schedule Order option in Add Task not found")
        raise Exception("Schedule Order option in Add Task not found")
    schedule_order_option.click()
    print("[LOG] Selected Schedule Order in Add Task popup")
    screenshot(page, "CRM_step_17_selected_schedule_order.png")
    sleep(3)

    confirm_add_tasks_btn = find_element_across_frames(page, "(//*[text()='Add tasks'])[2]")
    if not confirm_add_tasks_btn:
        print("[ERROR] Confirm Add Tasks button not found")
        raise Exception("Confirm Add Tasks button not found")
    confirm_add_tasks_btn.click()
    print("[LOG] Clicked Add Tasks to confirm scheduling")
    screenshot(page, "CRM_step_18_confirmed_add_tasks.png")
    sleep(15)

	finish_btn = find_element_across_frames(page, "//button[data-test-id='20160830155020026843112']")
    
    # If not found, try by name containing "Finish"
    if finish_btn is None:
        print("[LOG] Button not found by data-test-id, trying by name 'Finish'")
        finish_btn = find_element_across_frames(page, "//button[contains(@name, 'Finish')]")
    
    # If still not found, try by text content
    if finish_btn is None:
        print("[LOG] Button not found by name, trying by text 'Finish'")
        finish_btn = find_element_across_frames(page, "//button[contains(text(), 'Finish')]") 
    
    finish_btn.click()
    print("[LOG] Clicked Finish button in Scheduled order task")
    screenshot(page, "CRM_step_19_finish_btn.png")
    sleep(15)

	print("[LOG] Completed CRM Task Successfully")
	"""

	user_input = f"""
 
	<element_reference_code>
    {element_reference_code}
    </element_reference_code>

	<Corrected Selector Mapping>
	Instructions:
	- The following is a list of corrected and up-to-date selectors for the CRM application.
	- You MUST prioritize using the selectors from this list wherever applicable for the given scenario steps.
	- If a selector for a specific element exists in this mapping, use it instead of any selector you might derive from the Java Context.

	Selector Mapping:
	# Login
	username: #txtUserID
	password: #txtPassword
	loginButton: #sub

	# Patient Search
	newButton: '//a[normalize-space(.)="New"]'
	simulateWorkspaceInteractionButton: "//*[text()='Simulate Workspace Interaction']"
	patientIdInput: 'input[id="a3f8064b"]'
	callIntentInput: 'input[id="5e9cabab"]'
	prescriptionNumberInput: 'input[id="418aff81"]'
	fillNumberInput: 'input[id="ac6e34af"]'
	serviceBranchInput: 'input[id="28d60f5c"]'
	nextButton: "[data-test-id='20201223000248034111750']"  

	# Verification and Medication
	verificationCheckbox1: "(//input[@type='checkbox'])[1]"
	verificationCheckbox2: "(//input[@type='checkbox'])[2]"
	verificationCheckbox3: "(//input[@type='checkbox'])[3]"
	relationshipDropdown: "//*[text()='Relationship to Patient']/ancestor-or-self::*[contains(@class,'dataLabelFor')]/following-sibling::*//select"
	humiraMedicationCheckbox: "//span[@data-test-id='201710241151280460732434' and text()='HUMIRA']/ancestor::tr//input[@type='checkbox']"
	missedDoseNoRadio: "(//*[text()='No'])[1]"

	# Schedule Order Task
	addTaskButton: "//button[@data-test-id='2014111401004903823658']"
	scheduleOrderOption: "//*[text()='Schedule Order' and @class='Add_task']"
	confirmAddTasksButton: "(//*[text()='Add tasks'])[2]"

	# Patient Medication and Review
	patientMedicationYesRadio: "//label[contains(@class, 'radioLabel') and contains(@class, 'rb_standard') and contains(@class, 'rb_')]"
	patientDeclinesCheckbox: "//input[@data-test-id='202007080356410453224916']"
	reviewButton: "//button[@data-test-id='2020121801252208389436']"
	estimatedResponsibilityCheckbox: "//input[@data-test-id='202208101045470657482784']"
	modifySuppliesLink: "//a[@data-test-id='20201222234640063946826']"
	submitSuppliesPopupButton: "//button[@data-test-id='20141008160437053510472' and text()='Submit']"
	secondReviewButton: "//button[@data-test-id='20201218012522083910607']"

	# Clinical Transfer and Address Verification
	clinicalTransferYesRadio: "//label[@for='f5130791Yes' and text()='Yes']"
	pharmacistCounselingAcceptedRadio: "//label[@for='d5e175ceTransferred- Accepted RPH Counseling']"
	addressCheckButton: "//button[@data-test-id='2020122223395908963337']"
	addressConfirmedButton: "//button[@data-test-id='ESIButton' and text()='Address CONFIRMED']"
	finalSubmitButton: "//button[@data-test-id='20201218012522083911187']"
	</Corrected Selector Mapping>

	Application name : CRM
	<INFO>
	Url -> https://spcrmqa-internal.express-scripts.com/spcrm88/
	patient id:{patient_id}
	</INFO>

	<Scenario Steps>
	{steps}
	</Scenario Steps>
	"""
	messages = [ SystemMessage(system_prompt_script_generation), HumanMessage(user_input) ]
	
	with get_openai_callback() as cb:
		llm_code = llm.invoke(messages).content
		print("---")
	print()
	print(f"Script - CRM Total Tokens: {cb.total_tokens}")
	print(f"Script - CRM Prompt Tokens: {cb.prompt_tokens}")
	print(f"Script - CRM Completion Tokens: {cb.completion_tokens}")
	parsed_code = extract_python_code(llm_code)
	
	# Replace the placeholder values with actual patient_id
	parsed_code = parsed_code.replace("{patient_id}", f'"{patient_id}"')
	
	return parsed_code
