# -*- coding: utf-8 -*-
"""
SBI証券から保有資産をとってきますん(∩´∀｀)∩
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections import defaultdict
import json
import io


class SbiSec:

    def __init__(self, user_id, user_password):
        self.url_list = {
                'base_url': "https://site2.sbisec.co.jp/",
                'login_url': "https://site2.sbisec.co.jp/ETGate/"
        }
        self.login(user_id, user_password)

    def login(self, user_id, user_password):
        # 以下内容はログインページのhtmlから直接把握
        payload = {
                'JS_FLG': "0",
                'BW_FLG': "0",
                "_ControlID": "WPLETlgR001Control",
                "_DataStoreID": "DSWPLETlgR001Control",
                "_PageID": "WPLETlgR001Rlgn20",
                "_ActionID": "login",
                "getFlg": "on",
                "allPrmFlg": "on",
                "_ReturnPageInfo": "WPLEThmR001Control/DefaultPID/DefaultAID/DSWPLEThmR001Control",
                "user_id": user_id,
                "user_password": user_password
        }
        self.session = requests.session()
        res = self.session.post(self.url_list['login_url'], data=payload)
        res.raise_for_status()  # エラーの時に例外を発生させる

    def logout(self):
        self.session.close()

    def get_kouzakanri_url(self):
        """口座管理画面のURLはユーザーによらず一意だとは思いますが、それをしっかり確認していないので、
        念のため、ログイン後のトップ画面右上の「口座管理」ボタンからURLを取得することにしました。
        """
        if 'kouzakanri_url' in self.url_list:
            kouzakanri_url = self.url_list['kouzakanri_url']
        else:
            res = self.session.get(self.url_list['base_url'])
            soup = BeautifulSoup(res.text, "html.parser")

            # SBI証券トップページの右上の「口座管理」ボタンから相対URLを取得
            relative_path = soup.select_one("#link02M > ul > li:nth-of-type(3) > a").attrs["href"]
            kouzakanri_url = urljoin(self.url_list['base_url'], relative_path)
            self.url_list['kouzakanri_url'] = kouzakanri_url

        return kouzakanri_url

    def get_kouzakanri_html(self):
        res = self.session.get(self.get_kouzakanri_url())
        res.encoding = "cp932"  # 僕のPCはWindowsヽ(´ｴ`)ﾉ
        return res.text

    def get_kouzakanri_data(self):
        html = self.get_kouzakanri_html()
        soup = BeautifulSoup(html, "html.parser")

        tables = soup.find_all('table', width="300")

        # SBI証券の口座管理画面の各テーブル名を表す
        SBI_ACCOUNT_TYPE = dict(
            KABUSHIKI_TOKUTEI = 3,  # 株式(現物/特定預り)の箇所のテーブル
            KABUSHIKI_NISA = 4,     # 株式（現物/NISA預り
            TOUSHIN_TOKIUTEI = 5,   # 投資信託（金額/特定預り）
            TOUSHIN_NISA = 6        # 投資信託（金額/NISA預り）
            # 国内債券等は、他とテーブル構造が違っていた上、私は国債しか買っておらず興味がないので無視。
        )
        portfolio = defaultdict(lambda: defaultdict(dict))  # 3次元辞書を操作しやすくする為
        # Pythonで加工しやすくする為、一先ずリストに格納した
        for i in SBI_ACCOUNT_TYPE.values():
            rows = tables[i].find_all('tr')
            data = []
            for row in rows:
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                data.append([ele for ele in cols if ele])

            """
            dataは以下のような二重リスト。SBI証券のポートフォリオのtalbe構造と対応している。
                [[株式(現物/特定預り)],                           0行目：口座種別(1列)
                 ['保有株数', '取得単価', '現在値', '評価損益'],  1行目：ヘッダー(4列)
                 ['ISエマージング株', '現買 現売'],                 2行目(偶数行目)：投資商品名（2列)
                 [100, 4663, 5000, 33700]                       3行目（奇数行目)：データ (4列)
                 ['別商品', ....],                              別商品があれば偶数/奇数行目を以下繰り返し
                 [200, ....]]
            """

            table_name = data[0][0]
            header_row = data[1]
            body_rows = data[2:]
            for num in range(int(len(body_rows)/2)):
                toshi_item = body_rows[num*2][0]
                toshi_data_row = body_rows[num*2 + 1]
                portfolio[table_name][num] = dict(zip(header_row, toshi_data_row))
                portfolio[table_name][num]['投資商品'] = toshi_item

        return portfolio


if __name__ == '__main__':
    sbiobj = SbiSec(user_id="u0yaito", user_password="kebinnito")
    data = sbiobj.get_kouzakanri_data()
    sbiobj.logout()

    with io.open('filename.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=2, ensure_ascii=False)
