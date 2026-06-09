import logging
import time
from playwright.sync_api import Page

logger = logging.getLogger(__name__)

class AmazonHomePage:
    def __init__(self, page: Page):
        self.page = page
        self.search_input = page.locator("#twotabsearchtextbox")
        self.search_button = page.locator("#nav-search-submit-button")
        
    def navigate(self):
        """Navigates to Amazon.com, sets a US delivery zip code, and handles initial popups."""
        logger.info("Navigating to Amazon.com")
        self.page.goto("https://www.amazon.com", wait_until="load")
        
        # Check for CAPTCHA
        if "captcha" in self.page.title().lower() or self.page.locator("form[action*='captcha']").is_visible(timeout=2000):
            logger.warning("Amazon CAPTCHA detected! Please solve it or try running in headful mode.")
            raise RuntimeError("CAPTCHA detected on Amazon homepage. Execution blocked.")
            
        # Handle initial dismiss button for address/delivery popups if it blocks the page
        dismiss_btn = self.page.locator("input[data-action-type='DISMISS'], .glow-toaster-button-dismiss").first
        try:
            if dismiss_btn.is_visible(timeout=2000):
                logger.info("Dismissing address pop-up")
                dismiss_btn.click()
        except Exception as e:
            logger.debug(f"Address pop-up not found or could not be dismissed: {e}")

        # Set US delivery location to ensure product availability (especially for items like iPhones/electronics)
        self.set_us_delivery_location("10001")
            
    def set_us_delivery_location(self, zip_code: str = "10001"):
        """
        Sets the Amazon delivery location to a US zip code.
        This ensures add-to-cart buttons and US prices are visible.
        Uses retries and page reload to ensure the modal/overlay is fully dismissed.
        """
        logger.info(f"Setting delivery location to US zip code: {zip_code}")
        try:
            # Click the location selector in the header
            location_btn = self.page.locator("#nav-global-location-popover-link")
            location_btn.wait_for(state="visible", timeout=10000)
            
            # Retry mechanism for opening the location modal
            modal_selector = ".a-popover-wrapper, .a-popover-modal, #a-popover-content-1"
            modal = self.page.locator(modal_selector).first
            
            modal_opened = False
            for attempt in range(3):
                logger.info(f"Clicking location popover button (attempt {attempt + 1})")
                location_btn.click()
                try:
                    modal.wait_for(state="visible", timeout=3000)
                    modal_opened = True
                    break
                except Exception:
                    logger.warning("Popover modal did not open, retrying click...")
                    continue
            
            if not modal_opened:
                raise RuntimeError("Location popover modal failed to open after 3 attempts.")
            
            # Wait for the zip input field to be visible in the popover
            zip_input = self.page.locator("#GLUXZipUpdateInput, [data-action='GLUXPostalInputAction'], [aria-label='or enter a US zip code']").first
            zip_input.wait_for(state="visible", timeout=5000)
            
            # Fill the zip code
            zip_input.fill(zip_code)
            
            # Click the 'Apply' button
            apply_btn = self.page.locator("input[aria-labelledby='GLUXZipUpdate-announce'], #GLUXZipUpdate").first
            apply_btn.click()
            
            # Wait for and click 'Done' / 'Continue' button if it appears
            done_btn = self.page.locator("input[name='glowDoneButton'], #GLUXConfirmClose, button:has-text('Done'), .a-popover-footer #GLUXConfirmClose").first
            try:
                if done_btn.is_visible(timeout=3000):
                    logger.info("Clicking the confirmation Done button")
                    done_btn.click()
            except Exception:
                pass
                
            # Reload page to apply changes and clear the overlay/modal backdrop
            logger.info("Reloading page to apply location change and clear modal overlays")
            self.page.reload(wait_until="load")
            time.sleep(2)
            logger.info("US delivery location applied successfully")
        except Exception as e:
            logger.warning(f"Could not change delivery location to US zip code: {e}. Proceeding with default location.")
            try:
                self.page.reload()
            except Exception:
                pass
            
    def search_product(self, product_name: str):
        """Enters product_name in the search bar and clicks the search button."""
        logger.info(f"Searching for product: {product_name}")
        self.search_input.wait_for(state="visible", timeout=10000)
        self.search_input.fill(product_name)
        self.search_button.click()
        self.page.wait_for_load_state("domcontentloaded")
