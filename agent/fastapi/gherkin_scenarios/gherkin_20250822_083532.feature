Feature: End-to-End Validation of Direct Patient Fax Referral Workflow with Reject Status

Scenario: Ingest dummy Direct Patient Fax Referral and verify workflow stops at reject stage

  Given the QA Tester launches the Intake application and logs in with valid credentials
  And enters the Common Intake ID for the dummy fax referral in the search box
  When the T-Task Id is located and the Case Contents page is opened
  And the Intake Task is updated and the EIS Image Window is closed
  And the Drug Lookup window is opened and Drug Name "00378696093" is searched and selected
  And Therapy Type is set to "GLAT" and Place of Service is set to "Home"
  And the Patient record is linked using Patient ID and SB code "555"
  And the Prescriber/Category Team tab is filled with valid Prescriber NPI and fax number
  And the Intake T-Task is submitted
  Then the Intake task status should change to "Completed" in the Case Contents page

  Given the QA Tester launches the Clearance application and logs in with valid credentials
  When the Patient Case is searched using Patient ID
  And the case with ID starting with "IE-" is selected to open the Eligibility tab
  And Place of Service ID "12" is entered in the Payer section
  And Payer Information is entered with BIN "610140", PCN "D0TEST", Group Number "RTA"
  And Cardholder ID/Policy# "555757575", Person Code "001", and Insurance Effective Date are entered in Policy Information
  And the insurance details are saved
  Then the banner "Insurance details saved successfully" should appear
  And the Clearance Task is completed

  Given the QA Tester launches the RxP application and logs in with valid credentials
  When the Patient Case is searched using Patient ID
  And the Referral Task page is opened and DAW code "0" is selected
  And drug "GLAT" with NDC "00378696093" is selected and the appropriate SIG is chosen
  And Qty "1", Days Supply "30", Doses "1", and Refills "1" are entered
  And Apply Rules and Reviewed are clicked, and changes are accepted
  And all required fields in Patient, Medication, Rx Details, and Prescriber sections are verified and checkboxes are ticked
  And Next is clicked to invoke Trend Processing logic
  Then the banner "Case submitted to Pending - Trend work Queue. Click Close to proceed to next case" should appear
  And the QA Tester clicks Close to return to the RxP homepage

  When the Claim status is set to "Reject"
  Then the workflow should stop at the reject stage
  And RxProcessing RPh Verification should not be performed
  And Trend Processing should not be initiated
  And CRM Order Scheduling should not be performed
  And no order should be scheduled in CRM