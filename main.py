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
IN_STOCK_KEYWORDS = ["in stock", "available", "add to cart"]
OUT_OF_STOCK_KEYWORDS = ["out of stock", "sold out", "unavailable", "sold", "notify me when available"]
EXCLUDE_KEYWORDS = ["reddit", "quora", "forum", "blog", "youtube", "pinterest"]

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

# Perform search and check stock
def check_stock(query, text_widget, status_label):
    status_label.config(text="🔄 Searching...", fg="blue")

    options = Options()
    options.add_argument("--headless")
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
        results = driver.find_elements(By.CSS_SELECTOR, "li.b_algo h2 a")[:20]

        text_widget.insert(tk.END, f"\n🔍 Searching for: {query}\n\n")

        for i, result in enumerate(results):
            url = result.get_attribute("href")
            if any(bad in url.lower() for bad in EXCLUDE_KEYWORDS):
                continue

            tag_name = f"link-{url}"
            text_widget.insert(tk.END, f"🔗 Site {i+1}: ", "bold")
            text_widget.insert(tk.END, f"{url}\n", tag_name)
            text_widget.tag_config(tag_name, foreground="blue", underline=True)
            text_widget.tag_bind(tag_name, "<Button-1>", open_link)

            driver.execute_script("window.open(arguments[0]);", url)
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(3)

            page_text = driver.page_source.lower()
            # Stock status (prioritize OUT OF STOCK if both are present)
            in_stock_found = any(keyword in page_text for keyword in IN_STOCK_KEYWORDS)
            out_of_stock_found = any(keyword in page_text for keyword in OUT_OF_STOCK_KEYWORDS)

            if out_of_stock_found:
                text_widget.insert(tk.END, "❌ Product appears to be OUT OF STOCK.\n", "red")
            elif in_stock_found:
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

        status_label.config(text="✅ Search complete!", fg="green")


    except Exception as e:
        text_widget.insert(tk.END, f"\n❌ Error: {e}\n", "red")
        status_label.config(text="❌ Error occurred", fg="red")
    finally:
        driver.quit()



# Get product price


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