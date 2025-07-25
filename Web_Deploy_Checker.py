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

# Function to capture voice input
def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Speak your Pokémon search query:")
        audio = recognizer.listen(source)
    try:
        query = recognizer.recognize_google(audio)
        print(f"🗣️ You said: {query}")
        return query
    except sr.UnknownValueError:
        print("❌ Could not understand audio.")
    except sr.RequestError:
        print("❌ Could not request results from Google Speech Recognition.")
    return None

# Ask user for input mode
mode = input("Choose input mode: (1) Voice (2) Text: ")

if mode == "1":
    search_query = get_voice_input()
    if not search_query:
        search_query = input("Fallback to text input. Enter your query: ")
elif mode == "2":
    search_query = input("Enter your Pokémon search query: ")
else:
    print("Invalid choice. Defaulting to text input.")
    search_query = input("Enter your Pokémon search query: ")

# Setup Chrome
options = Options()
options.add_experimental_option("detach", True)
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
driver.maximize_window()

# Step 1: Go to Bing and handle cookie popup
driver.get("https://www.bing.com")
try:
    cookie_button = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "bnp_btn_accept"))
    )
    cookie_button.click()
    print("✅ Cookie consent accepted.")
except:
    print("ℹ️ No cookie popup appeared.")

# Step 2: Perform search
try:
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "q"))
    )
    full_query = f"{search_query} "+ "UK/Europe" + "English"
    search_box.send_keys(full_query + Keys.ENTER)
except:
    print("❌ Search box not found.")
    driver.quit()

# Step 3: Get top 20 search results
time.sleep(2)
results = driver.find_elements(By.CSS_SELECTOR, "li.b_algo h2 a")[:20]

# Step 4: Visit each result and check stock status
for i, result in enumerate(results):
    url = result.get_attribute("href")
    print(f"\n🔗 Checking site {i+1}: {url}")
    driver.execute_script("window.open(arguments[0]);", url)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(3)

    page_text = driver.page_source.lower()
    if any(keyword in page_text for keyword in ["in stock", "available", "add to cart"]):
        print("✅ Product appears to be IN STOCK.")
    elif any(keyword in page_text for keyword in ["out of stock", "sold out", "unavailable"]):
        print("❌ Product appears to be OUT OF STOCK.")
    else:
        print("⚠️ Stock status unclear.")

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

# Optional: Keep browser open
# time.sleep(30)
