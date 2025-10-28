Feature: End-to-End Trend Biosimilar Test for Integrated Patient Fax Referral Workflow

Scenario: Validate Integrated Patient Fax Referral workflow from Intake through RxProcessing to CRM Order Scheduling

  Given I launch the Intake application in Chrome or Edge
  And I log in with valid LAN ID and Password
  When I enter the Common Intake ID in the search box and press Enter
  And I click the T-Task Id link to navigate to the Case Contents page
  And I click on Update Task (Intake) to open the Task page and EIS Image Window
  And I close the EIS Image Window to view the full Task page
  And I go to the Drug tab and click the Search icon
  And I clear the search, enter Drug Name "HUMIRA", click Search, select "HUMIRA 40 MG/0.4 ML PEN 2'S (NDC: 00074055402)", and click Submit
  And I click on Update Task (Intake) with status "Pending Progress" to reopen the Task page
  And I select Therapy Type "HUMA" and Place of Service "Clinic" in the Drug tab and save the values
  And I go to the Patient tab, click the Search icon, clear, enter the Patient ID, click Search, select the record with SB = 799, and click Submit
  And I select any address from the Address List and select a team in the Prescriber/Category Team tab if blank
  And I click Submit to complete the Intake T-Task id
  Then I confirm the Task status changes to "Completed" in the Case Contents page

  When I launch the RxProcessing application in Chrome or Edge
  And I log in with valid LAN ID and Password
  And I click Advanced Search, clear, enter the Patient ID in the RxHome ID field, and click Search
  And I click Open Case for the corresponding patient and minimize the advanced search window
  And in the Referral Contents section, I click Begin and Link image in Viewer
  And I select DAW code "0"
  And I search and select drug "HUMIRA 40 MG/0.4 ML PEN 2'S (NDC: 00074055402)"
  And I click Common SIG and select "INJECT 40 MG (0.8 ML) UNDER THE SKIN EVERY 14 DAYS"
  And I enter Qty "1", Days Supply "14", Doses "1", Refills "1"
  And I click Apply Rules and then Reviewed
  And in the Prescriber section, I clear, enter NPI "1336183888", click Search, select a phone and fax/autofax number, and click Submit
  And I click Accept Changes
  Then I verify that Full Name, DOB, Gender, Age, Address, and Phone are auto populated in the Patient section and tick the checkbox if all values are populated
  And I verify that Prescribed Drug, Dispensed Drug, and Dispensed Drug Comments are auto populated in the Medication section and tick the checkbox if all values are populated
  And I verify that SIG Text, Prescribed Quantity, Prescribed Days Supply, Prescribed Doses, Prescribed Refills, Dispensed Quantity, Dispensed Days Supply, Dispensed Doses, Dispensed Refills, Date Written, Rx Expires, DAW Code, and Rx Origin Code are auto populated in the Rx Details section and tick the checkbox if all values are populated
  And I verify that Prescriber, Prescriber ID, Address, Phone, FAX, NPI, and DEA are auto populated in the Prescriber section and tick the checkbox if all required values are populated
  And I ensure all four checkboxes are selected or flag for manual review if any are unpopulated
  When I click Next to invoke Trend Processing logic
  Then I confirm the confirmation banner "Case submitted to Pending - Trend work Queue" appears
  And I click Close to return to the RxP homepage

  When I retrieve the REF Case by clicking Begin and land in the Order Summary Screen
  Then I confirm Prescribed Drug is "HUMIRA 40 MG/0.4 ML PEN 2'S (NDC: 00074055402)" and DAW Code is "0"
  And I click Submit and wait 1 to 2 minutes

  When I open Advanced Search, enter the REF Id in Case Id field, click Search, and click Open Case
  And I click Begin to navigate to the RPh Verification main page
  Then I confirm the red letter "A" appears on the image and annotation indicates biosimilar substitution
  And I click Verify in each of the five areas: Patient Details, Prescription Info, Prescription Details, Additional Details, and Prescriber
  And I click Submit if available, or click Next and proceed through Drug Rules, RxSnapshot, and DUR screens, clicking Submit at each if available
  And for DUR alerts, I select "RPh Approved Professional Judgement" and click Submit
  Then I confirm the REF Case status is "Resolved-Completed" after searching by REF Id in Advanced Search

  When I launch the CRM application in Chrome or Edge
  And I log in with valid LAN ID and Password
  And I click New and Simulate Workspace Interaction
  And I clear all pre-populated fields, enter the Patient ID, and click Next
  And on the Patient Verification & Caller Information page, I select the first three checkboxes under Verification Methods
  And I select "Patient" from Relationship to Patient
  And I select "HUMA" under Medication list
  And I choose "No" for "Has the patient missed doses or is the patient at risk of missing a dose within the next 3 days"
  And I click Next to land at Order Status View and navigate to Dashboard View
  And in Ready to Fill, I confirm the medication appears and click Order
  And on the Prescription List Screen, I select the medication with a checkmark under Schedule/Cancel and click Continue
  Then I confirm the Orange banner is displayed and validate its verbiage
  And I select "No" for "Patient New to Medication?" and "Yes" for "Do you have enough medication on hand for next 3 days?"
  And I click Next to arrive at the Review Screen
  And I click Next, select "No" under Clinical Transfer, select "Patient declined Pharmacist counseling" under Clinical Transfer to Pharmacist, and click Address Check
  And in the Verify Address Displayed pop-up, I click Address CONFIRMED
  Then I confirm the system lands on Dashboard View
  And on the Dashboard View, I navigate to the Notes tab and validate a new entry is posted for date/timestamp of Address Confirmation