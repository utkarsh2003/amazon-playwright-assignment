import logging
import time
from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)

class ProductPage:
    def __init__(self, page: Page):
        self.page = page
        # Using .first to avoid strict mode violations when Amazon renders multiple Buy Boxes/Accordions
        self.add_to_cart_button = page.locator("#add-to-cart-button").first
        
        # Various potential price selectors on Amazon product page
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
        
        # Let's wait a bit to make sure the price element is rendered
        self.page.wait_for_load_state("domcontentloaded")
        
        # Try each selector one by one
        for selector in self.price_selectors:
            locator = self.page.locator(selector).first
            try:
                if locator.is_visible(timeout=1500):
                    price_text = locator.inner_text().strip()
                    if price_text:
                        # Clean up any potential newline characters
                        cleaned_price = price_text.replace("\n", "").strip()
                        logger.info(f"Price found with selector '{selector}': {cleaned_price}")
                        return cleaned_price
            except Exception:
                continue

        # Fallback: Check if we can assemble it from whole and fraction components
        try:
            whole_locator = self.page.locator(".a-price-whole").first
            fraction_locator = self.page.locator(".a-price-fraction").first
            if whole_locator.is_visible(timeout=1000):
                whole_text = whole_locator.inner_text().replace("\n", "").strip()
                fraction_text = fraction_locator.inner_text().strip() if fraction_locator.is_visible() else "00"
                # Remove trailing dots/commas
                whole_text = whole_text.rstrip('.').rstrip(',')
                assembled_price = f"${whole_text}.{fraction_text}"
                logger.info(f"Price assembled from components: {assembled_price}")
                return assembled_price
        except Exception as e:
            logger.debug(f"Failed fallback price retrieval: {e}")

        # Final fallback: Look for buy box or offer price elements
        logger.warning("Could not retrieve price from standard selectors.")
        return "Price not found"

    def add_to_cart(self):
        """
        Clicks the 'Add to Cart' button and handles any upsell,
        warranty, or protection plan popups. Raises if Amazon does not show
        an add-to-cart confirmation.
        """
        logger.info("Adding product to cart")
        self.add_to_cart_button.wait_for(state="visible", timeout=10000)
        self.add_to_cart_button.click()
        
        # Let's handle warranty / coverage / protection plan popups if they appear
        no_thanks_btn = self.page.locator(
            "#attachSiNoCoverage, #attachSiNoCoverage-announce, [aria-labelledby='attachSiNoCoverage-announce'], #abb-intl-decl-btn"
        ).first
        
        try:
            if no_thanks_btn.is_visible(timeout=3000):
                logger.info("Decline warranty/protection popup clicked")
                no_thanks_btn.click()
        except Exception as e:
            logger.debug(f"No warranty popup displayed or could not click: {e}")

        # Also wait for slideout panels / sheets to close, or check if we are on confirmation page
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
            "h1:has-text('Added to Cart'), "
            "text=/Added to Cart/i"
        ).first

        try:
            expect(confirmation).to_be_visible(timeout=10000)
        except Exception:
            cart_count = self.page.locator("#nav-cart-count").first
            expect(cart_count).not_to_have_text("0", timeout=5000)

        time.sleep(1)
        logger.info("Product added to cart and confirmation verified")
