# coding: utf-8
import re
import requests
import time
import xlrd
from bs4 import BeautifulSoup
from lxml import etree

class WebOfScrapy(object):
    def __init__(self, sid, search_content, cookie):
        self.headers = {
            'Host': 'apps.webofknowledge.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://apps.webofknowledge.com/UA_AdvancedSearch_input.do?product=UA&search_mode=AdvancedSearch&SID=' + sid,
            "Cookie": cookie,
            'Content-Type': 'text/html;charset=UTF-8',
            'Content-Length': '1396',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

        self.form_data = {

            'action': 'search',
            'editions': ['SCI','SSCI','AHCI','ISTP','ISSHP','BSCI','BHCI','ESCI'],
            'endYear': '2018',
            'goToPageLoc': 'SearchHistoryTableBanner',
            'limitStatus':'collapsed',
            'period':'Range+Selection',
            'product':'UA',
            'range':'ALL',
            'replaceSetId':'',
            'rs_sort_by': 'PY.D;LD.D;SO.A;VL.D;PG.A;AU.A',
            'search_mode': 'AdvancedSearch',
            'SID': sid,
            'SinceLastVisit_DATE':'',
            'SinceLastVisit_UTC':'',
            'ss_lemmatization': 'On',
            'ss_query_language':'auto',
            'ss_showsuggestions': 'ON',
            'ss_spellchecking':'Suggest',
            'ssStatus':	'display:none',
            'startYear': '1980',
            'update_back2search_link_param': 'yes',
            'value(input1)': search_content,
            'value(searchOp)':'search',
            'value(limitCount)': '14',
            'value(select2)': 'LA',
            'value(select3)': 'DT'
        }

        self.form_data2 = {
            'product': 'WOS',
            'search_mode': 'AdvancedSearch',
            'SID': sid
        }

    def craw(self, root_uri):
        try:
            s = requests.session()
            s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'
            r = s.post(url=root_uri,data=self.form_data, headers=self.headers)
            r.encoding = r.apparent_encoding
            print(r.text)

        except Exception as e:
            print('Exception:', e)


if __name__ == '__main__':

    root = 'http://www.webofknowledge.com/'

    root_url = 'https://apps.webofknowledge.com/UA_AdvancedSearch.do'

    s = requests.get(root)
    sid = re.findall(r'SID=\w+&', s.url)[0].replace('SID=', '').replace('&', '')
    print('sid:', sid)
    cookie = s.headers["Set-Cookie"]
    Js = re.findall(r"(JSESSIONID=.*?);", cookie)

    search_condition1 = 'OO=(State Key Lab Qual Res Chinese Med OR Inst Chinese Med Sci) AND OG=(University of Macau OR Univ Macau OR Univ Macao OR Macau Univ OR Inst Chinese Med Sci OR State Key Lab Qual Res Chinese Med)'

    search_condition2 = 'OO=(State Key Lab Qual Res Chinese Med OR Inst Chinese Med Sci) AND OG=(University of Macau ' \
                        'OR Univ Macau OR Univ Macao OR Macau Univ OR Inst Chinese Med Sci OR State Key Lab Qual Res ' \
                        'Chinese Med) AND AU=(WANG YT)'

    scrapy = WebOfScrapy(sid=sid, search_content=search_condition1, cookie=Js[0])
    scrapy.craw(root_url)
