#!/usr/bin/env python3
"""
Application Configuration System
Defines configurations for 4 different applications to ensure consistent code generation.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import re
from dotenv import load_dotenv
import os
from pathlib import Path

dotenv_path = Path(__file__).resolve().parents[1]/"config"/".env"
load_dotenv(dotenv_path)

LAN_ID = os.getenv(LAN_ID)
LAN_PASSWORD = os.getenv(LAN_PASSWORD)

class ApplicationType(Enum):
    """Supported application types."""
    INTAKE = "Intake"
    CLEARANCE = "Clearance"
    CLAIMS = "Claims"
    AUTHORIZATION = "Authorization"
    RXP = "RxP"
    GENERIC = "Generic"

@dataclass
class ApplicationConfig:
    """Configuration for a specific application."""
    name: str
    type: ApplicationType
    base_url: str
    login_selectors: Dict[str, str]
    common_selectors: Dict[str, str]
    workflow_steps: List[Dict[str, Any]]
    element_patterns: Dict[str, List[str]]
    wait_times: Dict[str, int]
    credentials: Dict[str, str]
    special_handling: Dict[str, Any]

class ApplicationRegistry:
    """Registry for all application configurations."""
    
    def __init__(self):
        self.applications = self._initialize_applications()
    
    def _initialize_applications(self) -> Dict[str, ApplicationConfig]:
        """Initialize all application configurations."""
        return {
            "Intake": ApplicationConfig(
                name="Intake",
                type=ApplicationType.INTAKE,
                base_url="https://spcia-qa.express-scripts.com/spcia",
                login_selectors={
                    "username": "input[name='UserIdentifier']",
                    "password": "input[name='Password']",
                    "login_button": "button#sub"
                },
                common_selectors={
                    "search_field": "input[name='$PpyDisplayHarness$ppySearchText'], span.primary_search input, [role='textbox'][name='Enter text to search']",
                    "search_button": "button:has-text('Search'), button[type='submit']",
                    "results_table": "table, .results-table, [data-testid='results']",
                    "t_task_status": "(//*[@id='bodyTbl_right']/tbody/tr[2]/td[3]/div/span)",
                    "update_task_link": "a[partialLinkText='Update Task (Intake)'], a:has-text('Update Task (Intake)')",
                    "case_summary": "//div[text()='Case summary']",
                    "patient_details_tab": "(//h3[text()='Patient Details'])[1]",
                    "drug_search_icon": "(//td[@data-attribute-name='.pyTemplateInputBox']/div/span/i/img)[1], //img[contains(@data-click,'DrugLookup')]",
                    "drug_clear_button": "//button[@name='TherapyAndDrugLookup_pyWorkPage.Document.DrugList(1)_17']",
                    "drug_search_input": "//input[@id='7a12dd37']",
                    "drug_search_button": "//button[@name='TherapyAndDrugLookup_pyWorkPage.Document.DrugList(1)_18']",
                    "humira_radio": "//table[contains(@grid_ref_page,'.DrugList')]/tbody/tr/td//input[@type='radio']",
                    "drug_submit_button": "//*[@name='DrugLookUpModalTabUI_pyWorkPage.Document.DrugList(1)_96'], button[text()='Submit']",
                    "therapy_type": "input[name='$PpyWorkPage$pDocument$pDrugList$l1$pTherapyType'], select[name='$PpyWorkPage$pDocument$pDrugList$l1$pTherapyType']",
                    "place_of_service": "input[name='$PpyWorkPage$pDocument$pDrugList$l1$pPOSDescription'], select[name='$PpyWorkPage$pDocument$pDrugList$l1$pPOSDescription']",
                    "patient_lookup_icon": "img[data-template=''][data-click*='PatientLookUp'], select[name='PatientDetailsTab_pyWorkPage.Document_45']",
                    "patient_clear_button": "//button[@name='PatientLookUp_pyWorkPage.Document.Patient_26']",
                    "patient_id_input": "input[name='$PpyTempPage$pPatientID']",
                    "patient_search_button": "//button[contains(text(),'Search')]",
                    "patient_submit_button": "#ModalButtonSubmit, button#ModalButtonSubmit, //button[@id='ModalButtonSubmit']",
                    "address_dropdown": "#ded594e9",
                    "prescriber_tab": "//h3[text()='Prescriber / Category / Team']",
                    "team_input": "input[name='$PpyWorkPage$pDocument$pTeamName']",
                    "task_submit_button": "button[name='CommonFlowActionButtons_pyWorkPage_17'], //button[@title='Complete this assignment'], //button[text()='Submit']"
                },
                workflow_steps=[
                    {"action": "navigate", "description": "Navigate to Intake application"},
                    {"action": "login", "description": "Login with credentials"},
                    {"action": "wait", "description": "Wait for page load"},
                    {"action": "search", "description": "Search for intake ID"},
                    {"action": "view_results", "description": "View search results"}
                ],
                element_patterns={
                    "search_inputs": [
                        "input[placeholder*='intake']",
                        "input[placeholder*='search']",
                        "input[aria-label*='search']",
                        "input[name*='search']"
                    ],
                    "action_buttons": [
                        "button:has-text('Search')",
                        "button:has-text('Submit')",
                        "button[type='submit']"
                    ]
                },
                wait_times={
                    "page_load": 30000,
                    "element_wait": 15000,
                    "search_wait": 10000,
                    "results_wait": 5000
                },
                credentials={
                    "username": LAN_ID,
                    "password": LAN_PASSWORD
                },
                special_handling={
                    "post_login_wait": 3,
                    "search_verification": True,
                    "results_verification": True
                }
            ),
            
            "Clearance": ApplicationConfig(
                name="Clearance",
                type=ApplicationType.CLEARANCE,
                base_url="https://clearance-qa.express-scripts.com/spclr",
                login_selectors={
                    "username": "input[name='username'], input[id='username'], input[placeholder*='username']",
                    "password": "input[name='password'], input[id='password'], input[type='password']",
                    "login_button": "button[type='submit'], button:has-text('Login'), button:has-text('Sign In')"
                },
                common_selectors={
                    "search_cases": "a:has-text('Search Cases'), [data-test-id*='search'], [data-click*='SearchWorkItems'], [name*='SearchUtilities'], a[href='#']:has-text('Search Cases')",
                    "patient_id": "input[placeholder*='patient'], input[name*='patient'], input[aria-label*='patient'], input[id*='patient']",
                    "search_button": "button:has-text('Search'), button[type='submit'], [data-click*='Search']",
                    "cases_table": "table, .cases-table, [data-testid='cases'], [class*='table']"
                },
                workflow_steps=[
                    {"action": "navigate", "description": "Navigate to Clearance application"},
                    {"action": "login", "description": "Login with credentials"},
                    {"action": "wait", "description": "Wait for page load"},
                    {"action": "click_search_cases", "description": "Click Search Cases button"},
                    {"action": "search_patient", "description": "Search by Patient ID"},
                    {"action": "view_cases", "description": "View case results"}
                ],
                element_patterns={
                    "search_cases_buttons": [
                        "a:has-text('Search Cases')",
                        "[data-test-id*='search']",
                        "[data-click*='SearchWorkItems']",
                        "[name*='SearchUtilities']",
                        "a[href='#']:has-text('Search Cases')",
                        "button:has-text('Search Cases')"
                    ],
                    "patient_inputs": [
                        "input[placeholder*='patient']",
                        "input[name*='patient']",
                        "input[aria-label*='patient']",
                        "input[id*='patient']",
                        "input[data-test-id*='patient']"
                    ]
                },
                wait_times={
                    "page_load": 30000,
                    "element_wait": 15000,
                    "search_cases_wait": 20000,
                    "results_wait": 5000
                },
                credentials={
                    "username": LAN_ID,
                    "password": LAN_PASSWORD
                },
                special_handling={
                    "post_login_wait": 3,
                    "search_cases_verification": True,
                    "pega_specific": True
                }
            ),
            
            "Claims": ApplicationConfig(
                name="Claims",
                type=ApplicationType.CLAIMS,
                base_url="https://claims-qa.express-scripts.com/claims/app/Claims/SVFxeQ1KxRV42HP7Gy_AIT3R1dTRC6gM*/!STANDARD?pzPostData=-123456789",
                login_selectors={
                    "username": "input[name='username'], input[id='username'], input[placeholder*='username']",
                    "password": "input[name='password'], input[id='password'], input[type='password']",
                    "login_button": "button[type='submit'], button:has-text('Login'), button:has-text('Sign In')"
                },
                common_selectors={
                    "search_claims": "button:has-text('Search Claims'), [data-click*='Claims'], [data-test-id*='claims']",
                    "claim_number": "input[placeholder*='claim'], input[name*='claim'], input[aria-label*='claim']",
                    "search_button": "button:has-text('Search'), button[type='submit']",
                    "claims_table": "table, .claims-table, [data-testid='claims']"
                },
                workflow_steps=[
                    {"action": "navigate", "description": "Navigate to Claims application"},
                    {"action": "login", "description": "Login with credentials"},
                    {"action": "wait", "description": "Wait for page load"},
                    {"action": "click_search_claims", "description": "Click Search Claims button"},
                    {"action": "search_claim", "description": "Search by Claim Number"},
                    {"action": "view_claims", "description": "View claim results"}
                ],
                element_patterns={
                    "search_claims_buttons": [
                        "button:has-text('Search Claims')",
                        "[data-click*='Claims']",
                        "[data-test-id*='claims']",
                        "button:has-text('Search')"
                    ],
                    "claim_inputs": [
                        "input[placeholder*='claim']",
                        "input[name*='claim']",
                        "input[aria-label*='claim']",
                        "input[id*='claim']"
                    ]
                },
                wait_times={
                    "page_load": 30000,
                    "element_wait": 15000,
                    "search_claims_wait": 20000,
                    "results_wait": 5000
                },
                credentials={
                    "username": LAN_ID,
                    "password": LAN_PASSWORD
                },
                special_handling={
                    "post_login_wait": 3,
                    "search_claims_verification": True,
                    "pega_specific": True
                }
            ),
            
            "Authorization": ApplicationConfig(
                name="Authorization",
                type=ApplicationType.AUTHORIZATION,
                base_url="https://auth-qa.express-scripts.com/auth/app/Auth/SVFxeQ1KxRV42HP7Gy_AIT3R1dTRC6gM*/!STANDARD?pzPostData=-987654321",
                login_selectors={
                    "username": "input[name='username'], input[id='username'], input[placeholder*='username']",
                    "password": "input[name='password'], input[id='password'], input[type='password']",
                    "login_button": "button[type='submit'], button:has-text('Login'), button:has-text('Sign In')"
                },
                common_selectors={
                    "search_auth": "button:has-text('Search Auth'), [data-click*='Auth'], [data-test-id*='auth']",
                    "auth_number": "input[placeholder*='auth'], input[name*='auth'], input[aria-label*='auth']",
                    "search_button": "button:has-text('Search'), button[type='submit']",
                    "auth_table": "table, .auth-table, [data-testid='auth']"
                },
                workflow_steps=[
                    {"action": "navigate", "description": "Navigate to Authorization application"},
                    {"action": "login", "description": "Login with credentials"},
                    {"action": "wait", "description": "Wait for page load"},
                    {"action": "click_search_auth", "description": "Click Search Auth button"},
                    {"action": "search_auth", "description": "Search by Auth Number"},
                    {"action": "view_auth", "description": "View authorization results"}
                ],
                element_patterns={
                    "search_auth_buttons": [
                        "button:has-text('Search Auth')",
                        "[data-click*='Auth']",
                        "[data-test-id*='auth']",
                        "button:has-text('Search')"
                    ],
                    "auth_inputs": [
                        "input[placeholder*='auth']",
                        "input[name*='auth']",
                        "input[aria-label*='auth']",
                        "input[id*='auth']"
                    ]
                },
                wait_times={
                    "page_load": 30000,
                    "element_wait": 15000,
                    "search_auth_wait": 20000,
                    "results_wait": 5000
                },
                credentials={
                    "username": LAN_ID,
                    "password": LAN_PASSWORD
                },
                special_handling={
                    "post_login_wait": 3,
                    "search_auth_verification": True,
                    "pega_specific": True
                }
            ),
            
            "RxP": ApplicationConfig(
                name="RxP",
                type=ApplicationType.RXP,
                base_url="https://sprxp-qa.express-scripts.com/sprxp/",
                login_selectors={
                    "username": "input[name='username'], input[id='username'], input[placeholder*='username']",
                    "password": "input[name='password'], input[id='password'], input[type='password']",
                    "login_button": "button[type='submit'], button:has-text('Login'), button:has-text('Sign In')"
                },
                common_selectors={
                    "advance_search": "button:has-text('Advance Search'), [data-click*='AdvanceSearch']",
                    "patient_id": "input[name*='patient'], input[placeholder*='patient'], input[aria-label*='patient']",
                    "search_button": "button:has-text('Search'), button[type='submit']",
                    "open_case": "a:has-text('Open Case'), [data-click*='OpenCase']",
                    "referral_contents": "div:has-text('Referral Contents'), [data-testid*='referral']",
                    "begin_button": "button:has-text('Begin'), [data-click*='Begin']",
                    "link_image": "img[alt*='Link'], [data-click*='Link']",
                    "daw_code": "select[name*='daw'], input[name*='daw']",
                    "drug_search": "input[name*='drug'], input[placeholder*='drug']",
                    "common_sig": "select[name*='sig'], input[name*='sig']",
                    "quantity": "input[name*='qty'], input[name*='quantity']",
                    "days_supply": "input[name*='days'], input[name*='supply']",
                    "doses": "input[name*='doses']",
                    "refills": "input[name*='refills']",
                    "apply_rules": "button:has-text('Apply Rules'), [data-click*='ApplyRules']",
                    "reviewed": "button:has-text('Reviewed'), [data-click*='Reviewed']",
                    "patient_checkbox": "input[type='checkbox'][name*='patient']",
                    "medication_checkbox": "input[type='checkbox'][name*='medication']",
                    "rx_details_checkbox": "input[type='checkbox'][name*='rx']",
                    "prescriber_checkbox": "input[type='checkbox'][name*='prescriber']",
                    "next_button": "button:has-text('Next'), [data-click*='Next']",
                    "close_button": "button:has-text('Close'), [data-click*='Close']",
                    "submit_button": "button:has-text('Submit'), [data-click*='Submit']"
                },
                workflow_steps=[
                    {"action": "navigate", "description": "Navigate to RxP application"},
                    {"action": "login", "description": "Login with credentials"},
                    {"action": "wait", "description": "Wait for page load"},
                    {"action": "advance_search", "description": "Click Advance Search"},
                    {"action": "search_patient", "description": "Search by Patient ID"},
                    {"action": "open_case", "description": "Open case for patient"},
                    {"action": "begin_referral", "description": "Begin referral process"},
                    {"action": "link_image", "description": "Click Link image in Viewer"},
                    {"action": "select_daw", "description": "Select DAW code"},
                    {"action": "search_drug", "description": "Search and select drug"},
                    {"action": "select_sig", "description": "Select Common SIG"},
                    {"action": "enter_quantities", "description": "Enter quantities and refills"},
                    {"action": "apply_rules", "description": "Apply rules and review"},
                    {"action": "verify_sections", "description": "Verify and check all sections"},
                    {"action": "submit", "description": "Submit the case"}
                ],
                element_patterns={
                    "search_inputs": [
                        "input[placeholder*='search']",
                        "input[aria-label*='search']",
                        "input[name*='search']"
                    ],
                    "action_buttons": [
                        "button:has-text('Search')",
                        "button:has-text('Submit')",
                        "button[type='submit']"
                    ]
                },
                wait_times={
                    "page_load": 30000,
                    "element_wait": 15000,
                    "search_wait": 10000,
                    "results_wait": 5000
                },
                credentials={
                    "username": LAN_ID,
                    "password": LAN_PASSWORD
                },
                special_handling={
                    "post_login_wait": 3,
                    "search_verification": True,
                    "results_verification": True
                }
            )
        }
    
    def get_application(self, app_name: str) -> Optional[ApplicationConfig]:
        """Get application configuration by name."""
        return self.applications.get(app_name)
    
    def get_all_applications(self) -> List[str]:
        """Get list of all available application names."""
        return list(self.applications.keys())
    
    def detect_application(self, instructions: str) -> Optional[ApplicationConfig]:
        """Detect application from instructions."""
        app_match = re.search(r'Application name:\s*(\w+)', instructions, re.IGNORECASE)
        if app_match:
            app_name = app_match.group(1)
            # Handle multi-application workflows
            if "Multi-Application" in app_name or "Workflow" in app_name:
                # For multi-application workflows, prioritize Intake
                print("🎯 Multi-application workflow detected, prioritizing Intake")
                return self.get_application("Intake")
            return self.get_application(app_name)
        
        # Fallback: Check for specific application URLs in instructions
        if "spcia-qa.express-scripts.com/spcia/app/CIA" in instructions:
            print("🎯 Intake URL detected in instructions")
            return self.get_application("Intake")
        elif "clearance-qa.express-scripts.com" in instructions:
            print("🎯 Clearance URL detected in instructions")
            return self.get_application("Clearance")
        elif "sprxp-qa.express-scripts.com" in instructions:
            print("🎯 RxP URL detected in instructions")
            return self.get_application("RxP")
        
        return None

class ApplicationStepGenerator:
    """Generates application-specific steps based on configuration."""
    
    def __init__(self, app_registry: ApplicationRegistry):
        self.app_registry = app_registry
    
    def generate_steps(self, instructions: str, custom_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Generate steps based on application configuration."""
        app_config = self.app_registry.detect_application(instructions)
        
        if not app_config:
            return self._generate_generic_steps(instructions)
        
        # Extract custom data from instructions
        custom_data = custom_data or {}
        custom_data['instructions'] = instructions  # Pass instructions for Patient ID extraction
        
        url_match = re.search(r'Url\s*->\s*(https?://[^\s]+)', instructions, re.IGNORECASE)
        base_url = url_match.group(1) if url_match else app_config.base_url
        
        # Generate application-specific steps
        if app_config.type == ApplicationType.INTAKE:
            return self._generate_intake_steps(app_config, base_url, custom_data)
        elif app_config.type == ApplicationType.CLEARANCE:
            return self._generate_clearance_steps(app_config, base_url, custom_data)
        elif app_config.type == ApplicationType.CLAIMS:
            return self._generate_claims_steps(app_config, base_url, custom_data)
        elif app_config.type == ApplicationType.AUTHORIZATION:
            return self._generate_authorization_steps(app_config, base_url, custom_data)
        elif app_config.type == ApplicationType.RXP:
            return self._generate_rxp_steps(app_config, base_url, custom_data)
        else:
            return self._generate_generic_steps(instructions)
    
    def _generate_intake_steps(self, app_config: ApplicationConfig, base_url: str, custom_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate Intake application steps."""
        intake_id = custom_data.get('intake_id', 'CMNINTAKE06162025111705988683275')
        
        return [
            {"action": "navigate", "target": base_url, "timeout": app_config.wait_times["page_load"]},
            {"action": "fill", "target": "username", "value": app_config.credentials["username"], "timeout": app_config.wait_times["element_wait"]},
            {"action": "fill", "target": "password", "value": app_config.credentials["password"], "timeout": app_config.wait_times["element_wait"]},
            {"action": "click", "target": "login", "timeout": app_config.wait_times["element_wait"]},
            {"action": "wait", "target": str(app_config.special_handling["post_login_wait"])},
            {"action": "fill", "target": "search", "value": intake_id, "timeout": app_config.wait_times["element_wait"]},
            {"action": "press", "target": "Enter", "timeout": app_config.wait_times["search_wait"]},
            {"action": "wait", "target": "2"}
        ]
    
    def _generate_clearance_steps(self, app_config: ApplicationConfig, base_url: str, custom_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate Clearance application steps with Pega-specific handling."""
        # Extract Patient ID from instructions
        patient_id = "16877147"  # Default fallback
        if 'instructions' in custom_data:
            import re
            # Look for various Patient ID patterns
            patient_patterns = [
                r'Patient ID\s+(\d+)',  # "Patient ID 16984616"
                r'Enter Patient ID\s+(\d+)',  # "Enter Patient ID 16984616"
                r'Patient ID:\s*(\d+)',  # "Patient ID: 16984616"
                r'ID\s+(\d+)\s+in the search field',  # "ID 16984616 in the search field"
            ]
            
            for pattern in patient_patterns:
                patient_match = re.search(pattern, custom_data['instructions'], re.IGNORECASE)
                if patient_match:
                    patient_id = patient_match.group(1)
                    print(f"🔍 Extracted Patient ID from instructions: {patient_id}")
                    break
            else:
                print("⚠️ No Patient ID found in instructions, using default")
        
        print(f"🎯 Using Patient ID: {patient_id}")
        
        # Replace placeholder in instructions with actual Patient ID
        if 'instructions' in custom_data:
            custom_data['instructions'] = custom_data['instructions'].replace('{patient_id}', patient_id)
        
        # Extract case type from instructions (IE-, NR-, CPA-, etc.)
        case_type = "IE-"  # Default
        if 'instructions' in custom_data:
            import re
            case_match = re.search(r'case with ID starting with "([^"]+)"', custom_data['instructions'], re.IGNORECASE)
            if case_match:
                case_type = case_match.group(1)
                print(f"🔍 Extracted case type from instructions: {case_type}")
        
        print(f"🎯 Using case type: {case_type}")
        
        return [
            # Steps 1-5: Login and navigation
            {"action": "navigate", "target": base_url, "timeout": app_config.wait_times["page_load"]},
            {"action": "fill", "target": "username", "value": app_config.credentials["username"], "timeout": app_config.wait_times["element_wait"]},
            {"action": "fill", "target": "password", "value": app_config.credentials["password"], "timeout": app_config.wait_times["element_wait"]},
            {"action": "click", "target": "login", "timeout": app_config.wait_times["element_wait"]},
            {"action": "wait", "target": str(app_config.special_handling["post_login_wait"])},
            
            # Steps 6-8: Search Cases and Patient ID
            {"action": "pega_search_cases", "target": "Search Cases", "timeout": app_config.wait_times["search_cases_wait"]},
            {"action": "wait", "target": "5"},
            {"action": "pega_fill_patient_id", "target": "Patient ID", "value": patient_id, "timeout": app_config.wait_times["element_wait"]},
            {"action": "pega_search_patient", "target": "Search Patient", "timeout": app_config.wait_times["element_wait"]},
            {"action": "wait", "target": "5"},
            
            # Steps 9-10: Select Case (with better targeting)
            {"action": "pega_select_case", "target": f"Case with {case_type}", "value": case_type, "timeout": app_config.wait_times["element_wait"]},
            {"action": "wait", "target": "3"},
            
            # Steps 11-12: Payer Information
            {"action": "pega_dropdown", "target": "Place of Service ID", "value": "12 (Home)", "timeout": app_config.wait_times["element_wait"]},
            {"action": "pega_dropdown", "target": "BIN", "value": "610140", "timeout": app_config.wait_times["element_wait"]},
            {"action": "pega_dropdown", "target": "PCN", "value": "D0TEST", "timeout": app_config.wait_times["element_wait"]},
            {"action": "pega_dropdown", "target": "Group Number", "value": "D0TEST", "timeout": app_config.wait_times["element_wait"]},
            {"action": "click", "target": "Search", "timeout": app_config.wait_times["element_wait"]},
            {"action": "wait", "target": "2"},
            
            # Steps 15-16: Policy Information
            {"action": "pega_dropdown", "target": "Cardholder ID", "value": "555123123", "timeout": app_config.wait_times["element_wait"]},
            {"action": "pega_dropdown", "target": "Person Code", "value": "001", "timeout": app_config.wait_times["element_wait"]},
            {"action": "pega_date", "target": "Insurance Effective Date", "value": "Today", "timeout": app_config.wait_times["element_wait"]},
            {"action": "pega_date", "target": "Insurance Expiration Date", "value": "Tomorrow", "timeout": app_config.wait_times["element_wait"]},
            {"action": "pega_dropdown", "target": "Relationship", "value": "1-Self", "timeout": app_config.wait_times["element_wait"]},
            {"action": "click", "target": "Save", "timeout": app_config.wait_times["element_wait"]},
            {"action": "wait", "target": "2"},
            
            # Steps 17-19: Final steps
            {"action": "click", "target": "Next", "timeout": app_config.wait_times["element_wait"]},
            {"action": "wait", "target": "2"},
            {"action": "click", "target": "Co-Pay", "timeout": app_config.wait_times["element_wait"]},
            {"action": "wait", "target": "2"},
            {"action": "pega_dropdown", "target": "Assign Co-Pay", "value": "P", "timeout": app_config.wait_times["element_wait"]},
            {"action": "click", "target": "Finish", "timeout": app_config.wait_times["element_wait"]},
            {"action": "wait", "target": "3"}
        ]
    
    def _generate_claims_steps(self, app_config: ApplicationConfig, base_url: str, custom_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate Claims application steps."""
        claim_number = custom_data.get('claim_number', 'CLM123456789')
        
        return [
            {"action": "navigate", "target": base_url, "timeout": app_config.wait_times["page_load"]},
            {"action": "fill", "target": "username", "value": app_config.credentials["username"], "timeout": app_config.wait_times["element_wait"]},
            {"action": "fill", "target": "password", "value": app_config.credentials["password"], "timeout": app_config.wait_times["element_wait"]},
            {"action": "click", "target": "login", "timeout": app_config.wait_times["element_wait"]},
            {"action": "wait", "target": str(app_config.special_handling["post_login_wait"])},
            {"action": "click", "target": "Search Claims", "timeout": app_config.wait_times["search_claims_wait"]},
            {"action": "wait", "target": "2"},
            {"action": "fill", "target": "Claim Number", "value": claim_number, "timeout": app_config.wait_times["element_wait"]},
            {"action": "click", "target": "Search", "timeout": app_config.wait_times["element_wait"]},
            {"action": "wait", "target": "2"}
        ]
    
    def _generate_authorization_steps(self, app_config: ApplicationConfig, base_url: str, custom_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate Authorization application steps."""
        auth_number = custom_data.get('auth_number', 'AUTH987654321')
        
        return [
            {"action": "navigate", "target": base_url, "timeout": app_config.wait_times["page_load"]},
            {"action": "fill", "target": "username", "value": app_config.credentials["username"], "timeout": app_config.wait_times["element_wait"]},
            {"action": "fill", "target": "password", "value": app_config.credentials["password"], "timeout": app_config.wait_times["element_wait"]},
            {"action": "click", "target": "login", "timeout": app_config.wait_times["element_wait"]},
            {"action": "wait", "target": str(app_config.special_handling["post_login_wait"])},
            {"action": "click", "target": "Search Auth", "timeout": app_config.wait_times["search_auth_wait"]},
            {"action": "wait", "target": "2"},
            {"action": "fill", "target": "Auth Number", "value": auth_number, "timeout": app_config.wait_times["element_wait"]},
            {"action": "click", "target": "Search", "timeout": app_config.wait_times["element_wait"]},
            {"action": "wait", "target": "2"}
        ]
    
    def _generate_rxp_steps(self, app_config: ApplicationConfig, base_url: str, custom_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate RxP application steps."""
        patient_id = custom_data.get('patient_id', '17037447')
        
        return [
            # Steps 1-5: Login and navigation
            {"action": "navigate", "target": base_url, "timeout": app_config.wait_times["page_load"]},
            {"action": "fill", "target": "username", "value": app_config.credentials["username"], "timeout": app_config.wait_times["element_wait"]},
            {"action": "fill", "target": "password", "value": app_config.credentials["password"], "timeout": app_config.wait_times["element_wait"]},
            {"action": "click", "target": "login", "timeout": app_config.wait_times["element_wait"]},
            {"action": "wait", "target": str(app_config.special_handling["post_login_wait"])},
            
            # Steps 6-8: Advance Search and Patient ID
            {"action": "click", "target": "Advance Search", "timeout": app_config.wait_times["element_wait"]},
            {"action": "fill", "target": "Patient ID", "value": patient_id, "timeout": app_config.wait_times["element_wait"]},
            {"action": "click", "target": "Search", "timeout": app_config.wait_times["element_wait"]},
            {"action": "wait", "target": "3"},
            
            # Steps 9-10: Open Case and Begin
            {"action": "click", "target": "Open Case", "timeout": app_config.wait_times["element_wait"]},
            {"action": "click", "target": "Begin", "timeout": app_config.wait_times["element_wait"]},
            {"action": "wait", "target": "3"},
            
            # Steps 11-12: Link Image and DAW Code
            {"action": "click", "target": "Link image", "timeout": app_config.wait_times["element_wait"]},
            {"action": "select", "target": "DAW code", "value": "0", "timeout": app_config.wait_times["element_wait"]},
            
            # Steps 13-14: Drug Search and Selection
            {"action": "fill", "target": "Drug search", "value": "00074055402", "timeout": app_config.wait_times["element_wait"]},
            {"action": "click", "target": "Search", "timeout": app_config.wait_times["element_wait"]},
            {"action": "wait", "target": "2"},
            {"action": "click", "target": "HUMIRA 40 MG/0.4 ML PEN 2'S", "timeout": app_config.wait_times["element_wait"]},
            
            # Steps 15-16: Common SIG and Quantities
            {"action": "select", "target": "Common SIG", "value": "INJECT 40 MG (0.4 ML) UNDER THE SKIN EVERY 2 WEEKS", "timeout": app_config.wait_times["element_wait"]},
            {"action": "fill", "target": "Qty", "value": "1", "timeout": app_config.wait_times["element_wait"]},
            {"action": "fill", "target": "Days Supply", "value": "14", "timeout": app_config.wait_times["element_wait"]},
            {"action": "fill", "target": "Doses", "value": "1", "timeout": app_config.wait_times["element_wait"]},
            {"action": "fill", "target": "Refills", "value": "1", "timeout": app_config.wait_times["element_wait"]},
            
            # Steps 17-18: Apply Rules and Review
            {"action": "click", "target": "Apply Rules", "timeout": app_config.wait_times["element_wait"]},
            {"action": "click", "target": "Reviewed", "timeout": app_config.wait_times["element_wait"]},
            
            # Steps 19-22: Verify Sections
            {"action": "click", "target": "Patient checkbox", "timeout": app_config.wait_times["element_wait"]},
            {"action": "click", "target": "Medication checkbox", "timeout": app_config.wait_times["element_wait"]},
            {"action": "click", "target": "Rx Details checkbox", "timeout": app_config.wait_times["element_wait"]},
            {"action": "click", "target": "Prescriber checkbox", "timeout": app_config.wait_times["element_wait"]},
            
            # Steps 23-24: Next and Submit
            {"action": "click", "target": "Next", "timeout": app_config.wait_times["element_wait"]},
            {"action": "wait", "target": "5"},
            {"action": "click", "target": "Close", "timeout": app_config.wait_times["element_wait"]},
            {"action": "wait", "target": "120"},  # Wait for Trend Processing
            
            # Steps 25-26: Retrieve and Submit
            {"action": "click", "target": "Begin", "timeout": app_config.wait_times["element_wait"]},
            {"action": "click", "target": "Submit", "timeout": app_config.wait_times["element_wait"]},
            {"action": "wait", "target": "120"}  # Wait for RPh Verification
        ]
    
    def _generate_generic_steps(self, instructions: str) -> List[Dict[str, Any]]:
        """Generate generic steps for unknown applications."""
        url_match = re.search(r'Url\s*->\s*(https?://[^\s]+)', instructions, re.IGNORECASE)
        base_url = url_match.group(1) if url_match else "https://example.com"
        
        return [
            {"action": "navigate", "target": base_url, "timeout": 60000},
            {"action": "fill", "target": "username", "value": LAN_ID, "timeout": 30000},
            {"action": "fill", "target": "password", "value": LAN_PASSWORD, "timeout": 30000},
            {"action": "click", "target": "login", "timeout": 30000},
            {"action": "wait", "target": "3"}
        ]

# Global registry instance
app_registry = ApplicationRegistry()
step_generator = ApplicationStepGenerator(app_registry) 