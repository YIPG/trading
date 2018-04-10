from bs4 import BeautifulSoup
import requests
import feedparser
import zipfile
import xml.etree.ElementTree as ET

atom_URL = "http://resource.ufocatch.com/atom/tdnetx"
r = requests.get(atom_URL)
soup = BeautifulSoup(r.content, "xml")

Comp_name_l = soup.find_all("title")
XBRL_URL_l = soup.find_all(type="text/html")
for (title, link) in zip(Comp_name_l, XBRL_URL_l):
    comp = title.string
    XBRL_URL = link.get("href")
    # r2 = requests.get(XBRL_URL)
    # soup2 = BeautifulSoup(r2.content, "html")
    print(comp,XBRL_URL)

### 挫折した。HTMLをスクレイピングしてやってもいいが劇的に速度が落ちる
### そもそもAtomAPIの使い方知ってればこんなことには・・・
### というかキャッシュフローとかみてもSloan Ratioに着目するなら、それだけでいいやんってなった
### データたくさんとりたいときにこれは必要！！！
