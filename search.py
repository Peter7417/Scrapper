# from googlesearch import search
#
# list = search("5800x3d BOX computer store uk",num_results=100)
# matrix = []
# for response in list:
#     print(response)

from duckduckgo_search import ddg


s = "ryzen 5800x3d box uk"
search_matrix = ddg(s,max_results=5)

for response in search_matrix:

    title = response["title"]
    if title.find("Box.co.uk") > 0:
        print(response["href"])
        break

# print(a[1]["href"])




