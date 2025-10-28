import asyncio
import sys
import os
from pathlib import Path
from playwright.async_api import async_playwright

# Add the current directory to the path for local imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import agent_utils for element finding
try:
    from agent_utils import find_element_across_frames, handle_popups, robust_click, robust_fill, wait_for_element_with_retry
except ImportError as e:
    print(f"Warning: Could not import agent_utils: {{e}}")

from application_config import ApplicationRegistry
from automation_config import APPLICATION_URLS, DEFAULT_USERNAME, DEFAULT_PASSWORD, PATIENT_ID, INTAKE_ID
import asyncio

from agent_utils import find_element_across_frames
from time import sleep

async def safe_find_element(page, selector):
    """Safely find element, returning None if not found instead of raising error"""
    try:
        element = await find_element_across_frames(page, selector)
        return element
    except Exception as e:
        print(f"⚠️ Element not found: {selector} - {e}")
        return None

async def handle_popups(page):
    """Handle any popup windows, dialogs, or overlays"""
    try:
        # Check if a new page/window opened
        if len(page.context.pages) > 1:
            # Close the popup window
            popup_page = page.context.pages[-1]  # Get the last opened page
            await popup_page.close()
            print("Closed popup window")
            await asyncio.sleep(1)
    except Exception as e:
        print(f"No popup window to close: {e}")
    
    try:
        # Look for and close any modal dialogs
        modal_close_btn = page.locator('button[aria-label="Close"], .modal-close, .dialog-close').first
        if modal_close_btn:
            await modal_close_btn.click()
            print("Closed modal dialog")
            await asyncio.sleep(1)
    except:
        pass
    
    try:
        # Handle any "OK" buttons in dialogs - specifically for document rendering errors
        ok_btn = page.locator('text="OK"').first
        if ok_btn:
            await ok_btn.click()
            print("Clicked OK button to close document error dialog")
            await asyncio.sleep(2)
    except:
        pass
    
    try:
        # Handle any "Cancel" buttons
        cancel_btn = page.locator('text="Cancel"').first
        if cancel_btn:
            await cancel_btn.click()
            print("Clicked Cancel button")
            await asyncio.sleep(1)
    except:
        pass
    
    try:
        # Handle document rendering error dialogs specifically
        error_dialog = page.locator('text="Unable to display document"').first
        if error_dialog:
            # Find and click the OK button in this specific dialog
            ok_in_error = page.locator('text="OK"').first
            if ok_in_error:
                await ok_in_error.click()
                print("Closed document rendering error dialog")
                await asyncio.sleep(2)
    except:
        pass

