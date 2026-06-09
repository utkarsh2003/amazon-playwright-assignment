import os
import urllib.parse
import json
import pytest
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture test execution results (passed/failed) 
    so they can be reported back to LambdaTest.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

@pytest.fixture(scope="function")
def page(request):
    """
    Fixture that provides an initialized Playwright Page object.
    Supports local Chrome/Chromium execution and remote LambdaTest execution.
    """
    run_on_lt = os.getenv("RUN_ON_LT", "false").lower() == "true"
    
    if run_on_lt:
        username = os.getenv("LT_USERNAME")
        access_key = os.getenv("LT_ACCESS_KEY")
        
        if not username or not access_key:
            pytest.fail("LT_USERNAME and LT_ACCESS_KEY environment variables must be set in .env when RUN_ON_LT=true")
        
        capabilities = {
            "browserName": "pw-chromium",  
            "browserVersion": "latest",
            "LT:Options": {
                "platform": "Windows 10",
                "build": "Amazon Playwright Pytest Build",
                "name": f"{request.node.name}",
                "user": username,
                "accessKey": access_key,
                "network": True,      
                "video": True,        
                "console": True,      
                "w3c": True
            }
        }
        
        cap_str = urllib.parse.quote(json.dumps(capabilities))
        ws_endpoint = f"wss://cdp.lambdatest.com/playwright?capabilities={cap_str}"
        
        print(f"\n[LambdaTest] Connecting to remote grid for test: {request.node.name}")
        
        with sync_playwright() as p:
            browser = p.chromium.connect(ws_endpoint)
            context = browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            yield page
            
            rep_call = getattr(request.node, "rep_call", None)
            status = "passed"
            remark = "Test passed successfully"
            
            if rep_call:
                if rep_call.failed:
                    status = "failed"
                    remark = f"Test failed: {rep_call.longreprtext}"
                elif rep_call.skipped:
                    status = "skipped"
                    remark = "Test skipped"
            
            try:
                page.evaluate("_ => {}", f"lambda-status={status}")
                print(f"[LambdaTest] Status set to: {status}")
            except Exception as e:
                print(f"[LambdaTest] Failed to report status: {e}")
                
            page.close()
            context.close()
            browser.close()
            
    else:
        headless = os.getenv("HEADLESS", "false").lower() == "true"
        print(f"\n[Local] Launching local Chromium (headless={headless}) for test: {request.node.name}")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-infobars"
                ]
            )
            context = browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale="en-US"
            )
            context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            page = context.new_page()
            
            yield page
            
            page.close()
            context.close()
            browser.close()
