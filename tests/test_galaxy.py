from pages.amazon_home_page import AmazonHomePage
from pages.search_results_page import SearchResultsPage
from pages.product_page import ProductPage

def test_search_and_add_galaxy(page):
    """
    Test Case 2:
    1. Navigate to Amazon.com.
    2. Search for 'Galaxy'.
    3. Add the selected Galaxy device to the shopping cart.
    4. Retrieve and print the price of the device to the console.
    """
    home_page = AmazonHomePage(page)
    search_results = SearchResultsPage(page)
    product_page = ProductPage(page)
    
    try:
        # 1. Navigate to Amazon.com
        home_page.navigate()
        
        # 2. Search for 'Galaxy'
        home_page.search_product("Samsung Galaxy unlocked")
        
        # 3. Select the first search result product
        search_results.click_first_product(required_keyword="Galaxy")
        
        # 4. Retrieve and print the price of the device to the console
        price = product_page.get_price()
        assert price != "Price not found", "Unable to retrieve the selected Galaxy price"
        print(f"\n==================================================")
        print(f"  VERIFICATION: Selected Galaxy Price is: {price}")
        print(f"==================================================\n")
        
        # 5. Add the selected Galaxy device to the shopping cart
        product_page.add_to_cart()
    except Exception as e:
        page.screenshot(path="galaxy_failure.png")
        # Let's save HTML as well to analyze
        with open("galaxy_failure.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        raise e