async def step(page):
    initial_url = "https://spcia-qa.express-scripts.com/spcia"
    await page.goto(initial_url)

    # Login
    username = await safe_find_element(page, 'input[name="UserIdentifier"]')
    if not username:
        raise Exception("Username input not found")
    await username.fill("C9G5JS")
    await asyncio.sleep(1)

    password = await safe_find_element(page, 'input[name="Password"]')
    if not password:
        raise Exception("Password input not found")
    await password.fill("Emphatic-Award1-Tinker")
    await asyncio.sleep(1)

    login_btn = await safe_find_element(page, 'button#sub')
    if not login_btn:
        raise Exception("Login button not found")
    await login_btn.click()
    await asyncio.sleep(3)

    # 1. Enter Common Intake ID in the top-right search box
    # Use a more specific selector to avoid the duplicate element issue
    try:
        # Try the most specific selector first
        search_input = page.locator('input[name="$PpyDisplayHarness$ppySearchText"]').first
        if not search_input:
            # Fallback to role-based selection
            search_input = page.get_by_role("textbox", name="Enter text to search").first
        if not search_input:
            # Last resort: try the original selector but with first()
            search_input = page.locator('span.primary_search input').first
        
        if search_input:
            await search_input.click()
            await asyncio.sleep(1)
            await search_input.fill("CMNINTAKE07292025113206980296588")
            await asyncio.sleep(1)
        else:
            raise Exception("Search input not found")
    except Exception as e:
        print(f"Error finding search input: {e}")
        raise

    # 2. Press Enter
    await search_input.press("Enter")
    await asyncio.sleep(3)
    
    # Handle any popup dialogs that might appear
    try:
        # Check for and close any error dialogs
        error_dialog = page.locator('text="OK"').first
        if error_dialog:
            await error_dialog.click()
            await asyncio.sleep(1)
    except:
        pass  # No dialog found, continue

    # 3. Verify pop-up displays T-Task Id under the ID column
    # (Assuming SearchFieldTaskstatus presence as validation of popup)
    ttask_status = await safe_find_element(page, '(//*[@id="bodyTbl_right"]/tbody/tr[2]/td[3]/div/span)')
    if not ttask_status:
        raise Exception("T-Task Id status not found in the search results popup")
    await asyncio.sleep(1)

    # 4. Click on the T-ID link
    # The T-ID link is likely the Intake ID in results
    ntask_id = await safe_find_element(page, '(//*[@id="bodyTbl_right"]/tbody/tr[2]/td[3]/div/span)')
    if not ntask_id:
        raise Exception("T-ID link not found")
    await ntask_id.click()
    await asyncio.sleep(5)

    # 5. Validate navigation to Case Contents page
    case_summary = await safe_find_element(page, '//div[text()="Case summary"]')
    if not case_summary:
        raise Exception("Failed to navigate to Case Contents page")
    await asyncio.sleep(1)
    
    # Check for and handle any session locks or warnings
    try:
        # Look for any lock-related messages or buttons
        lock_warning = page.locator('text*="lock"').first
        if lock_warning:
            print("Found lock warning, attempting to handle...")
            # Try to find and click any "Continue" or "OK" buttons
            continue_btn = page.locator('text="Continue"').first
            if continue_btn:
                await continue_btn.click()
                await asyncio.sleep(2)
    except:
        pass

    # 6. Click on Update Task (Intake) under Name column
    update_task = await safe_find_element(page, 'a[partialLinkText="Update Task (Intake)"]')
    if not update_task:
        update_task = await safe_find_element(page, 'a:has-text("Update Task (Intake)")')
        if not update_task:
            update_task = await safe_find_element(page, 'a.Update Task (Intake)')
        if not update_task:
            # Try with locator from "updateTask"
            update_task = await safe_find_element(page, 'a[partialLinkText="Update Task (Intake)"]')
    if not update_task:
        raise Exception("Update Task (Intake) link not found")
    await update_task.click()
    await asyncio.sleep(5)
    
    # Handle any popup windows, dialogs, or overlays
    await handle_popups(page)

    # 7. Validate navigation to Task page
    click_on_patient_details_tab = await safe_find_element(page, '(//h3[text()="Patient Details"])[1]')
    if not click_on_patient_details_tab:
        raise Exception("Not on Task page: Patient Details tab not found")
    await asyncio.sleep(1)

 
    # 8. Click on Search icon
    search_drug_icon = await safe_find_element(page, '(//td[@data-attribute-name=".pyTemplateInputBox"]/div/span/i/img)[1]')
    if not search_drug_icon:
        search_drug_icon = await safe_find_element(page, '//img[contains(@data-click,"DrugLookup")]')
    if not search_drug_icon:
        raise Exception("Drug search icon not found")
    await search_drug_icon.click()
    await asyncio.sleep(2)

    # 9. Click Clear
    clear_btn = await safe_find_element(page, '//button[@name="TherapyAndDrugLookup_pyWorkPage.Document.DrugList(1)_17"]')
    if not clear_btn:
        raise Exception("Drug Clear button not found")
    await clear_btn.click()
    await asyncio.sleep(1)

    search_drug_input = await safe_find_element(page, '//input[@id="7a12dd37"]')
    if not search_drug_input:
        raise Exception("Drug input search box not found.")
    await search_drug_input.fill("00074055402")
    await asyncio.sleep(2)

    # 10. Click Search
    search_btn = await safe_find_element(page, '//button[@name="TherapyAndDrugLookup_pyWorkPage.Document.DrugList(1)_18"]')
    if not search_btn:
        raise Exception("Drug Search button not found")
    await search_btn.click()
    await asyncio.sleep(2)

    xpath = '//table[contains(@grid_ref_page,".DrugList")]/tbody/tr/td//input[@type="radio"]'
    humira_row_radio = await safe_find_element(page, xpath)
    if not humira_row_radio:
        raise Exception("Could not find HUMIRA 40 MG/0.4 ML PEN 2'S (NDC: 00074055402) radio in drug results")
    await humira_row_radio.click()
    await asyncio.sleep(1)

    # 12. Click Submit
    selected_drug_submit = await safe_find_element(page, "//*[@name='DrugLookUpModalTabUI_pyWorkPage.Document.DrugList(1)_96']")
    if not selected_drug_submit:
        selected_drug_submit = await safe_find_element(page, 'button[text()="Submit"]')
    if not selected_drug_submit:
        selected_drug_submit = await safe_find_element(page, '//button[text()="Submit"]')
    if not selected_drug_submit:
        raise Exception("Drug Submit button not found")
    await selected_drug_submit.click()
    await asyncio.sleep(3)

    
   
    
    # 6. Click on Update Task (Intake) under Name column
    update_task_selector = await safe_find_element(page, 'a[partialLinkText="Update Task (Intake)"]')
    if not update_task_selector:
        update_task_selector = await safe_find_element(page, 'a:has-text("Update Task (Intake)")')
        if not update_task_selector:
            update_task_selector = await safe_find_element(page, 'a.Update Task (Intake)')
        if not update_task_selector:
            # Try with locator from "updateTask"
            update_task_selector = await safe_find_element(page, 'a[partialLinkText="Update Task (Intake)"]')
    if not update_task_selector:
        raise Exception("Update Task (Intake) link not found")
    await update_task_selector.click()
    await asyncio.sleep(5)


    # Handle any popup windows, dialogs, or overlays
    await handle_popups(page)

    #--- Step 9: Add Therapy and Place of Service in Drug Tab ---
    # drug_tab = find_element_across_frames(page, "//h3[text()='Drug']")
    # if not drug_tab:
    #     raise Exception("Drug tab not found")
    # drug_tab.click()
    # sleep(2)

    # drug_tab = page.locator("h3.layout-group-item-title:has-text('Drug')").first
    # if not drug_tab.is_visible():
    #     raise Exception("Drug tab not found")
    # drug_tab.click()


    # Select Therapy Type: HUMA
    therapy_type = await safe_find_element(page, "input[name='$PpyWorkPage$pDocument$pDrugList$l1$pTherapyType']")
    if not therapy_type:
        therapy_type = await safe_find_element(page, "select[name='$PpyWorkPage$pDocument$pDrugList$l1$pTherapyType']")
    if not therapy_type:
        raise Exception("Therapy Type input not found")
    await therapy_type.fill("HUMA")
    await asyncio.sleep(1)

    # Select Place of Service: Home
    place_of_service = await safe_find_element(page, "input[name='$PpyWorkPage$pDocument$pDrugList$l1$pPOSDescription']")
    if not place_of_service:
        place_of_service = await safe_find_element(page, "select[name='$PpyWorkPage$pDocument$pDrugList$l1$pPOSDescription']")
    if not place_of_service:
        raise Exception("Place of Service dropdown not found")
    await place_of_service.select_option(label="Home")
    await asyncio.sleep(1)


    await asyncio.sleep(5)

    ##--- Step 10: Link Patient Record ---
    # Try multiple selectors for Patient Details tab
    patient_tab = await safe_find_element(page, "(//h3[text()='Patient Details'])[1]")
    if not patient_tab:
        patient_tab = await safe_find_element(page, "h3.layout-group-item-title:has-text('Patient Details')")
    if not patient_tab:
        patient_tab = await safe_find_element(page, "h3:has-text('Patient Details')")
    if not patient_tab:
        raise Exception("Patient Details tab not found")
    await patient_tab.click()
    await asyncio.sleep(5)

    # Try multiple selectors for Patient Details tab (second click)
    patient_tab = await safe_find_element(page, "(//h3[text()='Patient Details'])[1]")
    if not patient_tab:
        patient_tab = await safe_find_element(page, "h3.layout-group-item-title:has-text('Patient Details')")
    if not patient_tab:
        patient_tab = await safe_find_element(page, "h3:has-text('Patient Details')")
    if not patient_tab:
        raise Exception("Patient Details tab not found")
    await patient_tab.click()
    await asyncio.sleep(5)



    patient_lookup_icon = await safe_find_element(page, 'img[data-template=""][data-click*="PatientLookUp"]')
    if not patient_lookup_icon:
        patient_lookup_icon = await safe_find_element(page, "select[name='PatientDetailsTab_pyWorkPage.Document_45']")
    if not patient_lookup_icon:
        raise Exception("Patient Lookup icon not found")
    await patient_lookup_icon.click()
    await asyncio.sleep(2)

    # Click Clear (in lookup modal)
    patient_lookup_clear_btn = await safe_find_element(page, "//button[@name='PatientLookUp_pyWorkPage.Document.Patient_26']")
    # if not patient_lookup_clear_btn:
    #     # fallback: generic clear in dialog
    #     patient_lookup_clear_btn = find_element_across_frames(page, "//button[text()='Clear']")
    if not patient_lookup_clear_btn:
        raise Exception("Clear button in patient lookup not found")
    await patient_lookup_clear_btn.click()
    await asyncio.sleep(1)

    # Enter Patient ID (from DaaS tool)
    patient_id_input = await safe_find_element(page, "input[name='$PpyTempPage$pPatientID']")
    if not patient_id_input:
        raise Exception("Patient ID input not found")
    await patient_id_input.fill(PATIENT_ID)
    await asyncio.sleep(1)

    # Click Search
    search_btn = await safe_find_element(page, "//button[contains(text(),'Search')]")
    if not search_btn:
        raise Exception("Search button in patient lookup not found")
    await search_btn.click()
    await asyncio.sleep(2)

    # Select the record with SB = 555
    # Need to find table row/cell with SB == '555', click its radio or select option in grid.
    found = False
    for row in range(1, 6):  # Try first 5 results/rows
        print("Inside loop")
        sb_cell_xpath = f"(//table[contains(@grid_ref_page,'pyWorkPage.Document.Patient')]/tbody/tr[contains(@class,'Row')])[{row}]/td[4]/div/div/div/div/div/div/div/span"
        sb_cell = await safe_find_element(page, sb_cell_xpath)
        print(sb_cell)
        if sb_cell:
            sb_val = await sb_cell.inner_text()
            sb_val = sb_val.strip()
            print(f"{row}, {sb_val}")
            if sb_val == "555":
                radio_xpath = f"(//table[contains(@grid_ref_page,'pyWorkPage.Document.Patient')]/tbody/tr[contains(@class,'Row')])[{row}]/td[2]//input[@type='radio']"
                radio = await safe_find_element(page, radio_xpath)
                if not radio:
                    raise Exception(f"Radio for SB=555 not found in row {row}")
                await radio.click()
                found = True
                break
    if not found:
        raise Exception("Patient record with SB=555 not found")
    await asyncio.sleep(1)

    # Click Submit
    submit_btn = await safe_find_element(page, "#ModalButtonSubmit")
    if not submit_btn:
        submit_btn = await safe_find_element(page, "button#ModalButtonSubmit")
    if not submit_btn:
        submit_btn = await safe_find_element(page, "//button[@id='ModalButtonSubmit']")
    if not submit_btn:
        raise Exception("Submit button in patient lookup not found")
    await submit_btn.click()
    await asyncio.sleep(3)

       # From Address List, select any address
    address_dropdown = await safe_find_element(page, "#ded594e9")
    if not address_dropdown:
        raise Exception("Address dropdown not found")
    await address_dropdown.select_option(index=1)
    await asyncio.sleep(5)
    

    # --- Step 11: Complete Prescriber/Category ---
    # Try multiple selectors for Prescriber tab
    prescriber_tab = await safe_find_element(page, "(//h3[text()='Prescriber / Category / Team'])[1]")
    if not prescriber_tab:
        prescriber_tab = await safe_find_element(page, "h3.layout-group-item-title:has-text('Prescriber / Category / Team')")
    if not prescriber_tab:
        prescriber_tab = await safe_find_element(page, "h3:has-text('Prescriber / Category / Team')")
    if not prescriber_tab:
        raise Exception("Prescriber / Category / Team tab not found")
    await prescriber_tab.click()
    await asyncio.sleep(5)



    

    # Select any team in the input if blank
    input_prescr_team = await safe_find_element(page, "input[name='$PpyWorkPage$pDocument$pTeamName']")
    if input_prescr_team:
        current_value = await input_prescr_team.input_value()
        current_value = current_value.strip() if current_value else ""
        if not current_value:
            await input_prescr_team.fill("TEAM 1")
            await asyncio.sleep(1)
    # else: ignore if no input (sometimes not required)

    await asyncio.sleep(1)

    # --- Step 12: Complete the Intake T-Task id ---
    # Click Submit (for task)
    task_submit_btn = await safe_find_element(page, "button[name='CommonFlowActionButtons_pyWorkPage_17']")
    if not task_submit_btn:
        task_submit_btn = await safe_find_element(page, "//button[@title='Complete this assignment']")
    if not task_submit_btn:
        task_submit_btn = await safe_find_element(page, "//button[text()='Submit']")
    if not task_submit_btn:
        raise Exception("Submit button on task page not found")
    await task_submit_btn.click()
    await asyncio.sleep(5)

    # # # Optionally, check for status "Completed" in Case Contents
    # # status_elem = find_element_across_frames(page, "//span[normalize-space()='Resolved-System']")
    # # if not status_elem:
    # #     # Accept that the status element may not be shown in this view—for an explicit wait, usually done with proper helpers/wait, which aren't described
    # #     pass
    # # sleep(2)

