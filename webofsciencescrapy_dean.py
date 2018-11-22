# coding: utf-8
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
import os
import csv


sleep_time = 1

search_condition2 = 'AD=(State Key Lab Qual Res Chinese Med OR Inst Chinese Med Sci) AND OG=(University of Macau ' \
                    'OR Univ Macau OR Univ Macao OR Macau Univ OR Inst Chinese Med Sci OR State Key Lab Qual Res ' \
                    'Chinese Med) AND AU=(WANG YT)'

total_result_file_path = 'total_result_num_dean.txt'

data2_path = "Publish_papers_statistics_dean.csv"


class WebOfScrapy(object):
    def __init__(self):
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options, executable_path='../geckodriver')

    def __del__(self):
        self.driver.quit()

    def get_sid(self, root):
        """
        Get sid from first page.
        :param root:
        :return:
        """
        sid = ''
        if root:
            s = requests.get(root)
            sid = re.findall(r'SID=\w+&', s.url)[0].replace('SID=', '').replace('&', '')
            s.close()
        return sid

    def craw(self, url, search_conditon, result_file_name):
        """
        Craw the website of WOC
        :param url:
        :param search_conditon:
        :return:
        """
        if url == "":
            print("Advanced Search url can't find!")
            return

        # get Advanced Search Page
        self.driver.get(url)
        time.sleep(sleep_time)

        # get input form of Advanced Search Page
        input_form = self.driver.find_element_by_id('value(input1)')
        if input_form:
            print('Find input form')
        else:
            print('Input form of Advanced Search Page not found!')
            return

        input_form.send_keys(search_conditon)
        input_form.submit()

        locator = (By.ID, 'set_1_div')
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(locator))
            search_result_elem = self.driver.find_element_by_id("set_1_div")
            if search_result_elem:
                print("Find search item element:", search_result_elem.text)
                result_num_str = search_result_elem.text
                if "," in result_num_str:
                    result_num_str = result_num_str.replace(",", "")

                # check result is updated or not.

                current_total_num = ""
                with open(total_result_file_path, 'r') as f:
                    current_total_num = f.readlines()[0].strip()

                if current_total_num == result_num_str:
                    print("Not find new paper published")
                    return
                else:
                    print("There are a lot of new papers published!")

                result_num = int(result_num_str)
                search_result_elem_a = search_result_elem.find_element_by_tag_name('a')

                item_per_page = 10
                if search_result_elem_a:
                    search_result_url = search_result_elem_a.get_attribute('href')
                    if search_result_url != '':

                        # write to csv file
                        with open(result_file_name, 'w') as csvfile:
                            csv_writer = csv.writer(csvfile)
                            csv_writer.writerow(["Title", "Authers", "Publish Year", "Journal", "IF", "IF-5year", "Citation Frequency"])

                            for i in range(1, result_num + 1):

                                title_str = ""
                                author_str = ""
                                journal_str = ""
                                impact_factor_str = "0"
                                impact_factor_5year_str = "0"
                                citation_frequency_str = "0"
                                publish_year_str = ""

                                page_id = int(math.floor(i * 1. / item_per_page)) + 1
                                if i % item_per_page == 0:
                                    page_id -= 1
                                item_id = i
                                print('process %d page %d item' % (page_id, item_id))

                                page_url = search_result_url + '&page=' + str(page_id)

                                self.driver.get(page_url)
                                time.sleep(sleep_time)

                                record_div = self.driver.find_element_by_id('RECORD_' + str(item_id))
                                record_alist = record_div.find_elements_by_tag_name('a')
                                if record_alist is None or len(record_alist) == 0:
                                    continue
                                record_title_a = record_alist[0]

                                # title
                                title_str = record_title_a.text.strip()

                                item_url = record_title_a.get_attribute('href')
                                self.driver.get(item_url)
                                time.sleep(sleep_time)

                                # author
                                rf_field_elements = self.driver.find_elements_by_class_name('FR_field')
                                if rf_field_elements:
                                    # author
                                    author_str = rf_field_elements[0].text.strip()
                                    if '作者:' in author_str:
                                        author_str = author_str.replace('作者:', '')
                                    elif "By:" in author_str:
                                        author_str = author_str.replace("By:", "")

                                    # publish year
                                    for rf_id in range(len(rf_field_elements)):
                                        if "Published:" in rf_field_elements[rf_id].text or "出版年:" in rf_field_elements[rf_id].text:
                                            publish_year_str = rf_field_elements[rf_id].text.strip()
                                            if "Published:" in publish_year_str:
                                                publish_year_str = publish_year_str.replace("Published:", "").strip()
                                            elif "出版年:" in publish_year_str:
                                                publish_year_str = publish_year_str.replace("出版年:", "").strip()
                                            if publish_year_str != "":
                                                print(publish_year_str)
                                                publish_year_str = re.findall(r'[0-9]{4}', publish_year_str)[0].strip()
                                    #
                                    #
                                    # publish_year_str = rf_field_elements[4].text.strip()
                                    # if "Published:" in publish_year_str:
                                    #     publish_year_str = publish_year_str.replace("Published:", "").strip()
                                    # elif "出版年:" in publish_year_str:
                                    #     publish_year_str = publish_year_str.replace("出版年:", "").strip()
                                    # if publish_year_str != "":
                                    #     print(publish_year_str)
                                    #     publish_year_str = re.findall(r'[0-9]{4}', publish_year_str)[0].strip()

                                else:
                                    print('not find authors')

                                # journal
                                source_title_p = self.driver.find_elements_by_class_name('sourceTitle')
                                if source_title_p:
                                    journal_str = source_title_p[0].text.strip()
                                else:
                                    print('not find journal')

                                # impact factor and 5-year
                                if_table_elem = self.driver.find_elements_by_class_name('Impact_Factor_table')

                                if if_table_elem and len(if_table_elem) >= 1:
                                    td_elements = if_table_elem[0].find_elements_by_tag_name('td')
                                    print('td elements len:', len(td_elements))
                                    if td_elements and len(td_elements) == 2:
                                        impact_factor_str = td_elements[0].get_attribute("textContent")
                                        impact_factor_5year_str = td_elements[1].get_attribute("textContent")

                                # citation frequency in all database
                                try:
                                    sidebar_column1 = self.driver.find_element_by_id('UA_scoredcard_data')
                                    if sidebar_column1:
                                        citation_frequency_str = sidebar_column1.text.strip()
                                        if '/ 所有数据库' in citation_frequency_str:
                                            citation_frequency_str = citation_frequency_str.replace('/ 所有数据库', '')
                                        elif " in All Databases" in citation_frequency_str:
                                            citation_frequency_str = citation_frequency_str.replace(" in All Databases", "")
                                    else:
                                        print('not find cf!')
                                except:
                                    citation_frequency_str = '0'

                                csv_writer.writerow([title_str, author_str, publish_year_str, journal_str, impact_factor_str, impact_factor_5year_str, citation_frequency_str])

                                time.sleep(sleep_time)

                # update total number of result
                with open(total_result_file_path, 'w') as f:
                    f.write(result_num_str)

            else:
                print("Not find the research result element!")
                return


        finally:
            self.driver.quit()



def main():
    root = 'http://www.webofknowledge.com/'

    app = WebOfScrapy()

    # get sid from website
    sid = app.get_sid(root)
    if sid == "":
        print("Network error!, Can't find SID from WOC!")
        return
    else:
        print("SID:", sid)

    # get Advanced search page
    advanced_search_page_url = 'https://apps.webofknowledge.com/WOS_AdvancedSearch_input.do?product=WOS&search_mode=AdvancedSearch&SID=' + sid.strip()
    print(advanced_search_page_url)

    # craw search result page of condition 2
    app.craw(advanced_search_page_url, search_condition2, data2_path)
    print("Search condtion 2 finished!")


if __name__ == '__main__':
    main()
