from playwright.sync_api import Page

def set_test_status(page: Page, status: str, remark: str = None):
    """
    Sets the test execution status (passed/failed) on the LambdaTest dashboard.
    
    Args:
        page (Page): The Playwright page object.
        status (str): "passed" or "failed".
        remark (str, optional): A description or reason for failure. Defaults to None.
    """
    try:
        page.evaluate("_ => {}", f"lambda-status={status}")
        
        if remark:
            print(f"LambdaTest Status: {status} - Remark: {remark}")
    except Exception as e:
        print(f"Failed to set LambdaTest status: {e}")
