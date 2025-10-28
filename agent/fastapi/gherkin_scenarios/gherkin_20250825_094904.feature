Feature: Direct Patient Fax Referral End-to-End Workflow - Reject 75 Status Validation

Scenario: Validate that a dummy fax referral is rejected with Reject 75 status and workflow is halted across all interconnected applications

  Given I launch the Intake application and log in with valid credentials
  And I search for the referral using the Common Intake ID in the Intake application
  When I open the T-Task ID from the search results
  And I close the EIS Image Window
  And I navigate to the Drug tab and perform a drug lookup for NDC "00378696093"
  And I select "GLATIRAMER 20MG PFS 30's (NDC: 00378696093)" and submit
  Then I verify the T-Task ID status is "Pending Progress"
  When I open the Intake task with status "Pending Progress"
  And I close the EIS Image Window
  And I select Therapy Type "GLAT" and Place of Service "Home" in the Drug tab
  And I link the patient record with SB "555" in the Patient tab
  And I select any address if blank in the Address List
  And I enter and select "ACUTE 1" under Team dropdown in the Prescriber/Category Team tab if blank
  And I submit to complete the Intake T-Task ID
  Then I verify the Task status changes to "Completed" in the Case Contents page

  Given I launch the Clearance application and log in with valid credentials
  And I search for the patient case using Patient ID "17164196"
  When I select the case with ID starting with "IE-"
  And I open the Direct Patient Referral IE-ID to land on the Eligibility tab
  And I enter Place of Service ID "12" in the Payer section
  And I ensure Billing Sequence is "01-Primary", Benefit type is "PBM", MAIL NPI is unchecked
  And I enter BIN "610140", PCN "D0TEST", Group Number "D0TEST" and search
  And I enter Cardholder ID "555757575", Person Code "01", Insurance Effective Date as today's date, and Relationship "1-Self" in Policy Holder Information
  And I save the policy information
  Then I verify the banner "Insurance details saved successfully" appears
  When I select the checkbox under Drugs
  And I enter "1730" under Select Primary Payer for Service(s) and select from the dropdown
  And I assign Co-Pay as "P"
  And I finish to complete the Clearance Task
  Then I verify the task is marked as completed and the screen resets to blank

  Given I launch the RxP application and log in with valid credentials
  And I search for the patient case using Patient ID "17164196" in Advanced Search
  When I open the case for the patient and begin the Referral Task
  And I link image in Viewer and select DAW code "0"
  And I search and select drug "GLATIRAMER 20MG PFS 30's NDC 00378696093"
  And I select Common SIG "INJECT 20 MG (1 ML) UNDER THE SKIN DAILY"
  And I enter Qty "1", Days Supply "14", Doses "1", Refills "1"
  And I apply rules and mark as reviewed
  Then I verify all required fields in Patient, Medication, Rx Details, and Prescriber sections are populated and tick the corresponding checkboxes
  And I click Next and close to return to the RxP homepage

  When I search for the patient case again in Advanced Search
  And I open the case and begin the REF Case in Order Summary Screen
  Then I confirm Prescribed Drug is "GLATIRAMER" and Dispensed Drug is "GLATOPA"
  And I submit and close to return to the RxP homepage

  When I search for the patient case in Advanced Search and expand the case
  Then I verify the "Assigned To" status is "Pending Clearance"

  When I search for the patient case in Advanced Search and expand the case
  Then I verify the referral is rejected with Reject 75 status

  When the REF-ID status is "Pending Clearance"
  And I enter the REF Id in Case Id field, search, expand the case, select "Re-Adjudicate" under Rx-Level Action, and submit
  Then I verify Reject 75 status with reason is displayed

  Then I verify that the workflow is stopped and does not proceed to RxProcessing RPh Verification, Trend Processing, or CRM Order Scheduling
  And I verify that no order is scheduled in CRM for the rejected referral