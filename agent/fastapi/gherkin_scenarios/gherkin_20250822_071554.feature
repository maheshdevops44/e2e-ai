Feature: End-to-End Integrated Patient Fax Referral Workflow for Trend Biosimilar (Humira) Scenario

Scenario: Validate the complete workflow for an Integrated Patient Fax Referral with Therapy Type HUMA and Drug HUMIRA 40 MG/0.4 ML PEN 2'S (NDC: 00074055402) from Intake through RxProcessing to CRM Order Scheduling

  Given I launch the Intake application and log in with valid credentials
  And I search for the Common Intake ID in the Intake homepage
  When I open the T-Task Id from the search results to navigate to the Case Contents page
  And I open the Intake Task and close the EIS Image Window
  And I go to the Drug tab, search for HUMIRA, and select HUMIRA 40 MG/0.4 ML PEN 2'S (NDC: 00074055402)
  And I submit the drug selection and ensure the T-Task ID status is "Pending Progress"
  And I reopen the Intake Task with status "Pending Progress"
  And I select Therapy Type as HUMA and Place of Service as Clinic (Optional) in the Drug tab
  And I go to the Patient tab, search for the Patient ID, select the record with SB = 799, and link the patient record
  And I select the address from Address List and set the team as ARTH MHS if blank
  And I submit the Intake Task and verify the Task status changes to "Completed"

  When the Intake Task is completed for the Integrated Patient
  Then the Clearance logic is auto-completed in the background and the case is moved to RxProcessing

  Given I launch the RxProcessing application and log in with valid credentials
  And I search for the Patient ID in Advanced Search and open the corresponding case
  When I begin Order Entry, link the image in Viewer, and select DAW code as 0
  And I select HUMIRA 40 MG/0.4 ML PEN 2'S (NDC: 00074055402) as the drug
  And I select the Common SIG: INJECT 40 MG (0.8 ML) UNDER THE SKIN EVERY 14 DAYS
  And I enter Qty = 1, Days Supply = 14, Doses = 1, Refills = 1
  And I apply rules and mark the case as Reviewed
  And I enter Prescriber NPI 1336183888, select phone and fax/autofax, and submit
  Then I verify that Patient, Medication, Rx Details, and Prescriber sections are correctly auto populated and tick all four checkboxes if complete
  When I click Next to invoke Trend Processing logic
  Then I should see the banner "Case submitted to Pending - Trend work Queue. Click Close to proceed to next case"
  And I close to return to the RxProcessing homepage

  When I retrieve the REF Case and confirm Prescribed Drug is HUMIRA 40 MG/0.4 ML PEN 2'S and DAW Code is 0
  And I submit the case and wait for RPh Verification
  And I open the REF Case for RPh Verification
  Then I confirm the red letter "A" appears and annotation indicates biosimilar substitution
  And I sequentially verify Patient Details, Prescription Info, Prescription Details, Additional Details, and Prescriber areas
  And I submit through Drug Rules, RxSnapshot, and DUR screens, resolving any DUR Alerts with "RPh Approved Professional Judgement"
  Then I confirm the REF Case status is Resolved-Completed

  Given I launch the CRM application and log in with valid credentials
  When I start a new Simulate Workspace Interaction and enter the Patient ID
  Then I verify the Patient ID is displayed on the Patient Verification & Caller Information page
  And I select the first three Verification Methods checkboxes
  And I select Patient from Relationship to Patient
  And I select HUMA under Medication list
  And I choose No for "Has the patient missed doses or is the patient at risk of missing a dose within the next 3 days"
  And I proceed to Order Status View and Dashboard View
  When I confirm the medication appears in Ready to Fill and click Order
  And I select the medication with a checkmark under Schedule/Cancel and click Continue
  Then I confirm the Orange banner is displayed and validate its verbiage
  And I select No for "Patient New to Medication?" and Yes for "Do you have enough medication on hand for next 3 days?"
  And I proceed to the Review Screen and click Next
  And I select No for Clinical Transfer and "Patient declined Pharmacist counseling" for Clinical Transfer to Pharmacist
  And I click Address Check and confirm the address in the pop-up window
  Then I verify that the Dashboard View Notes tab contains a new entry for the date/timestamp of Address Confirmation