from agent_utils import find_element_across_frames
from time import sleep

async def handle_popups(page):
    """Handle any popup windows, dialogs, or overlays"""
    # try:
    #     # Check if a new page/window opened
    #     if len(page.context.pages) > 1:
    #         # Close the popup window
    #         popup_page = page.context.pages[-1]  # Get the last opened page
    #         await popup_page.close()
    #         print("Closed popup window")
    #         await asyncio.sleep(1)
    # except Exception as e:
    #     print(f"No popup window to close: {e}")
    
    try:
        # Look for and close any modal dialogs
        modal_close_btn = page.locator('button[aria-label="Close"], .modal-close, .dialog-close').first
        if modal_close_btn:
            await modal_close_btn.click()
            print("Closed modal dialog")
            await asyncio.sleep(1)
    except:
        pass
    
    # try:
    #     # Handle any "OK" buttons in dialogs - specifically for document rendering errors
    #     ok_btn = page.locator('text="OK"').first
    #     if ok_btn:
    #         ok_btn.click()
    #         print("Clicked OK button to close document error dialog")
    #         sleep(2)
    # except:
    #     pass
    
    # try:
    #     # Handle any "Cancel" buttons
    #     cancel_btn = page.locator('text="Cancel"').first
    #     if cancel_btn:
    #         cancel_btn.click()
    #         print("Clicked Cancel button")
    #         sleep(1)
    # except:
    #     pass
    
    # try:
    #     # Handle document rendering error dialogs specifically
    #     error_dialog = page.locator('text="Unable to display document"').first
    #     if error_dialog:
    #         # Find and click the OK button in this specific dialog
    #         ok_in_error = page.locator('text="OK"').first
    #         if ok_in_error:
    #             ok_in_error.click()
    #             print("Closed document rendering error dialog")
    #             sleep(2)
    # except:
    #     pass
    
