import httpx
import dotenv

dotenv.load_dotenv()

def get_azure_llm(model_name: str, api_version: str = '2024-10-21', **kwargs):
    from langchain_openai.chat_models import AzureChatOpenAI
    from dotenv import load_dotenv
    load_dotenv()
    return AzureChatOpenAI(
            azure_deployment=model_name,
            api_version=api_version,
            http_client= httpx.Client(verify = False),
            **kwargs
        )

if __name__ == "__main__":
    llm = get_azure_llm("ai-coe-gpt41")
    print(llm.invoke("""
    
can you give a combined playwright step. Don't give browser load methods. start with  
def step(page):
    step one code.
    step two code.

    start with this code.
    Login to Clearance:
"playwright_script": "from playwright.async_api import async_playwright\\\\n\\\\nasync def test_clearance_login(page, username, password):\\\\n \\\\\\\"\\\\\\\"\\\\\\\"\\\\n Logs into the Clearance QA Portal using provided credentials.\\\\n Args:\\\\n page: Playwright page object\\\\n username (str): Login user name (LanID)\\\\n password (str): Login password (already decrypted)\\\\n \\\\\\\"\\\\\\\"\\\\\\\"\\\\n # Define selectors as per ClearanceCaseManagerHomePage\\\\n USERNAME_SELECTOR = '[name=\\\\\\\"UserIdentifier\\\\"

Click on Search cases:
"playwright_script": "from playwright.async_api import async_playwright\\\\n\\\\nasync def test_step(page):\\\\n try:\\\\n # Switch to the 4th window/tab (Python 0-based index)\\\\n all_pages = page.context.pages\\\\n if len(all_pages) < 4:\\\\n # Wait until the target window appears (8s max)\\\\n for _ in range(8):\\\\n all_pages = page.context.pages\\\\n if len(all_pages) >= 4:\\\\n break\\\\n await page.wait_for_timeout(1000)\\\\n if len(all_pages) < 4:\\\\n raise Exception('Unable to find the 4th browser window for Clearance Case Manager')\\\\n target_page = all_pages[3] # Index 3 for the 4th window\\\\n\\\\n # Selector for Search Cases button (from @FindBy(name = \\\\\\\"SearchUtilities_pyDisplayHarness_5\\\\\\\"))\\\\n search_cases_selector = '[name=\\\\\\\"SearchUtilities_pyDisplayHarness_5\\\\"             
"""))