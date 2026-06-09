import logging
import time
from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)

class ProductPage:
    def __init__(self, page: Page):
        self.page = page
        
        self.add_to_cart_button = page.locator("#add-to-cart-button").first
        
        
        self.price_selectors = [
            "#corePrice_desktop .a-price .a-offscreen",
            "#corePriceDisplay_desktop_feature_div .a-price .a-offscreen",
            "#corePrice_feature_div .a-price .a-offscreen",
            "#price_inside_buybox",
            "#priceblock_ourprice",
            "#priceblock_dealprice",
            ".a-price .a-offscreen",
            ".a-color-price"
        ]

    def get_price(self) -> str:
        """
        Attempts to locate and extract the price of the product from the page.
        Returns the formatted price string (e.g. '$999.00').
        """
        logger.info("Attempting to retrieve product price")
        
       
        self.page.wait_for_load_state("domcontentloaded")

        time.sleep(1)  
        for selector in self.price_selectors:
            locator = self.page.locator(selector).first
            try:
                if locator.is_visible(timeout=1500):
                    price_text = locator.inner_text().strip()
                    if price_text:
                       
                        cleaned_price = price_text.replace("\n", "").strip()
                        logger.info(f"Price found with selector '{selector}': {cleaned_price}")
                        return cleaned_price
            except Exception:
                continue

        
        try:
            whole_locator = self.page.locator(".a-price-whole").first
            fraction_locator = self.page.locator(".a-price-fraction").first
            if whole_locator.is_visible(timeout=1000):
                whole_text = whole_locator.inner_text().replace("\n", "").strip()
                fraction_text = fraction_locator.inner_text().strip() if fraction_locator.is_visible() else "00"
                
                whole_text = whole_text.rstrip('.').rstrip(',')
                assembled_price = f"${whole_text}.{fraction_text}"
                logger.info(f"Price assembled from components: {assembled_price}")
                return assembled_price
        except Exception as e:
            logger.debug(f"Failed fallback price retrieval: {e}")

        
        logger.warning("Could not retrieve price from standard selectors.")
        return "Price not found"

    def add_to_cart(self):
        """
        Clicks the 'Add to Cart' button and handles any upsell,
        warranty, or protection plan popups. Raises if Amazon does not show
        an add-to-cart confirmation.
        """
        logger.info("Adding product to cart")
        self.click_add_to_cart_button()

        no_thanks_btn = self.page.locator(
            "#attachSiNoCoverage, #attachSiNoCoverage-announce, [aria-labelledby='attachSiNoCoverage-announce'], #abb-intl-decl-btn"
        ).first
        
        try:
            if no_thanks_btn.is_visible(timeout=3000):
                logger.info("Decline warranty/protection popup clicked")
                no_thanks_btn.click()
        except Exception as e:
            logger.debug(f"No warranty popup displayed or could not click: {e}")

        close_sheet_btn = self.page.locator("#attach-close_button").first
        try:
            if close_sheet_btn.is_visible(timeout=2000):
                logger.info("Closing attach sheet panel")
                close_sheet_btn.click()
        except Exception as e:
            logger.debug(f"Attach sheet close button not found or not clicked: {e}")
            
        confirmation = self.page.locator(
            "#attachDisplayAddBaseAlert, "
            "#attach-added-to-cart-alert-and-image-area, "
            "#NATC_SMART_WAGON_CONF_MSG_SUCCESS, "
            "h1:has-text('Added to Cart')"
        ).first

        try:
            expect(confirmation).to_be_visible(timeout=10000)
        except Exception:
            try:
                expect(self.page.get_by_text("Added to Cart").first).to_be_visible(timeout=3000)
            except Exception:
                cart_count = self.page.locator("#nav-cart-count").first
                expect(cart_count).not_to_have_text("0", timeout=5000)

        time.sleep(1)
        logger.info("Product added to cart and confirmation verified")

    def click_add_to_cart_button(self):
        self.ensure_us_delivery_location_if_needed()

        direct_add_to_cart = self.page.locator(
            "#add-to-cart-button, "
            "input[name='submit.add-to-cart'], "
            "input[aria-labelledby='submit.add-to-cart-announce']"
        ).first

        try:
            if direct_add_to_cart.is_visible(timeout=8000):
                direct_add_to_cart.click()
                return
        except Exception:
            logger.info("Direct Add to Cart button not visible; checking buying options")

        buying_options = self.first_visible_locator([
            "#buybox-see-all-buying-choices input",
            "#buybox-see-all-buying-choices",
            "#aod-ingress-link",
            "#olpLinkWidget_feature_div a",
            "text=/See All Buying Options/i",
        ], timeout=5000)

        if buying_options:
            buying_options.click()
            offer_add_to_cart = self.page.locator(
                "#aod-offer input[name='submit.addToCart'], "
                "#aod-offer input[aria-label*='Add to Cart'], "
                "#aod-offer button:has-text('Add to Cart'), "
                "input[name='submit.addToCart']"
            ).first
            offer_add_to_cart.wait_for(state="visible", timeout=10000)
            offer_add_to_cart.click()
            return

        raise RuntimeError("No Add to Cart or buying-options Add to Cart control was visible.")

    def ensure_us_delivery_location_if_needed(self, zip_code: str = "10001"):
        blocked_location = self.page.get_by_text("cannot be shipped to your selected delivery location").first

        try:
            if not blocked_location.is_visible(timeout=2000):
                return
        except Exception:
            return

        logger.info(f"Product is blocked by delivery location; setting US ZIP code {zip_code}")
        location_trigger = self.first_visible_locator([
            "#nav-global-location-popover-link",
            "#contextualIngressPtLink",
        ], timeout=3000)

        if not location_trigger:
            logger.warning("Delivery location trigger was not visible")
            return

        location_trigger.click()

        zip_input = self.page.locator(
            "#GLUXZipUpdateInput, "
            "input[aria-label*='zip'], "
            "input[aria-label*='ZIP'], "
            "input[placeholder*='zip'], "
            "input[placeholder*='ZIP']"
        ).first
        zip_input.wait_for(state="visible", timeout=10000)
        zip_input.fill(zip_code)

        apply_button = self.page.locator(
            "input[aria-labelledby='GLUXZipUpdate-announce'], "
            "#GLUXZipUpdate, "
            "span:has-text('Apply') input"
        ).first
        apply_button.click()

        done_button = self.first_visible_locator([
            "input[name='glowDoneButton']",
            "#GLUXConfirmClose",
            "button:has-text('Done')",
        ], timeout=5000)

        if done_button:
            done_button.click()

        self.page.reload(wait_until="domcontentloaded")
        time.sleep(2)

    def first_visible_locator(self, selectors: list[str], timeout: int = 1000):
        for selector in selectors:
            locator = self.page.locator(selector).first
            try:
                if locator.is_visible(timeout=timeout):
                    return locator
            except Exception:
                continue
        return None