#     # try:
#     #     # Handle any overlay dialogs that might be blocking interaction
#     #     overlay = page.locator('.overlay, .modal-backdrop, .dialog-overlay').first
#     #     if overlay:
#     #         # Try to click outside the dialog to close it
#     #         page.click('body', position={'x': 10, 'y': 10})
#     #         print("Clicked outside dialog to close overlay")
#     #         sleep(1)
#     # except:
#     #     pass

# async def step(page):
#     initial_url = "https://spcia-qa.express-scripts.com/spcia"
#     await page.goto(initial_url)

#     # Login
#     username = await find_element_across_frames(page, 'input[name="UserIdentifier"]')
#     if not username:
#         raise Exception("Username input not found")
#     await username.fill("C9G5JS")
#     await asyncio.sleep(1)

#     password = await find_element_across_frames(page, 'input[name="Password"]')
#     if not password:
#         raise Exception("Password input not found")
#     await password.fill("Emphatic-Award1-Tinker")
#     await asyncio.sleep(1)

#     login_btn = await find_element_across_frames(page, 'button#sub')
#     if not login_btn:
#         raise Exception("Login button not found")
#     await login_btn.click()
#     await asyncio.sleep(3)

#     # 1. Enter Common Intake ID in the top-right search box
#     # Use a more specific selector to avoid the duplicate element issue
#     try:
#         # Try the most specific selector first
#         search_input = page.locator('input[name="$PpyDisplayHarness$ppySearchText"]').first
#         if not search_input:
#             # Fallback to role-based selection
#             search_input = page.get_by_role("textbox", name="Enter text to search").first
#         if not search_input:
#             # Last resort: try the original selector but with first()
#             search_input = page.locator('span.primary_search input').first
        
#         if search_input:
#             await search_input.click()
#             await asyncio.sleep(1)
#             await search_input.fill("CMNINTAKE07252025051022208449980")
#             await asyncio.sleep(1)
#         else:
#             raise Exception("Search input not found")
#     except Exception as e:
#         print(f"Error finding search input: {e}")
#         raise

#     # 2. Press Enter
#     await search_input.press("Enter")
#     await asyncio.sleep(3)
    
#     # Handle any popup dialogs that might appear
#     # try:
#     #     # Check for and close any error dialogs
#     #     error_dialog = page.locator('text="OK"').first
#     #     if error_dialog:
#     #         error_dialog.click()
#     #         sleep(1)
#     # except:
#     #     pass  # No dialog found, continue

#     # 3. Verify pop-up displays T-Task Id under the ID column
#     # (Assuming SearchFieldTaskstatus presence as validation of popup)
#     ttask_status = await find_element_across_frames(page, '(//*[@id="bodyTbl_right"]/tbody/tr[2]/td[3]/div/span)')
#     if not ttask_status:
#         raise Exception("T-Task Id status not found in the search results popup")
#     await asyncio.sleep(1)

#     # 4. Click on the T-ID link
#     # The T-ID link is likely the Intake ID in results
#     ntask_id = await find_element_across_frames(page, '(//*[@id="bodyTbl_right"]/tbody/tr[2]/td[3]/div/span)')
#     if not ntask_id:
#         raise Exception("T-ID link not found")
#     await ntask_id.click()
#     await asyncio.sleep(2)

#     # 5. Validate navigation to Case Contents page
#     case_summary = await find_element_across_frames(page, '//div[text()="Case summary"]')
#     if not case_summary:
#         raise Exception("Failed to navigate to Case Contents page")
#     await asyncio.sleep(1)
    
#     # Check for and handle any session locks or warnings
#     # try:
#     #     # Look for any lock-related messages or buttons
#     #     lock_warning = page.locator('text*="lock"').first
#     #     if lock_warning:
#     #         print("Found lock warning, attempting to handle...")
#     #         # Try to find and click any "Continue" or "OK" buttons
#     #         continue_btn = page.locator('text="Continue"').first
#     #         if continue_btn:
#     #             continue_btn.click()
#     #             sleep(2)
#     # except:
#     #     pass

