from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import sys
import requests
import re
import math

sleep_time = 1

options = Options()
options.headless = True
driver = webdriver.Firefox(options=options, executable_path='geckodriver.exe')

root = 'http://www.webofknowledge.com/'
s = requests.get(root)
sid = re.findall(r'SID=\w+&', s.url)[0].replace('SID=', '').replace('&', '')
print('sid:', sid)

first_page = 'https://apps.webofknowledge.com/WOS_AdvancedSearch_input.do?product=WOS&search_mode=AdvancedSearch&SID=' + sid.strip()
driver.get(first_page)
time.sleep(sleep_time)

input_form = driver.find_element_by_id('value(input1)')
if input_form:
    print('Find input form')
else:
    print('Input form not found!')

content = 'OO=(State Key Lab Qual Res Chinese Med OR Inst Chinese Med Sci) AND OG=(University of Macau OR Univ Macau OR Univ Macao OR Macau Univ OR Inst Chinese Med Sci OR State Key Lab Qual Res Chinese Med)'
input_form.send_keys(content)
input_form.submit()

locator = (By.ID, 'set_1_div')

try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    search_result_elem = driver.find_element_by_id('set_1_div')
    if search_result_elem:
        print("Find search item element")
        print('text', search_result_elem.text)

        result_num = int(search_result_elem.text)
        search_result_elem_a = search_result_elem.find_element_by_tag_name('a')

        item_per_page = 10

        if search_result_elem_a:
            search_result_url = search_result_elem_a.get_attribute('href')
            if search_result_url != '':
                for i in range(1, result_num+1):

                    title_str = ''
                    author_str = ''
                    journal_str = ''
                    impact_factor_str = ''
                    impact_factor_5year_str = ''
                    citation_frequency = ''


                    page_id = int(math.floor(i * 1. / item_per_page)) + 1
                    if i % item_per_page == 0:
                        page_id -= 1
                    item_id = i
                    print('process %d page %d item' % (page_id, item_id))

                    page_url = search_result_url + '&page=' + str(page_id)

                    driver.get(page_url)
                    time.sleep(sleep_time)

                    record_div = driver.find_element_by_id('RECORD_' + str(item_id))
                    record_alist = record_div.find_elements_by_tag_name('a')
                    if record_alist is None or len(record_alist) == 0:
                        continue
                    record_title_a = record_alist[0]

                    # title
                    title_str = record_title_a.text.strip()
                    print(title_str)

                    item_url = record_title_a.get_attribute('href')
                    print(item_url)
                    driver.get(item_url)
                    time.sleep(sleep_time)

                    # author
                    rf_field_elements = driver.find_elements_by_class_name('FR_field')
                    if rf_field_elements:
                        # author
                        author_str = rf_field_elements[0].text.strip()
                        if '作者:' in author_str:
                            author_str = author_str.replace('作者:', '')
                        print(author_str)
                    else:
                        print('not find authors')

                    # journal
                    source_title_p = driver.find_elements_by_class_name('sourceTitle')
                    if source_title_p:
                        journal_str = source_title_p[0].text.strip()
                        print(journal_str)
                    else:
                        print('not find journal')

                    # impact factor and 5-year
                    if_table_elem = driver.find_elements_by_class_name('Impact_Factor_table')
                    print('table len:', len(if_table_elem))
                    print('table:', if_table_elem[0].text)
                    if if_table_elem and len(if_table_elem) >= 1:
                        td_elements = if_table_elem[0].find_elements_by_tag_name('td')
                        print('td elements len:', len(td_elements))
                        if td_elements and len(td_elements) == 2:
                            impact_factor_str = td_elements[0].get_attribute("textContent")
                            impact_factor_5year_str = td_elements[1].get_attribute("textContent")
                    # citation frequency

                    try:
                        sidebar_column1 = driver.find_element_by_id('UA_scoredcard_data')
                        if sidebar_column1:
                            citation_frequency = sidebar_column1.text.strip()
                            if '/ 所有数据库' in citation_frequency:
                                citation_frequency = citation_frequency.replace('/ 所有数据库', '')
                        else:
                            print('not find cf!')
                    except:
                        citation_frequency = '0'

                    print('title:', title_str, '\n authors:', author_str, '\n journal:', journal_str, '\n if:', impact_factor_str, '\n if 5year:', impact_factor_5year_str, '\n cf:', citation_frequency)

                    time.sleep(sleep_time)

    else:
        print('Not find the search result element!')

finally:
    driver.quit()
