import requests
from bs4 import BeautifulSoup

r = requests.get("https://velotio.com") #Fetch HTML Page
soup = BeautifulSoup(r.text, "html.parser") #Parse HTML Page
print "Webpage Title :" + soup.title.string
print "Fetch All Links:" soup.find_all('a')

