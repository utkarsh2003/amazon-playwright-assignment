import logging
from playwright.sync_api import Page

logger = logging.getLogger(__name__)

class SearchResultsPage:
    def __init__(self, page: Page):
        self.page = page
        # Locator matching search result items on Amazon search results page
        self.result_items = page.locator('[data-component-type="s-search-result"]')
        
    def click_first_product(self, required_keyword: str | None = None):
        """Clicks the first visible product result that has a title and price."""
        logger.info("Selecting the first priced product from search results")
        
        # Wait until at least one search result item is visible
        self.result_items.first.wait_for(state="visible", timeout=15000)
        
        selected_item = None
        item_count = min(self.result_items.count(), 10)

        for index in range(item_count):
            item = self.result_items.nth(index)
            product_link = item.locator(
                'h2 a[href*="/dp/"], '
                'h2 a[href*="/gp/product/"], '
                'a[href*="/dp/"]:has(h2), '
                'a[href*="/gp/product/"]:has(h2)'
            ).first
            price = item.locator(".a-price .a-offscreen").first

            try:
                if not (
                    item.is_visible(timeout=1000)
                    and product_link.is_visible(timeout=1000)
                    and price.is_visible(timeout=1000)
                ):
                    continue

                product_title = product_link.inner_text().strip()
                if required_keyword and required_keyword.lower() not in product_title.lower():
                    logger.info(f"Skipping non-matching result title: '{product_title}'")
                    continue

                if product_title:
                    selected_item = item
                    selected_link = product_link
                    selected_title = product_title
                    break
            except Exception:
                continue

        if selected_item is None:
            raise RuntimeError("No visible matching priced product was found in the first 10 search results.")

        logger.info(f"Selected product title: '{selected_title}'")
        
        logger.info("Clicking on the product link")
        selected_link.click()
        self.page.wait_for_load_state("domcontentloaded")
