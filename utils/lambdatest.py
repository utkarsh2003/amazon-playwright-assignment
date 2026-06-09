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
        # Send status
        page.evaluate("_ => {}", f"lambda-status={status}")
        
        # If there is a remark, we can send it as a log/comment or description
        if remark:
            # LambdaTest allows updating status remark or name using JSON executor or simple strings
            # Wait, lambda-name is used for setting test name, lambda-status is for status
            # Let's write the remark to console/log
            print(f"LambdaTest Status: {status} - Remark: {remark}")
    except Exception as e:
        print(f"Failed to set LambdaTest status: {e}")
