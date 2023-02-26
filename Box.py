import requests
from bs4 import BeautifulSoup
from googlesearch import search


user_search = input("Product search: ")
matrix = search(user_search + "box online technology store")
URL = []
for result in matrix:
    URL.append(result)

page = requests.get(URL[0])
print(URL[0])
soup = BeautifulSoup(page.content, "html.parser")
print(soup)

results = soup.find(class_="wrapper")
print(results)
job_elements = results.find_all("div", class_="product-list-item")
job_elements_middle = results.find_all("div", class_="product-list-item middle")
# print(job_elements)

for job_element in job_elements:
    name_element = job_element.find("div", class_="p-list-title-wrapper")
    price_element = job_element.find("div", class_="p-list-price")
    for a in name_element.find_all('a', href=True):
         link = a['href']
    if price_element is not None:
        print("Product_name: ", name_element.text.strip())
        print("Link: ", link)
        print("Price: ", price_element.text.strip())
        print()

for job_element_middle in job_elements_middle:
    name_element = job_element_middle.find("div", class_="p-list-title-wrapper")
    price_element = job_element_middle.find("div", class_="p-list-price")
    for a in name_element.find_all('a', href=True):
         link = a['href']
    if price_element is not None:
        print("Product_name: ", name_element.text.strip())
        print("Link: ", link)
        print("Price: ", price_element.text.strip())
        print()



