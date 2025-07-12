import requests
from bs4 import BeautifulSoup


url='https://www.ebay.com/sch/i.html?_from=R40&_nkw=Jordan+1&_sacat=15709&_sop=10&_ipg=50&LH_Auction=1&LH_BIN=1&_dcat=15709'
response=requests.get(url)
response.raise_for_status()
print(response.status_code)
soup=BeautifulSoup(response.text, "html.parser")
print(soup)


    # You'd do similar steps for product line, season, condition, image, etc.

