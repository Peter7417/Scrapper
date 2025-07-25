from bs4 import BeautifulSoup
import tkinter as tk
import webbrowser
import threading
import speech_recognition as sr
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

# Get product price
def extract_price(text):
    # Look for common currency formats
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


# Keywords to check stock status
IN_STOCK_KEYWORDS = ["in stock", "available", "add to cart", "buy it now", "unsold", "buy now", "Add to Basket"]
OUT_OF_STOCK_KEYWORDS = ["ended","out of stock", "sold out", "unavailable", "notify me when available"]
EXCLUDE_KEYWORDS = ["reddit", "quora", "forum", "blog", "youtube", "pinterest", "zhidao.baidu", "playblackdessert"]

# Capture voice input
def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        status_label.config(text="🎙️ Listening...", fg="blue")
        audio = recognizer.listen(source)
    try:
        query = recognizer.recognize_google(audio)
        status_label.config(text=f"🗣️ You said: {query}", fg="green")
        return query
    except sr.UnknownValueError:
        status_label.config(text="❌ Could not understand audio.", fg="red")
    except sr.RequestError:
        status_label.config(text="❌ Speech recognition failed.", fg="red")
    return None

# Open link in browser
def open_link(event):
    widget = event.widget
    index = widget.index("@%s,%s" % (event.x, event.y))
    tag_names = widget.tag_names(index)
    for tag in tag_names:
        if tag.startswith("link-"):
            url = tag.split("link-")[1]
            webbrowser.open_new(url)
# Normalize and extract text from HTML
def preprocess_html(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ").lower()
    return text, soup

# Regex-based keyword detection
def keyword_found(text, keywords):
    for keyword in keywords:
        pattern = re.compile(r"\b" + re.escape(keyword) + r"\b", re.IGNORECASE)
        if pattern.search(text):
            return True
    return False

# Count keyword matches
def keyword_count(text, keywords):
    count = 0
    for keyword in keywords:
        count += len(re.findall(r"\b" + re.escape(keyword) + r"\b", text, re.IGNORECASE))
    return count

# Scan specific HTML elements for keywords
def scan_elements_for_keywords(soup, keywords):
    elements = soup.find_all(["button", "h1", "h2", "h3", "span", "div"])
    for el in elements:
        text = el.get_text().lower()
        if any(kw in text for kw in keywords):
            return True
    return False

# Main stock checking function
def check_stock(query, text_widget, status_label):
    global stop_search
    stop_search = False

    status_label.config(text="🔄 Searching...", fg="blue")

    options = Options()
    # options.add_argument("--headless")  # Uncomment for headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
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

        # Scroll to bottom to load more results
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Collect up to 20 results across pages
        all_results = []
        visited_urls = set()

        while len(all_results) < 20:
            links = driver.find_elements(By.CSS_SELECTOR, "li.b_algo h2 a")
            for link in links:
                url = link.get_attribute("href")
                if url and url not in visited_urls and not any(bad in url.lower() for bad in EXCLUDE_KEYWORDS):
                    all_results.append(link)
                    visited_urls.add(url)
                    if len(all_results) >= 20:
                        break

            # Try to go to next page
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "a.sb_pagN")
                next_button.click()
                time.sleep(2)
            except:
                break  # No more pages

        text_widget.insert(tk.END, f"\n🔍 Searching for: {query}\n\n")

        for i, result in enumerate(all_results):
            if stop_search:
                text_widget.insert(tk.END, "\n🛑 Search stopped by user.\n", "red")
                status_label.config(text="🛑 Search stopped.", fg="red")
                break

            url = result.get_attribute("href")
            tag_name = f"link-{url}"
            text_widget.insert(tk.END, f"🔗 Site {i+1}: ", "bold")
            text_widget.insert(tk.END, f"{url}\n", tag_name)
            text_widget.tag_config(tag_name, foreground="blue", underline=True)
            text_widget.tag_bind(tag_name, "<Button-1>", open_link)

            driver.execute_script("window.open(arguments[0]);", url)
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(3)

            raw_html = driver.page_source
            page_text, soup = preprocess_html(raw_html)

            # Keyword scoring
            in_stock_score = keyword_count(page_text, IN_STOCK_KEYWORDS)
            out_of_stock_score = keyword_count(page_text, OUT_OF_STOCK_KEYWORDS)

            # Element scanning
            in_stock_elements = scan_elements_for_keywords(soup, IN_STOCK_KEYWORDS)
            out_of_stock_elements = scan_elements_for_keywords(soup, OUT_OF_STOCK_KEYWORDS)

            # Final decision logic
            if (out_of_stock_score > 0 and out_of_stock_score >= in_stock_score) or out_of_stock_elements:
                text_widget.insert(tk.END, "❌ Product appears to be OUT OF STOCK.\n", "red")
            elif in_stock_score > 0 or in_stock_elements:
                text_widget.insert(tk.END, "✅ Product appears to be IN STOCK.\n", "green")
            else:
                text_widget.insert(tk.END, "⚠️ Stock status unclear.\n", "orange")

            price = extract_price(page_text)
            if price:
                text_widget.insert(tk.END, f"💰 Price found: {price}\n", "bold")
            else:
                text_widget.insert(tk.END, "💸 Price not found.\n", "orange")

            text_widget.insert(tk.END, "\n")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        if not stop_search:
            status_label.config(text="✅ Search complete!", fg="green")

    except Exception as e:
        text_widget.insert(tk.END, f"\n❌ Error: {e}\n", "red")
        status_label.config(text="❌ Error occurred", fg="red")
    finally:
        driver.quit()


