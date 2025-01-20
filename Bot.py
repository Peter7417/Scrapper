from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

options =Options()
service = Service(ChromeDriverManager().install())
options.add_experimental_option("detach",True)

driver = webdriver.Chrome(service=service,
                          options=options)

driver.get("https://www.chaoscards.co.uk/shop/card-games/pokemon")
driver.maximize_window()
time.sleep(1)

#Reject = driver.find_element(By.XPATH, '//*[@id="W0wltc"]/div')
#time.sleep(5)
#Reject.click()

search = driver.find_element(By.XPATH, '//*[@id="header_search_search_for"]')
time.sleep(1)
search.send_keys("Pokemon prismatic evolution" + Keys.ENTER)

time.sleep(2)
if driver.find_element((By.XPATH, '//*[@id="product-quick-buy-364192"]/span')) is True:
    add = driver.find_element(By.XPATH, '//*[@id="product-quick-buy-364192"]/span')
    add.click()
else:
    print("none")


#time.sleep(30)
