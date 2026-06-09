from pages.amazon_home_page import AmazonHomePage
from pages.search_results_page import SearchResultsPage
from pages.product_page import ProductPage

def test_search_and_add_iphone(page):
    """
    Test Case 1:
    1. Navigate to Amazon.com.
    2. Search for 'iPhone'.
    3. Add the selected iPhone to the shopping cart.
    4. Retrieve and print the price of the device to the console.
    """
    home_page = AmazonHomePage(page)
    search_results = SearchResultsPage(page)
    product_page = ProductPage(page)
    
    try:
        # 1. Navigate to Amazon.com
        home_page.navigate()
        
        # 2. Search for 'iPhone'
        home_page.search_product("iPhone unlocked")
        
        # 3. Select the first search result product
        search_results.click_first_product(required_keyword="iPhone")
        
        # 4. Retrieve and print the price of the device to the console
        price = product_page.get_price()
        assert price != "Price not found", "Unable to retrieve the selected iPhone price"
        print(f"\n==================================================")
        print(f"  VERIFICATION: Selected iPhone Price is: {price}")
        print(f"==================================================\n")
        
        # 5. Add the selected iPhone to the shopping cart
        product_page.add_to_cart()
    except Exception as e:
        page.screenshot(path="iphone_failure.png")
        # Let's save HTML as well to analyze
        with open("iphone_failure.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        raise e
