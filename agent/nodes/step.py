from agent_utils import find_element_across_frames, robust_fill
from time import sleep
from datetime import datetime
from playwright.sync_api import sync_playwright
import sys

def step(page):
    initial_url = "https://clearance-qa.express-scripts.com/spclr"
    page.goto(initial_url)
    sleep(2)

    # Step 1: Login
    username = find_element_across_frames(page, 'input[name="UserIdentifier"]')
    if not username:
        raise Exception("Username input not found")
    username.fill("C9G5JR")
    page.screenshot(path="screenshot_1.png")
    sleep(1)

    password = find_element_across_frames(page, 'input[name="Password"]')
    if not password:
        raise Exception("Password input not found")
    password.fill("Adth2107!")
    page.screenshot(path="screenshot_2.png")
    sleep(1)

    login_btn = find_element_across_frames(page, 'button#sub')
    if not login_btn:
        raise Exception("Login button not found")
    login_btn.click()
    sleep(4)

    # Step 2: Search for the Patient Case
    search_cases = find_element_across_frames(page, 'a[name="SearchUtilities_pyDisplayHarness_5"]')
    if not search_cases:
        raise Exception("Search Cases link not found")
    search_cases.click()
    page.screenshot(path="screenshot_3.png")
    sleep(3)

    patient_id_input = find_element_across_frames(page, 'input[name="$PpyDisplayHarness$pCaseSearchCriteria$pPatient$pPatientIDNumeric"]')
    if not patient_id_input:
        raise Exception("Patient ID input not found")
    patient_id_input.fill("17078886")
    page.screenshot(path="screenshot_4.png")
    sleep(1)

    search_btn = find_element_across_frames(page, 'button[name="SearchCases_pyDisplayHarness.CaseSearchCriteria_14"]')
    if not search_btn:
        raise Exception("Search button not found")
    search_btn.click()
    sleep(4)

    # Step 3: Click on the IE- case row
    ie_task_link = find_element_across_frames(page, '//table[@pl_prop=\'D_GetWorkCases.pxResults\']/tbody/tr[2]/td[1]//a')
    if not ie_task_link:
        raise Exception("IE Task ID link not found")
    ie_task_link.click()
    sleep(40)

    pos_input = find_element_across_frames(page, 'input[name="$PpyWorkPage$pPlaceOfService"]')
    if not pos_input:
        raise Exception("Place of Service input not found")
    pos_input.fill("12")
    sleep(1)

    bin_input = find_element_across_frames(page, 'input[name="$PpyWorkPage$pAdditionalPayers$l1$pBankIDNumber"]')
    if not bin_input:
        raise Exception("BIN input not found")
    bin_input.fill("610144")
    sleep(10)

    pcn_input = find_element_across_frames(page, 'input[name="$PpyWorkPage$pAdditionalPayers$l1$pPCN"]')
    print("*******************************",pcn_input)
    if not pcn_input:
        raise Exception("PCN input not found")
    pcn_input.click()
    pcn_input.fill("D0TEST")
    sleep(10)

    group_number_input = find_element_across_frames(page, 'input[name="$PpyWorkPage$pAdditionalPayers$l1$pGroupNumber"]')
    if not group_number_input:
        raise Exception("Group Number input not found")
    group_number_input.click()
    group_number_input.fill("RTA")
    sleep(10)

    save_payee_btn = find_element_across_frames(page, 'button[data-test-id="PayerInfoScreen-Button-Search"]')
    if not save_payee_btn:
        raise Exception("Save Payee button not found")
    save_payee_btn.click()
    page.screenshot(path="screenshot_5.png")
    sleep(3)

    cardholder_input = find_element_across_frames(page, '//span/input[@id="6a329411"]')
    if not cardholder_input:
        raise Exception("Cardholder ID input not found")
    cardholder_input.fill("555123123")
    sleep(1)

    person_code_input = find_element_across_frames(page, '//div/input[@id="a451c2d0"]')
    if not person_code_input:
        raise Exception("Person Code input not found")
    person_code_input.fill("01")
    sleep(10)

    effective_date_input = find_element_across_frames(page, '//span/input[@class="inactvDtTmTxt"]')
    if not effective_date_input:
        raise Exception("Insurance Effective Date input not found")
    today = datetime.now().strftime("%m/%d/%Y")
    # effective_date_input.fill(today)
    effective_date_input.fill(today)
    sleep(1)

    # Add End Date input
    end_date_input = find_element_across_frames(page, 'input[data-test-id="20171109141147048668261"]')
    if not end_date_input:
        raise Exception("End Date input not found")
    # Set end date to 1 year from today
    end_date = datetime.now().replace(year=datetime.now().year + 1).strftime("%m/%d/%Y")
    end_date_input.fill(end_date)
    sleep(1)

    relationship_dropdown = find_element_across_frames(page, '//div/select[@data-test-id="20171115143211077239541"]')
    if not relationship_dropdown:
        raise Exception("Relationship dropdown not found")
    relationship_dropdown.select_option(label="1 - Self")
    sleep(1)

    save_policy_btn = find_element_across_frames(page, 'button[data-test-id="20200305121820016323290"]')
    if not save_policy_btn:
        raise Exception("Save Policy button not found")
    save_policy_btn.click()
    page.screenshot(path="screenshot_6.png")
    sleep(20)

    next_btn = find_element_across_frames(page, 'button[name="CommonFlowActionButtons_pyWorkPage_31"]')
    if not next_btn:
        raise Exception("Next button not found")
    next_btn.click()
    sleep(20)

    drug_checkbox = find_element_across_frames(page, '//span[@class="checkbox"]//input[@type="checkbox"]')
    if not drug_checkbox:
        raise Exception("Drug field checkbox not found")
    if not drug_checkbox.is_checked():
        drug_checkbox.check()
    page.screenshot(path="screenshot_7.png")
    sleep(30)

    # Handle autocomplete dropdown manually for better control (NR case)
    print("Filling primary payer service input (NR case)...")
    primary_payer_input = find_element_across_frames(page, 'input[data-test-id="202006170412060535921"]')
    if not primary_payer_input:
        raise Exception("Primary Payer Service input not found")
    
    # Clear and fill the input
    primary_payer_input.clear()
    primary_payer_input.fill("71504")
    
    # Wait for dropdown to appear and click the first option
    print("Waiting for autocomplete dropdown...")
    sleep(10)  # Wait for suggestions to load
    
    page.keyboard.press("ArrowDown")
    sleep(10)
    page.keyboard.press("ArrowDown")
    page.keyboard.press("Enter")
    print("Used keyboard navigation")
    
    page.screenshot(path="screenshot_8.png")
    sleep(30)

    copay_input = find_element_across_frames(page, 'select[data-test-id="20200313110855039235493"]')
    if not copay_input:
        # Try alternative selector
        copay_input = find_element_across_frames(page, 'select[name="$PpyWorkPage$pBillingSplitServices$l1$pCoPay$l1$pAssignCoPayTo"]')
        if not copay_input:
            raise Exception("CoPay input not found")
    copay_input.select_option(value="P")
    page.screenshot(path="screenshot_9.png")
    sleep(30)

    finish_btn = find_element_across_frames(page, '//span/button[text()="Finish"]')
    if not finish_btn:
        raise Exception("Finish button not found")
    finish_btn.click()
    page.screenshot(path="screenshot_10.png")
    sleep(60)

    # # Step 11: Repeat for NR Case
    # # Go back to Search Cases
    # search_cases = find_element_across_frames(page, 'a[name="SearchUtilities_pyDisplayHarness_5"]')
    # if not search_cases:
    #     raise Exception("Search Cases link not found (NR repeat)")
    # search_cases.click()
    # page.screenshot(path="screenshot_11.png")
    # sleep(3)

    # patient_id_input = find_element_across_frames(page, 'input[name="$PpyDisplayHarness$pCaseSearchCriteria$pPatient$pPatientIDNumeric"]')
    # if not patient_id_input:
    #     raise Exception("Patient ID input not found (NR repeat)")
    # patient_id_input.fill("17045254")
    # sleep(1)

    # search_btn = find_element_across_frames(page, 'button[name="SearchCases_pyDisplayHarness.CaseSearchCriteria_14"]')
    # if not search_btn:
    #     raise Exception("Search button not found (NR repeat)")
    # search_btn.click()
    # sleep(4)

    # # Find NR- case row (assuming it's now at row 2)
    # nr_task_link = find_element_across_frames(page, '//table[@pl_prop=\'D_GetWorkCases.pxResults\']/tbody/tr[2]/td[1]//a')
    # if not nr_task_link:
    #     raise Exception("NR Task ID link not found")
    # nr_task_link.click()
    # sleep(35)

    # # Repeat Steps 4-10 for NR case

    # pos_input = find_element_across_frames(page, 'input[name="$PpyWorkPage$pPlaceOfService"]')
    # if not pos_input:
    #     raise Exception("Place of Service input not found (NR)")
    # pos_input.fill("12")
    # sleep(1)

    # bin_input = find_element_across_frames(page, 'input[name="$PpyWorkPage$pAdditionalPayers$l1$pBankIDNumber"]')
    # if not bin_input:
    #     raise Exception("BIN input not found (NR)")
    # bin_input.fill("610144")
    # sleep(10)

    # pcn_input = find_element_across_frames(page, 'input[name="$PpyWorkPage$pAdditionalPayers$l1$pPCN"]')
    # print("*******************************",pcn_input)
    # if not pcn_input:
    #     raise Exception("PCN input not found (NR)")
    # pcn_input.click()
    # pcn_input.fill("D0TEST")
    # sleep(10)

    # group_number_input = find_element_across_frames(page, 'input[name="$PpyWorkPage$pAdditionalPayers$l1$pGroupNumber"]')
    # if not group_number_input:
    #     raise Exception("Group Number input not found (NR)")
    # group_number_input.click()
    # group_number_input.fill("RTA")
    # sleep(10)

    # save_payee_btn = find_element_across_frames(page, 'button[data-test-id="PayerInfoScreen-Button-Search"]')
    # if not save_payee_btn:
    #     raise Exception("Save Payee button not found (NR)")
    # save_payee_btn.click()
    # page.screenshot(path="screenshot_12.png")
    # sleep(3)

    # cardholder_input = find_element_across_frames(page, '//span/input[@id="6a329411"]')
    # if not cardholder_input:
    #     raise Exception("Cardholder ID input not found (NR)")
    # cardholder_input.fill("555123123")
    # sleep(1)

    # person_code_input = find_element_across_frames(page, '//div/input[@id="a451c2d0"]')
    # if not person_code_input:
    #     raise Exception("Person Code input not found (NR)")
    # person_code_input.fill("01")
    # sleep(10)

    # effective_date_input = find_element_across_frames(page, '//span/input[@class="inactvDtTmTxt"]')
    # if not effective_date_input:
    #     raise Exception("Insurance Effective Date input not found (NR)")
    # today = datetime.now().strftime("%m/%d/%Y")
    # # effective_date_input.fill(today)
    # effective_date_input.fill(today)
    # sleep(1)

    # # Add End Date input
    # end_date_input = find_element_across_frames(page, 'input[data-test-id="20171109141147048668261"]')
    # if not end_date_input:
    #     raise Exception("End Date input not found (NR)")
    # # Set end date to 1 year from today
    # end_date = datetime.now().replace(year=datetime.now().year + 1).strftime("%m/%d/%Y")
    # end_date_input.fill(end_date)
    # sleep(1)

    # relationship_dropdown = find_element_across_frames(page, '//div/select[@data-test-id="20171115143211077239541"]')
    # if not relationship_dropdown:
    #     raise Exception("Relationship dropdown not found (NR)")
    # relationship_dropdown.select_option(label="1 - Self")
    # sleep(1)

    # save_policy_btn = find_element_across_frames(page, 'button[data-test-id="20200305121820016323290"]')
    # if not save_policy_btn:
    #     raise Exception("Save Policy button not found (NR)")
    # save_policy_btn.click()
    # page.screenshot(path="screenshot_13.png")
    # sleep(20)

    # next_btn = find_element_across_frames(page, 'button[name="CommonFlowActionButtons_pyWorkPage_31"]')
    # if not next_btn:
    #     raise Exception("Next button not found (NR)")
    # next_btn.click()
    # sleep(20)

    # drug_checkbox = find_element_across_frames(page, '//span[@class="checkbox"]//input[@type="checkbox"]')
    # if not drug_checkbox:
    #     raise Exception("Drug field checkbox not found (NR)")
    # if not drug_checkbox.is_checked():
    #     drug_checkbox.check()
    # page.screenshot(path="screenshot_14.png")
    # sleep(30)

    # # Handle autocomplete dropdown manually for better control (NR case)
    # print("Filling primary payer service input (NR case)...")
    # primary_payer_input = find_element_across_frames(page, 'input[data-test-id="202006170412060535921"]')
    # if not primary_payer_input:
    #     raise Exception("Primary Payer Service input not found (NR)")
    
    # # Clear and fill the input
    # primary_payer_input.clear()
    # primary_payer_input.fill("71504")
    
    # # Wait for dropdown to appear and click the first option
    # print("Waiting for autocomplete dropdown...")
    # sleep(10)  # Wait for suggestions to load
    
    # page.keyboard.press("ArrowDown")
    # sleep(10)
    # page.keyboard.press("ArrowDown")
    # page.keyboard.press("Enter")
    # print("Used keyboard navigation")
    
    # page.screenshot(path="screenshot_15.png")
    # sleep(30)

    # copay_input = find_element_across_frames(page, 'select[data-test-id="20200313110855039235493"]')
    # if not copay_input:
    #     # Try alternative selector
    #     copay_input = find_element_across_frames(page, 'select[name="$PpyWorkPage$pBillingSplitServices$l1$pCoPay$l1$pAssignCoPayTo"]')
    #     if not copay_input:
    #         raise Exception("CoPay input not found")
    # copay_input.select_option(value="P")
    # page.screenshot(path="screenshot_16.png")
    # sleep(30)

    # finish_btn = find_element_across_frames(page, '//span/button[text()="Finish"]')
    # if not finish_btn:
    #     raise Exception("Finish button not found (NR)")
    # finish_btn.click()
    # page.screenshot(path="screenshot_17.png")
    # sleep(60)

def main():
    """Main function to run the Playwright automation script"""
    try:
        print("🚀 Starting Clearance automation script...")
        
        with sync_playwright() as p:
            # Launch browser (you can change to 'firefox' or 'webkit' if needed)
            browser = p.chromium.launch(headless=False, slow_mo=1000)
            context = browser.new_context()
            page = context.new_page()
                    
            print("✅ Browser launched successfully")
            
            # Run the automation steps
            step(page)
            
            print("✅ Automation completed successfully!")
            
            # Keep browser open for a few seconds to see the final state
            sleep(5)
            
    except Exception as e:
        print(f"❌ Error during automation: {e}")
        sys.exit(1)
    finally:
        if 'browser' in locals():
            browser.close()
            print("🔒 Browser closed")

if __name__ == "__main__":
    main()