#     # 6. Click on Update Task (Intake) under Name column
#     update_task = await find_element_across_frames(page,'//a[text()="Update Task (Intake)"]')
#     # update_task = await find_element_across_frames(page, 'a[partialLinkText="Update Task (Intake)"]')
#     # if not update_task:
#     #     update_task = await find_element_across_frames(page, 'a:has-text("Update Task (Intake)")')
#     #     if not update_task:
#     #         update_task = await find_element_across_frames(page, 'a.Update Task (Intake)')
#     #     if not update_task:
#     #         # Try with locator from "updateTask"
#     #         update_task = await find_element_across_frames(page, 'a[partialLinkText="Update Task (Intake)"]')
#     if not update_task:
#         raise Exception("Update Task (Intake) link not found")
#     await update_task.click()
#     await asyncio.sleep(5)
    
#     # Handle any popup windows, dialogs, or overlays
#     await handle_popups(page)

#     # 7. Validate navigation to Task page
#     # click_on_patient_details_tab = await find_element_across_frames(page, '(//h3[text()="Patient Details"])[1]')
#     # if not click_on_patient_details_tab:
#     #     raise Exception("Not on Task page: Patient Details tab not found")
#     await asyncio.sleep(5)

 
#     # 8. Click on Search icon
#     # search_drug_icon = find_element_across_frames(page, '(//td[@data-attribute-name=".pyTemplateInputBox"]/div/span/i/img)[1]')
#     # if not search_drug_icon:
#     #     search_drug_icon = await find_element_across_frames(page, '//img[contains(@data-click,"DrugLookup")]')
#     search_drug_icon = await find_element_across_frames(page, '(//td[@data-attribute-name=".pyTemplateInputBox"]/div/span/i/img)[1]')
#     # if not search_drug_icon:
#     #     search_drug_icon = await find_element_across_frames(page, '//img[contains(@data-click,"DrugLookup")]')
#     if not search_drug_icon:
#         raise Exception("Drug search icon not found")
#     await search_drug_icon.click()
#     await asyncio.sleep(2)

#     # 9. Click Clear
#     clear_btn = await find_element_across_frames(page, '//button[@name="TherapyAndDrugLookup_pyWorkPage.Document.DrugList(1)_17"]')
#     if not clear_btn:
#         raise Exception("Drug Clear button not found")
#     await clear_btn.click()
#     await asyncio.sleep(1)

#     search_drug_input = await find_element_across_frames(page, '//input[@id="7a12dd37"]')
#     if not search_drug_input:
#         raise Exception("Drug input search box not found.")
#     await search_drug_input.fill("00074055402")
#     await asyncio.sleep(2)

#     # 10. Click Search
#     search_btn = await find_element_across_frames(page, '//button[@name="TherapyAndDrugLookup_pyWorkPage.Document.DrugList(1)_18"]')
#     if not search_btn:
#         raise Exception("Drug Search button not found")
#     await search_btn.click()
#     await asyncio.sleep(2)

#     xpath = '//table[contains(@grid_ref_page,".DrugList")]/tbody/tr/td//input[@type="radio"]'
#     humira_row_radio = await find_element_across_frames(page, xpath)
#     if not humira_row_radio:
#         raise Exception("Could not find HUMIRA 40 MG/0.4 ML PEN 2'S (NDC: 00074055402) radio in drug results")
#     await humira_row_radio.click()
#     await asyncio.sleep(1)

#     # 12. Click Submit
#     selected_drug_submit = await find_element_across_frames(page, "//*[@name='DrugLookUpModalTabUI_pyWorkPage.Document.DrugList(1)_96']")
#     if not selected_drug_submit:
#         selected_drug_submit = await find_element_across_frames(page, 'button[text()="Submit"]')
#     if not selected_drug_submit:
#         selected_drug_submit = await find_element_across_frames(page, '//button[text()="Submit"]')
#     if not selected_drug_submit:
#         raise Exception("Drug Submit button not found")
#     await selected_drug_submit.click()
#     await asyncio.sleep(3)

    
   
    
#     # 6. Click on Update Task (Intake) under Name column
#     update_task_selector = await find_element_across_frames(page, 'a[partialLinkText="Update Task (Intake)"]')
#     if not update_task_selector:
#         update_task_selector = await find_element_across_frames(page, 'a:has-text("Update Task (Intake)")')
#         if not update_task_selector:
#             update_task_selector = await find_element_across_frames(page, 'a.Update Task (Intake)')
#         if not update_task_selector:
#             # Try with locator from "updateTask"
#             update_task_selector = await find_element_across_frames(page, 'a[partialLinkText="Update Task (Intake)"]')
#     if not update_task_selector:
#         raise Exception("Update Task (Intake) link not found")
#     await update_task_selector.click()
#     await asyncio.sleep(5)


#     # Handle any popup windows, dialogs, or overlays
#     await handle_popups(page)

#     #--- Step 9: Add Therapy and Place of Service in Drug Tab ---
#     # drug_tab = await find_element_across_frames(page, "//h3[text()='Drug']")
#     # if not drug_tab:
#     #     raise Exception("Drug tab not found")
#     # drug_tab.click()
#     # sleep(2)

#     # drug_tab = page.locator("h3.layout-group-item-title:has-text('Drug')").first
#     # if not drug_tab.is_visible():
#     #     raise Exception("Drug tab not found")
#     # drug_tab.click()


#     # Select Therapy Type: HUMA
#     therapy_type = await find_element_across_frames(page, "input[name='$PpyWorkPage$pDocument$pDrugList$l1$pTherapyType']")
#     if not therapy_type:
#         therapy_type = await find_element_across_frames(page, "select[name='$PpyWorkPage$pDocument$pDrugList$l1$pTherapyType']")
#     if not therapy_type:
#         raise Exception("Therapy Type input not found")
#     await therapy_type.fill("HUMA")
#     await asyncio.sleep(1)

#     # Select Place of Service: Home
#     place_of_service = await find_element_across_frames(page, "input[name='$PpyWorkPage$pDocument$pDrugList$l1$pPOSDescription']")
#     if not place_of_service:
#         place_of_service = await find_element_across_frames(page, "select[name='$PpyWorkPage$pDocument$pDrugList$l1$pPOSDescription']")
#     if not place_of_service:
#         raise Exception("Place of Service dropdown not found")
#     await place_of_service.select_option(label="Home")
#     await asyncio.sleep(1)


