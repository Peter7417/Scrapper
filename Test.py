from flask import Flask, request, render_template
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

app = Flask(__name__)

# Keywords
IN_STOCK_KEYWORDS = ["in stock", "available", "add to cart"]
OUT_OF_STOCK_KEYWORDS = ["out of stock", "sold out", "unavailable", "sold", "notify me when available"]
EXCLUDE_KEYWORDS = ["reddit", "quora", "forum", "blog", "youtube", "pinterest"]

def extract_price(text):
    price_patterns = [
        r"£\s?\d{1,4}(?:\.\d{2})?",
        r"\$\s?\d{1,4}(?:\.\d{2})?",
        r"€\s?\d{1,4}(?:\.\d{2})?",
        r"Price[:\s]*[£$€]?\s?\d{1,4}(?:\.\d{2})?",
        r"Only[:\s]*[£$€]?\s?\d{1,4}(?:\.\d{2})?",
        r"Now[:\s]*[£$€]?\s?\d{1,4}(?:\.\d{2})?"
    ]
    for pattern in price_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group()
    return None

def check_stock(query):
    options = Options()
    #options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")  # Suppress non-fatal logs
    options.add_experimental_option("excludeSwitches", ["enable-logging"])  # Suppress GCM logs

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    results_html = f"<h2>Showing IN STOCK results for: {query}</h2><ul>"

    try:
        # Step 1: Go to Bing and search
        driver.get("https://www.bing.com")
        try:
            cookie_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "bnp_btn_accept"))
            )
            cookie_button.click()
        except:
            pass

        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        full_query = f"{query} UK/Europe English"
        search_box.send_keys(full_query + Keys.ENTER)

        time.sleep(2)
        results = driver.find_elements(By.CSS_SELECTOR, "li.b_algo a")[:10]
        print(f"Found {len(results)} search results")

        # Step 2: Loop through results and show only IN STOCK
        for i, result in enumerate(results):
            url = result.get_attribute("href")
            if any(bad in url.lower() for bad in EXCLUDE_KEYWORDS):
                continue

            driver.execute_script("window.open(arguments[0]);", url)
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(3)

            page_text = driver.page_source.lower()
            in_stock_found = any(keyword in page_text for keyword in IN_STOCK_KEYWORDS)
            out_of_stock_found = any(keyword in page_text for keyword in OUT_OF_STOCK_KEYWORDS)

            # Show only if IN STOCK and not OUT OF STOCK
            if in_stock_found and not out_of_stock_found:
                stock_status = "<span style='color:green;'>✅ IN STOCK</span>"
                price = extract_price(page_text)
                price_info = f"<strong>💰 Price:</strong> {price}" if price else "💸 Price not found"
                results_html += f"<li><a href='{url}' target='_blank'>{url}</a><br>{stock_status}<br>{price_info}</li><br>"

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    except Exception as e:
        results_html += f"<li style='color:red;'>Error: {e}</li>"
    finally:
        driver.quit()

    results_html += "</ul>"
    return results_html

@app.route("/", methods=["GET", "POST"])
def home():
    result = ""
    if request.method == "POST":
        query = request.form["query"]
        result = check_stock(query)
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
