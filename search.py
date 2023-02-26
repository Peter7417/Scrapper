from duckduckgo_search import ddg

s = "ryzen 5800x3d box uk"
search_matrix = ddg(s,max_results=5)

for response in search_matrix:

    title = response["title"]
    if title.find("Box.co.uk") > 0:
        link = (response["href"])
        break

# print(a[1]["href"])