# GUI setup
def start_gui():
    global status_label  # Needed for voice input feedback

    window = tk.Tk()
    window.title("Product Stock Checker")
    window.geometry("800x620")

    # Input row: Entry + Buttons
    input_frame = tk.Frame(window)
    input_frame.pack(pady=10)

    query_entry = tk.Entry(input_frame, width=50)
    query_entry.pack(side=tk.LEFT, padx=5)

    tk.Button(input_frame, text="Search (Text)", command=lambda: on_text_search(query_entry)).pack(side=tk.LEFT, padx=5)
    # tk.Button(input_frame, text="Search (Voice)", command=on_voice_search).pack(side=tk.LEFT)

    # Status label
    status_label = tk.Label(window, text="", font=("Helvetica", 10))
    status_label.pack(pady=5)

    # Results area
    frame = tk.Frame(window)
    frame.pack(pady=10, fill=tk.BOTH, expand=True)

    text_widget = tk.Text(frame, wrap=tk.WORD)
    scrollbar = tk.Scrollbar(frame, command=text_widget.yview)
    text_widget.configure(yscrollcommand=scrollbar.set)
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Text styles
    text_widget.tag_config("green", foreground="green")
    text_widget.tag_config("red", foreground="red")
    text_widget.tag_config("orange", foreground="orange")
    text_widget.tag_config("bold", font=("Helvetica", 10, "bold"))

    # define a stop to the GUI
    def stop_searching():
        global stop_search
        stop_search = True

    tk.Button(input_frame, text="Stop Search", command=stop_searching).pack(side=tk.LEFT, padx=5)

    # Search functions
    def on_text_search(entry):
        query = entry.get()
        text_widget.delete(1.0, tk.END)
        threading.Thread(target=check_stock, args=(query, text_widget, status_label)).start()

    def on_voice_search():
        text_widget.delete(1.0, tk.END)

        def run_voice_search():
            query = get_voice_input()
            if query:
                check_stock(query, text_widget, status_label)
            else:
                text_widget.insert(tk.END, "❌ No voice input detected.\n", "red")

        threading.Thread(target=run_voice_search).start()

    window.mainloop()

# Launch GUI
start_gui()