#     await asyncio.sleep(5)

#     ##--- Step 10: Link Patient Record ---
#     patient_tab = await find_element_across_frames(page, "//h3[text()='Patient Details']")
#     if not patient_tab:
#         raise Exception("Patient Details tab not found")
#     await patient_tab.click()
#     await asyncio.sleep(5)

#     patient_tab = await find_element_across_frames(page, "//h3[text()='Patient Details']")
#     if not patient_tab:
#         raise Exception("Patient Details tab not found")
#     await patient_tab.click()
#     await asyncio.sleep(5)

#     patient_lookup_icon = await find_element_across_frames(page, 'img[data-template=""][data-click*="PatientLookUp"]')
#     if not patient_lookup_icon:
#         patient_lookup_icon = await find_element_across_frames(page, "select[name='PatientDetailsTab_pyWorkPage.Document_45']")
#     if not patient_lookup_icon:
#         raise Exception("Patient Lookup icon not found")
#     await patient_lookup_icon.click()
#     await asyncio.sleep(2)

#     # Click Clear (in lookup modal)
#     patient_lookup_clear_btn = await find_element_across_frames(page, "//button[@name='PatientLookUp_pyWorkPage.Document.Patient_26']")
#     # if not patient_lookup_clear_btn:
#     #     # fallback: generic clear in dialog
#     #     patient_lookup_clear_btn = await find_element_across_frames(page, "//button[text()='Clear']")
#     if not patient_lookup_clear_btn:
#         raise Exception("Clear button in patient lookup not found")
#     await patient_lookup_clear_btn.click()
#     await asyncio.sleep(1)

#     # Enter Patient ID (from DaaS tool)
#     patient_id_input = await find_element_across_frames(page, "input[name='$PpyTempPage$pPatientID']")
#     if not patient_id_input:
#         raise Exception("Patient ID input not found")
#     await patient_id_input.fill("17037448")
#     await asyncio.sleep(1)

#     # Click Search
#     search_btn = await find_element_across_frames(page, "//button[contains(text(),'Search')]")
#     if not search_btn:
#         raise Exception("Search button in patient lookup not found")
#     await search_btn.click()
#     await asyncio.sleep(2)

#     # Select the record with SB = 555
#     # Need to find table row/cell with SB == '555', click its radio or select option in grid.
#     found = False
#     for row in range(1, 6):  # Try first 5 results/rows
#         print("Inside loop")
#         sb_cell_xpath = f"(//table[contains(@grid_ref_page,'pyWorkPage.Document.Patient')]/tbody/tr[contains(@class,'Row')])[{row}]/td[4]/div/div/div/div/div/div/div/span"
#         sb_cell = await find_element_across_frames(page, sb_cell_xpath)
#         print(sb_cell)
#         if sb_cell:
#             sb_val = await sb_cell.inner_text()
#             sb_val = sb_val.strip()
#             print(f"{row}, {sb_val}")
#             if sb_val == "555":
#                 radio_xpath = f"(//table[contains(@grid_ref_page,'pyWorkPage.Document.Patient')]/tbody/tr[contains(@class,'Row')])[{row}]/td[2]//input[@type='radio']"
#                 radio = await find_element_across_frames(page, radio_xpath)
#                 if not radio:
#                     raise Exception(f"Radio for SB=555 not found in row {row}")
#                 await radio.click()
#                 found = True
#                 break
#     if not found:
#         raise Exception("Patient record with SB=555 not found")
#     await asyncio.sleep(1)

#     # Click Submit
#     submit_btn = await find_element_across_frames(page, "#ModalButtonSubmit")
#     if not submit_btn:
#         submit_btn = await find_element_across_frames(page, "button#ModalButtonSubmit")
#     if not submit_btn:
#         submit_btn = await find_element_across_frames(page, "//button[@id='ModalButtonSubmit']")
#     if not submit_btn:
#         raise Exception("Submit button in patient lookup not found")
#     await submit_btn.click()
#     await asyncio.sleep(3)

#        # From Address List, select any address
#     address_dropdown = await find_element_across_frames(page, "#ded594e9")
#     if not address_dropdown:
#         raise Exception("Address dropdown not found")
#     await address_dropdown.select_option(index=1)
#     await asyncio.sleep(5)
    

#     # --- Step 11: Complete Prescriber/Category ---
#     prescriber_tab = await find_element_across_frames(page, "//h3[text()='Prescriber / Category / Team']")
#     if not prescriber_tab:
#         raise Exception("Prescriber / Category / Team tab not found")
#     await prescriber_tab.click()
#     await asyncio.sleep(5)



    

#     # Select any team in the input if blank
#     input_prescr_team = await find_element_across_frames(page, "input[name='$PpyWorkPage$pDocument$pTeamName']")
#     if input_prescr_team:
#         current_value = await input_prescr_team.input_value()
#         current_value = current_value.strip() if hasattr(input_prescr_team, "input_value") else ""
#         if not current_value:
#             await input_prescr_team.fill("TEAM 1")
#             await asyncio.sleep(1)
#     # else: ignore if no input (sometimes not required)

#     await asyncio.sleep(1)

#     # --- Step 12: Complete the Intake T-Task id ---
#     # Click Submit (for task)
#     task_submit_btn = await find_element_across_frames(page, "button[name='CommonFlowActionButtons_pyWorkPage_17']")
#     if not task_submit_btn:
#         task_submit_btn = await find_element_across_frames(page, "//button[@title='Complete this assignment']")
#     if not task_submit_btn:
#         task_submit_btn = await find_element_across_frames(page, "//button[text()='Submit']")
#     if not task_submit_btn:
#         raise Exception("Submit button on task page not found")
#     await task_submit_btn.click()
#     await asyncio.sleep(5)

# if __name__ == "__main__":
#     from playwright.sync_api import sync_playwright
    
