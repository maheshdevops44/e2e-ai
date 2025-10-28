Feature: End-to-End Integrated Patient Fax Referral Workflow for Trend Biosimilar - Humira

Scenario: Validate successful ingestion, processing, and order scheduling for an Integrated Patient Fax Referral with Humira in the Trend Biosimilar scenario

  Given I launch the Intake application in Chrome or Edge and log in with valid credentials
  And I enter the Common Intake ID in the search box and press Enter
  When I locate and click the T-Task Id link under the ID column in the pop-up window
  And I click on Update Task (Intake) under the "Name" column on the Case Contents page
  And I close the EIS Image Window
  And I go to the Drug tab and click the Search icon
  And I clear the Drug Lookup window, enter Drug Name "HUMIRA", click Search, select "HUMIRA 40 MG/0.4 ML PEN 2'S (NDC: 00074055402)", and click Submit
  And I return to the Case Contents page and click on Update Task (Intake) with status "Pending Progress"
  And I select Therapy Type "HUMA" and Place of Service "Clinic" in the Drug tab
  And I go to the Patient tab, click the Search icon next to the Patient ID field, clear, enter the Patient ID, click Search, select the record with SB = 799, and click Submit
  And I select any address from the Address List
  And I select "ARTH MHS" as the team in the Prescriber/Category Team tab if blank
  And I click Submit to complete the Intake T-Task id
  Then I confirm the task status changes to "Completed" in the Case Contents page

  Given the Intake referral is completed for the Integrated Patient
  When the Clearance application auto-completes the case in the background
  Then the case transitions to RxProcessing (RxP) for Order Entry

  Given I launch the RxP application in Chrome or Edge and log in with valid credentials
  And I click on Advanced Search, clear, enter the Patient ID in the RxHome ID field, and click Search
  When I click Open Case for the corresponding patient and minimize the advanced search window
  And I click Begin in the Referral Contents section and link image in Viewer
  And I select DAW code "0"
  And I search and select drug "HUMIRA 40 MG/0.4 ML PEN 2'S (NDC: 00074055402)"
  And I select Common SIG "INJECT 40 MG (0.8 ML) UNDER THE SKIN EVERY 14 DAYS"
  And I enter Qty = 1, Days Supply = 14, Doses = 1, Refills = 1
  And I click Apply Rules and then Reviewed
  And I clear the Prescriber section, enter NPI "1336183888", click Search, select a phone and fax/autofax number, and click Submit
  And I click Accept Changes
  Then I verify all fields in Patient, Medication, Rx Details, and Prescriber sections are correctly auto-populated and tick the associated checkbox for each section
  And I ensure all four checkboxes are selected; if any values are unpopulated, I leave that section's checkbox unchecked and flag for manual review
  When I click Next to invoke Trend Processing logic in the background
  Then I confirm the appearance of the confirmation banner "Case submitted to Pending - Trend work Queue. Click Close to proceed to next case"
  And I click Close to return to the RxP homepage

  Given Trend Processing background biosimilar conversion logic completes
  When I retrieve the REF Case by clicking Begin
  Then I confirm Prescribed Drug is "HUMIRA 40 MG/0.4 ML PEN 2'S" and Dispensed Drug is biosimilar (e.g., ADALIMUMAB-ADBM)
  And I click Submit

  Given the REF Case is available for RPh Verification
  When I open Advanced Search, enter the REF Id in the Case Id field, click Search, and click Open Case
  And I click Begin to navigate to the RPh Verification main page
  Then I confirm the red letter "A" appears on the image and validate the annotation indicating biosimilar substitution
  And I click the first Verify button in Patient Details area
  And I click the second Verify button in Prescription Info area
  And I click the third Verify button in Prescription Details area
  And I click the fourth Verify button in Additional Details area
  And I click the fifth Verify button in Prescriber area
  When I click Submit if available; if not, I click Next and proceed through Drug Rules, RxSnapshot, and DUR screens, clicking Submit at each if available
  And on the DUR screen, I resolve any DUR Alerts by selecting "RPh Approved Professional Judgement" and click Submit
  Then I confirm the REF Case status is "Resolved-Completed" after searching by REF Id in Advanced Search

  Given I launch the CRM application in Chrome or Edge and log in with valid credentials
  When I click New and Simulate Workspace Interaction
  And I clear all pre-populated fields and enter the Patient ID in the Patient ID field, then click Next
  Then I confirm the Patient ID field is displayed on the Patient Verification & Caller Information page
  And I select the first three checkboxes under Verification Methods
  And I select "Patient" from the Relationship to Patient drop-down menu
  And I select "HUMA" under Medication list
  And I choose "No" for "Has the patient missed doses or is the patient at risk of missing a dose within the next 3 days?"
  And I click Next to land at Order Status View and navigate to Dashboard View
  And in Ready to Fill, I confirm the medication for the test case appears and click the Order button
  And on the Prescription List Screen, I select the medication corresponding to the Rx# with a checkmark under Schedule/Cancel and click Continue
  Then I confirm the orange banner is displayed and validate the verbiage
  And I select "No" for "Patient New to Medication?" and "Yes" for "Do you have enough medication on hand for next 3 days?"
  And I click Next to arrive at the Review Screen
  And I click Next, select "No" under Clinical Transfer, and "Patient declined Pharmacist counseling" under Clinical Transfer to Pharmacist
  And I click Address Check to display the Verify Address Displayed pop-up window
  And I click Address CONFIRMED to land on Dashboard View
  Then on the Dashboard View, I navigate to the Notes tab and validate a new entry is posted for the date/timestamp of Address Confirmation

  And at each step, I verify that all relevant data is accurately reflected in backend databases and user interfaces as described in the SOP