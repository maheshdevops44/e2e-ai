from agent_utils import find_element_across_frames
from time import sleep
import pytest
from playwright.sync_api import sync_playwright, Page, expect
import os

def handle_popups(page):
    try:
        # Look for and close any modal dialogs
        modal_close_btn = page.locator('button[aria-label="Close"], .modal-close, .dialog-close').first
        if modal_close_btn:
            modal_close_btn.click(timeout=3000)
            print("Closed modal dialog")
            sleep(1)
    except:
        pass

def screenshot(page, name):
    """Take a screenshot and save it with the given name"""
    try:
        screenshot_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'screenshots'))
        os.makedirs(screenshot_dir, exist_ok=True)
        page.screenshot(path=os.path.join(screenshot_dir, f"{name}.png"))
        print(f"Screenshot saved: {name}.png")
    except Exception as e:
        print(f"Failed to take screenshot {name}: {e}")

def step(page):
    initial_url = "https://spcia-qa.express-scripts.com/spcia"
    input_fields = {
        "Username": "C9G5JS",
        "Password": "Emphatic-Award1-Tinker"
    }
    common_intake_id = "CMNINTAKE07292025113207551647359"
    patient_id = "17045255"

    # Step 1: Launch and Login to Intake
    page.goto(initial_url)
    sleep(5)
    screenshot(page, "01_launch_page")

    username_elem = find_element_across_frames(page, 'input[name="UserIdentifier"]')
    if not username_elem:
        raise Exception("Username input not found")
    username_elem.fill(input_fields["Username"])
    sleep(1)
    screenshot(page, "01_username_filled")

    password_elem = find_element_across_frames(page, 'input[name="Password"]')
    if not password_elem:
        raise Exception("Password input not found")
    password_elem.fill(input_fields["Password"])
    sleep(1)
    screenshot(page, "01_password_filled")

    login_btn = find_element_across_frames(page, 'button#sub')
    if not login_btn:
        raise Exception("Login button not found")
    login_btn.click()
    sleep(8)
    screenshot(page, "01_login_clicked")

    # Step 2: Search Intake ID in top-right search box
    search_box = find_element_across_frames(page, '(//input[@id="24dbd519"])[1]')
    if not search_box:
        raise Exception("Top-right search box not found")
    search_box.fill(common_intake_id)
    sleep(1)
    screenshot(page, "02_filled_intake_id")
    search_box.press("Enter")
    sleep(5)
    screenshot(page, "02_search_entered")
    handle_popups(page)

    # Step 3: Click first T-ID link in search result table
    t_id_link = find_element_across_frames(page, '(//*[@id="bodyTbl_right"]/tbody/tr[2]/td[3]/div/span)')
    if not t_id_link:
        raise Exception("T-ID link in result table not found")
    t_id_link.click()
    sleep(5)
    screenshot(page, "03_t_id_clicked")
    handle_popups(page)

    # Step 4: Click on Update Task (Intake) under Name column
    update_task_link = find_element_across_frames(page, "//a[contains(text(),'Update Task (Intake)')]")
    if not update_task_link:
        raise Exception("Update Task (Intake) link not found")
    update_task_link.click()
    sleep(5)
    screenshot(page, "04_update_task_intake_clicked")
    handle_popups(page)
    sleep(5)  # Instruction: sleep after this step

    # Step 5: Close EIS Image Window (assuming popup close: X button with common selectors)
    # Try close button selector on new modal popup
    try:
        eis_close_btn = find_element_across_frames(page, 'button[aria-label="Close"]')
        if eis_close_btn:
            eis_close_btn.click()
            sleep(2)
            screenshot(page, "05_eis_image_closed")
        else:
            screenshot(page, "05_no_eis_image_popup")
    except Exception:
        screenshot(page, "05_eis_image_popup_close_attempted")
        pass

    handle_popups(page)
    sleep(2)

    # Step 6: Go to Drug Lookup Page - Drug tab then Search icon (skip tab as Drug is default)
    drug_search_icon = find_element_across_frames(page, '//img[contains(@data-click,"DrugLookup")]')
    if not drug_search_icon:
        raise Exception("Drug search icon not found")
    drug_search_icon.click()
    sleep(5)
    screenshot(page, "06_drug_lookup_search_icon_clicked")
    handle_popups(page)

    # Step 7: Perform Drug Search and Submit
    clear_btn = find_element_across_frames(page, '//button[@name="TherapyAndDrugLookup_pyWorkPage.Document.DrugList(1)_18"]')
    if not clear_btn:
        raise Exception("Drug Lookup clear button not found")
    clear_btn.click()
    sleep(2)
    screenshot(page, "07_drug_clear_clicked")

    search_drugname_elem = find_element_across_frames(page, 'input[name="$PpyTempPage$pDrugName"]')
    if not search_drugname_elem:
        raise Exception("Drug Lookup drug name input not found")
    search_drugname_elem.fill("00074055402")
    sleep(1)
    screenshot(page, "07_drug_name_entered")

    search_btn = find_element_across_frames(page, "//button[text()='Search' and starts-with(@name,'TherapyAndDrugLookUp')]")
    if not search_btn:
        raise Exception("Drug Lookup search button not found")
    search_btn.click()
    sleep(5)
    screenshot(page, "07_drug_search_clicked")

    # Select the first radio under returned results (humira radio selector)
    humira_radio = find_element_across_frames(page, '//table[contains(@grid_ref_page,".DrugList")]/tbody/tr/td//input[@type="radio"]')
    if not humira_radio:
        raise Exception("Drug Lookup search result radio button not found")
    humira_radio.click()
    sleep(1)
    screenshot(page, "07_drug_radio_selected")

    # Submit selected drug
    drug_submit_btn = find_element_across_frames(page, "//*[@name='DrugLookUpModalTabUI_pyWorkPage.Document.DrugList(1)_96']")
    if not drug_submit_btn:
        drug_submit_btn = find_element_across_frames(page, "//button[text()='Submit']")
    if not drug_submit_btn:
        raise Exception("Drug Lookup submit button not found")
    drug_submit_btn.click()
    sleep(5)
    screenshot(page, "07_drug_lookup_submitted")
    handle_popups(page)

    # Step 8: Open Task Again - Click Update Task (Intake) with Pending Progress status
    pending_update_task = find_element_across_frames(page, "//a[contains(text(),'Update Task (Intake)')]")
    if not pending_update_task:
        raise Exception("Update Task (Intake) with Pending Progress status not found after drug submit")
    pending_update_task.click()
    sleep(5)
    screenshot(page, "08_pending_update_task_clicked")
    handle_popups(page)
    sleep(5)  # Instruction: sleep after this step

    # Step 9: Add Therapy and Place of Service in Drug tab (tab is default, so fill input)
    therapy_input = find_element_across_frames(page, "input[name='$PpyWorkPage$pDocument$pDrugList$l1$pTherapyType']")
    if not therapy_input:
        raise Exception("Therapy Type input not found")
    therapy_input.fill("HUMA")
    sleep(1)
    screenshot(page, "09_therapy_type_filled")

    pos_dropdown = find_element_across_frames(page, "select[name='$PpyWorkPage$pDocument$pDrugList$l1$pPOSDescription']")
    if not pos_dropdown:
        # try with input type if select isn't found (for apps using combo input)
        pos_dropdown = find_element_across_frames(page, "input[name='$PpyWorkPage$pDocument$pDrugList$l1$pPOSDescription']")
    if not pos_dropdown:
        raise Exception("Place of Service dropdown/input not found")

    # Try to select option 'Home'
    try:
        pos_dropdown.select_option(label="Home")
    except Exception:
        pos_dropdown.fill("Home")
    sleep(1)
    screenshot(page, "09_pos_home_selected")

    # Step 10: Link Patient Record
    # Go to Patient tab
    patient_tab_elem = find_element_across_frames(page, "(//h3[text()='Patient Details'])[1]")
    if not patient_tab_elem:
        raise Exception("Patient tab not found")
    patient_tab_elem.click()
    sleep(1)
    screenshot(page, "10_patient_tab_clicked")
    # Try clicking again if patient_tab_elem is visible
    from playwright.sync_api import TimeoutError
    try:
        patient_tab_elem_2 = find_element_across_frames(page, "(//h3[text()='Patient Details'])[1]")
        if patient_tab_elem_2:
            patient_tab_elem_2.click()
            sleep(1)
    except:
        pass

    # Click the Patient search icon
    patient_search_icon = find_element_across_frames(page, 'img[data-template=""][data-click*="PatientLookUp"]')
    if not patient_search_icon:
        raise Exception("Patient search icon not found")
    patient_search_icon.click()
    sleep(2)
    screenshot(page, "10_patient_search_icon_clicked")
    handle_popups(page)

    # Click Clear in patient search window
    patient_search_clear = find_element_across_frames(page, "//button[@name='PatientLookUp_pyWorkPage.Document.Patient_26']")
    if not patient_search_clear:
        raise Exception("Patient search clear button not found")
    patient_search_clear.click()
    sleep(1)
    screenshot(page, "10_patient_search_clear_clicked")

    # Enter Patient ID
    patient_search_input = find_element_across_frames(page, 'input[name="$PpyTempPage$pPatientID"]')
    if not patient_search_input:
        raise Exception("Patient search input for Patient ID not found")
    patient_search_input.fill(patient_id)
    sleep(1)
    screenshot(page, "10_patient_id_filled")

    # Patient search button (Search)
    patient_search_btn = find_element_across_frames(page, "//button[contains(text(),'Search')]")
    if not patient_search_btn:
        raise Exception("Patient search button not found")
    patient_search_btn.click()
    sleep(5)
    screenshot(page, "10_patient_search_clicked")

    # Select record with SB = 799
    sb_799_radio = find_element_across_frames(page, "//table[contains(@grid_ref_page,'pyWorkPage.Document.Patient')]/tbody/tr[./td[4]//span[text()='799']]/td[2]//input[@type='radio']")
    if not sb_799_radio:
        sb_799_radio = find_element_across_frames(page, "//table[contains(@grid_ref_page,'pyWorkPage.Document.Patient')]/tbody/tr[contains(@class,'Row')]/td[4]/div/span[text()='799']/ancestor::tr/td[2]//input[@type='radio']")
    if not sb_799_radio:
        raise Exception("Patient table radio button with SB=799 not found")
    sb_799_radio.click()
    sleep(1)
    screenshot(page, "10_patient_sb799_radio_selected")

    # Submit selection
    submit_patient_btn = find_element_across_frames(page, "//button[@id='ModalButtonSubmit']")
    if not submit_patient_btn:
        raise Exception("Patient submit button not found")
    submit_patient_btn.click()
    sleep(3)
    screenshot(page, "10_patient_submit_clicked")

    # From Address List, select first index
    address_dropdown = find_element_across_frames(page, "#ded594e9")
    if not address_dropdown:
        raise Exception("Address List (dropdown with id=#ded594e9) not found")
    try:
        address_dropdown.select_option(index=1)
    except Exception:
        # fallback: click dropdown and try to click first
        pass
    sleep(1)
    screenshot(page, "10_patient_addr_first_selected")

    # Step 11: Complete Prescriber/Category Team if blank
    presc_team_dropdown = find_element_across_frames(page, "select[name='$PpyWorkPage$pDocument$pTeamName']")
    if not presc_team_dropdown:
        presc_team_dropdown = find_element_across_frames(page, "input[name='$PpyWorkPage$pDocument$pTeamName']")
    if not presc_team_dropdown:
        raise Exception("Prescriber/Category Team dropdown not found")

    try:
        options = presc_team_dropdown.locator("option:not([value=''])")
        if options.count() > 0:
            first_option_value = options.first.get_attribute("value")
            presc_team_dropdown.select_option(first_option_value)
        else:
            print("No non-blank team options found.")
    except Exception:
        try:
            presc_team_dropdown.fill("TEAM 1")
        except Exception:
            raise Exception("Unable to set Prescriber/Category Team as TEAM 1")
    sleep(1)
    screenshot(page, "11_presc_category_team_set")

    # Step 12: Complete the Intake T-Task ID (Submit)
    task_submit_btn = find_element_across_frames(page, "button[name='CommonFlowActionButtons_pyWorkPage_17']")
    if not task_submit_btn:
        raise Exception("Task Submit button not found")
    task_submit_btn.click()
    sleep(5)
    screenshot(page, "12_task_submit_clicked")
    handle_popups(page)

def main():
    """Simple main function to run the step function"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        
        # Set up automatic popup handling
        def on_new_page(new_page):
            try:
                new_page.wait_for_load_state('domcontentloaded', timeout=8000)
                title = new_page.title()
                url = new_page.url
                
                print(f"New page detected:")
                print(f"  Title: {title}")
                print(f"  URL: {url}")
                
                if 'Untitled' in title or 'about:blank' in title:
                    print('Potentially unwanted blank page/popup detected -> closing it')
                    new_page.close()
                    return
            except Exception as e:
                print(f"Could not get title/url for new page: {e}")
        
        context.on("page", on_new_page)
        
        page = context.new_page()
        
        try:
            step(page)
            print("Step execution completed successfully!")
        except Exception as e:
            print(f"Error during execution: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    main() 