#     def on_new_page(page):
#         try:
#             # Increase the wait time or use a more targeted wait
#             page.wait_for_load_state('domcontentloaded', timeout=8000) # Increased timeout to 30 seconds

#             title = page.title()
#             url = page.url

#             print(f"New page detected:")
#             print(f"  Title: {title}")
#             print(f"  URL: {url}")

#             if 'Untitled' in title or 'about:blank' in title: # Also check for empty title
#                 print('Potentially unwanted blank page/popup detected -> closing it')
#                 page.close()
#                 return   

#             # Then check for your specific unwanted popups
#             if 'Show EIS Image' in title or 'Document.LaunchImageViewerWindow' in url:
#                 print('Specific unwanted popup detected -> closing it')
#                 page.close()
#             else:
#                   print("keeping page open (not matching criteria)")
#         except Exception as e:
#             print(f"Could not get title/url for new page: {e}")
    
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)
#         context = browser.new_context()
        
#         # Set up automatic popup handling
#         context.on("page", on_new_page)
        
#         page = context.new_page()
        
#         try:
#             step(page)
#             print("Step execution completed successfully!")
#         except Exception as e:
#             print(f"Error during execution: {e}")
#         finally:
#             browser.close()

async def run_clearance_automation(page):
    """Run Clearance automation using agent_utils, application_config, and automation_config."""
    print("🚀 Starting Clearance automation...")
    
    # Initialize application registry
    app_registry = ApplicationRegistry()
    clearance_config = app_registry.get_application("Clearance")
    
    # Get Clearance URL from automation_config
    clearance_url = APPLICATION_URLS["Clearance"]
    print(f"📍 Navigating to Clearance: {clearance_url}")
    await page.goto(clearance_url)
    await asyncio.sleep(3)
    
    # Login to Clearance using robust selectors
    print("🔐 Logging into Clearance...")
    
    # Username - try multiple selectors
    username_selectors = [
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
    
    username = await find_element_across_frames(page, username_selectors[0])
    if not username:
        # Try alternative selectors
        for selector in username_selectors[1:]:
            username = await find_element_across_frames(page, selector)
            if username:
                print(f"✅ Found username field with selector: {selector}")
                break
    
    if not username:
        raise Exception("Username input not found")
    
    await robust_fill(page, username_selectors[0], DEFAULT_USERNAME)
    await asyncio.sleep(1)

    # Password - try multiple selectors
    password_selectors = [
        'input[name="Password"]',
        'input[name="password"]',
        'input[name="PASSWORD"]',
        'input[type="password"]',
        'input[placeholder*="password" i]',
        'input[placeholder*="pass" i]',
        'input[id*="password" i]',
        'input[id*="pass" i]'
    ]
    
    password = await find_element_across_frames(page, password_selectors[0])
    if not password:
        # Try alternative selectors
        for selector in password_selectors[1:]:
            password = await find_element_across_frames(page, selector)
            if password:
                print(f"✅ Found password field with selector: {selector}")
                break
    
    if not password:
        raise Exception("Password input not found")
    
    await robust_fill(page, password_selectors[0], DEFAULT_PASSWORD)
    await asyncio.sleep(1)

    # Login button - try multiple selectors
    login_button_selectors = [
        'button#sub',
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
    
    login_btn = await find_element_across_frames(page, login_button_selectors[0])
    if not login_btn:
        # Try alternative selectors
        for selector in login_button_selectors[1:]:
            login_btn = await find_element_across_frames(page, selector)
            if login_btn:
                print(f"✅ Found login button with selector: {selector}")
                break
    
    if not login_btn:
        raise Exception("Login button not found")
    
    await robust_click(page, login_button_selectors[0])
    await asyncio.sleep(3)
    
    # Handle any popups after login
    await handle_popups(page)
    
    # Advanced Search
    print("🔍 Performing Advanced Search...")
    advanced_search_selectors = [
        'button:has-text("Advanced Search")',
        'button[text()="Advanced Search"]',
        'button:contains("Advanced Search")',
        'a:has-text("Advanced Search")',
        'input[value="Advanced Search"]',
        'button[id*="advanced" i]',
        'button[id*="search" i]'
    ]
    
    advanced_search_btn = await find_element_across_frames(page, advanced_search_selectors[0])
    if not advanced_search_btn:
        # Try alternative selectors
        for selector in advanced_search_selectors[1:]:
            advanced_search_btn = await find_element_across_frames(page, selector)
            if advanced_search_btn:
                print(f"✅ Found Advanced Search button with selector: {selector}")
                break
    
    if not advanced_search_btn:
        raise Exception("Advanced Search button not found")
    
    await robust_click(page, advanced_search_selectors[0])
    await asyncio.sleep(2)
    
    # Enter Patient ID in RxHome ID field
    print(f"👤 Searching for Patient ID: {PATIENT_ID}")
    rxhome_id_selectors = [
        'input[name="RxHomeID"]',
        'input[name="PatientID"]',
        'input[name="patient_id"]',
        'input[placeholder*="RxHome" i]',
        'input[placeholder*="Patient" i]',
        'input[placeholder*="ID" i]',
        'input[id*="rxhome" i]',
        'input[id*="patient" i]',
        'input[aria-label*="RxHome" i]',
        'input[aria-label*="Patient" i]'
    ]
    
    rxhome_id_input = await find_element_across_frames(page, rxhome_id_selectors[0])
    if not rxhome_id_input:
        # Try alternative selectors
        for selector in rxhome_id_selectors[1:]:
            rxhome_id_input = await find_element_across_frames(page, selector)
            if rxhome_id_input:
                print(f"✅ Found RxHome ID field with selector: {selector}")
                break
    
    if not rxhome_id_input:
        raise Exception("RxHome ID input not found")
    
    await robust_fill(page, rxhome_id_selectors[0], PATIENT_ID)
    await asyncio.sleep(1)
    
    # Click Search
    search_button_selectors = [
        'button:has-text("Search")',
        'button[text()="Search"]',
        'button:contains("Search")',
        'input[type="submit"][value="Search"]',
        'button[id*="search" i]',
        'button[class*="search" i]',
        'input[type="submit"]',
        'button[type="submit"]'
    ]
    
    search_btn = await find_element_across_frames(page, search_button_selectors[0])
    if not search_btn:
        # Try alternative selectors
        for selector in search_button_selectors[1:]:
            search_btn = await find_element_across_frames(page, selector)
            if search_btn:
                print(f"✅ Found Search button with selector: {selector}")
                break
    
    if not search_btn:
        raise Exception("Search button not found")
    
    await robust_click(page, search_button_selectors[0])
    await asyncio.sleep(3)
    
    # Handle any popups after search
    await handle_popups(page)
    
    print("✅ Clearance automation completed successfully!")

async def step_with_clearance(page):
    """Run Intake followed by Clearance automation."""
    print("🚀 Starting Multi-Application Workflow: Intake → Clearance")
    print("="*80)
    
    try:
        # Step 1: Run Intake automation
        print("\n=== STEP 1: INTAKE AUTOMATION ===")
        await step(page)
        
        # Step 2: Run Clearance automation
        print("\n=== STEP 2: CLEARANCE AUTOMATION ===")
        await run_clearance_automation(page)
        
        print("\n✅ Multi-application workflow completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during multi-application workflow: {e}")
        raise

async def step_with_all_apps(page):
    """Run Intake → Clearance → RxP automation."""
    print("🚀 Starting Multi-Application Workflow: Intake → Clearance → RxP")
    print("="*80)
    
    try:
        # Step 1: Run Intake automation
        print("\n=== STEP 1: INTAKE AUTOMATION ===")
        await step(page)
        
        # Step 2: Run Clearance automation
        print("\n=== STEP 2: CLEARANCE AUTOMATION ===")
        await run_clearance_automation(page)
        
        # Step 3: Run RxP automation
        print("\n=== STEP 3: RXP AUTOMATION ===")
        await run_rxp_automation(page)
        
        print("\n✅ Multi-application workflow completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during multi-application workflow: {e}")
        raise

async def run_rxp_automation(page):
    """Run RxP automation using the same patient ID from Intake."""
    print("🚀 Starting RxP automation...")
    
    # Navigate to RxP
    rxp_url = "https://sprxp-qa.express-scripts.com/sprxp/"
    await page.goto(rxp_url)
    
    # Login to RxP
    username = await find_element_across_frames(page, 'input[name="UserIdentifier"]')
    if not username:
        raise Exception("Username input not found")
    await username.fill("C9G5JS")
    await asyncio.sleep(1)

    password = await find_element_across_frames(page, 'input[name="Password"]')
    if not password:
        raise Exception("Password input not found")
    await password.fill("Emphatic-Award1-Tinker")
    await asyncio.sleep(1)

    login_btn = await find_element_across_frames(page, 'button#sub')
    if not login_btn:
        raise Exception("Login button not found")
    await login_btn.click()
    await asyncio.sleep(3)
    
    # Advanced Search
    advanced_search_btn = await find_element_across_frames(page, 'button:has-text("Advanced Search")')
    if not advanced_search_btn:
        raise Exception("Advanced Search button not found")
    await advanced_search_btn.click()
    await asyncio.sleep(2)
    
    # Enter Patient ID in RxHome ID field
    rxhome_id_input = await find_element_across_frames(page, 'input[name="RxHomeID"]')
    if not rxhome_id_input:
        raise Exception("RxHome ID input not found")
    await rxhome_id_input.fill(PATIENT_ID)  # Use the configured Patient ID
    await asyncio.sleep(1)
    
    # Click Search
    search_btn = await find_element_across_frames(page, 'button:has-text("Search")')
    if not search_btn:
        raise Exception("Search button not found")
    await search_btn.click()
    await asyncio.sleep(3)
    
    print("✅ RxP automation completed successfully!")

async def automation():
    """Run the automation with proper async handling."""
    from playwright.async_api import async_playwright
    
    async def on_new_page(page):
        try:
            # Increase the wait time or use a more targeted wait
            await page.wait_for_load_state('domcontentloaded', timeout=30000) # Increased timeout to 30 seconds

            title = await page.title()
            url = page.url

            print(f"New page detected:")
            print(f"  Title: {title}")
            print(f"  URL: {url}")

            if 'Untitled' in title or 'about:blank' in title: # Also check for empty title
                print('Potentially unwanted blank page/popup detected -> closing it')
                await page.close()
                return   

            # Then check for your specific unwanted popups
            if 'Show EIS Image' in title or 'Document.LaunchImageViewerWindow' in url:
                print('Specific unwanted popup detected -> closing it')
                await page.close()
            else:
                  print("keeping page open (not matching criteria)")
        except Exception as e:
            print(f"Could not get title/url for new page: {e}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        # Set up automatic popup handling
        context.on("page", on_new_page)
        
        page = await context.new_page()
        
        try:
            await run_clearance_automation(page)
            print("Clearance automation completed successfully!")
        except Exception as e:
            print(f"Error during execution: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    
    def on_new_page(page):
        try:
            # Increase the wait time or use a more targeted wait
            page.wait_for_load_state('domcontentloaded', timeout=30000) # Increased timeout to 30 seconds

            title = page.title()
            url = page.url

            print(f"New page detected:")
            print(f"  Title: {title}")
            print(f"  URL: {url}")

            if 'Untitled' in title or 'about:blank' in title: # Also check for empty title
                print('Potentially unwanted blank page/popup detected -> closing it')
                page.close()
                return   

            # Then check for your specific unwanted popups
            if 'Show EIS Image' in title or 'Document.LaunchImageViewerWindow' in url:
                print('Specific unwanted popup detected -> closing it')
                page.close()
            else:
                  print("keeping page open (not matching criteria)")
        except Exception as e:
            print(f"Could not get title/url for new page: {e}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        
        # Set up automatic popup handling
        context.on("page", on_new_page)
        
        page = context.new_page()
        
        try:
            step(page)
            print("Step execution completed successfully!")
        except Exception as e:
            print(f"Error during execution: {e}")
        finally:
            browser.close()
