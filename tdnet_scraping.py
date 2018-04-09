from bs4 import BeautifulSoup
import requests
import feedparser
import zipfile
import xml.etree.ElementTree as ET

atom_URL="http://resource.ufocatch.com/atom/tdnetx"
r=requests.get(atom_URL)
soup=BeautifulSoup(r.content, "xml")
print(soup)
