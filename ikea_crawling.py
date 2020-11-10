import requests
from http import cookiejar
from bs4 import BeautifulSoup
import time
import re
import os
import json
from numpy import random
from random import randint, choice
import pandas as pd
from fake_useragent import UserAgent
import threading


# 設定隨機產生假的代理伺服器
def set_header_user_agent():
    user_agent = UserAgent()
    return user_agent.random


# 建立指定路徑資料夾
def set_folders(keys):
    resource_path = r'./testfolder/' + keys

    if not os.path.exists(resource_path):
        os.makedirs(resource_path)

    else:
        return resource_path

# 將資料轉成json檔並寫入指定路徑資料夾內
def dump_json_file(query_dict, file_name, resource_path):

    with open(resource_path+"/{}.json".format(file_name),'w',encoding='utf-8') as outfile:
#             print(file_name)
            json.dump(query_dict, outfile, ensure_ascii=False)
            print('dump the data successfully')
            print('-'*30)


# 取得soup
def get_soup(url):
    #     useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
    referer = "https://www.ikea.com.tw/zh"

    user_agent = set_header_user_agent()

    headers = {'User-Agent': user_agent, 'referer': referer}
    cookies = cookiejar.CookieJar()

    res = requests.get(url=url, headers=headers, cookies=cookies)
    soup = BeautifulSoup(res.text, 'html.parser')
    time.sleep(randint(5, 8))

    return soup


# 先取得產品分類的總頁數，在產品分類的每一頁擷取單一產品頁面的url
url_list = []  # 存放抓取到的url
def get_page_url(keys):


    set_folders(keys)
    url = "https://www.ikea.com.tw/zh/products/" + keys  # keys = ["sofas/sofa-beds"]
    print(url)
    print("***" * 10)

    category_soup = get_soup(url)
    pages = category_soup.select('a[class="page-link"]')

    for page in range(1, len(pages) + 1):

        each_page = "https://www.ikea.com.tw/zh/products/" + keys + '?&&={}'.format(page)  # 1-12 page

        page_soup = get_soup(each_page)

        links = page_soup.select('div[class="card-header"] a')

        for link in range(len(links)):
            page_url = links[link]['href']

            url = 'https://www.ikea.com.tw' + page_url

            url_list.append(url)  # 將抓取的url存入url_list裡

            print(url)
            print("-" * 30)

            get_data(url, keys)

        print("=" * 30)
        time.sleep(randint(5, 8))


# 取造訪頁面所有所需資訊
done_url_list = []  # 存放已抓完產品資料的url
def get_data(url, keys):
    resource_path = set_folders(keys)

    process_url = set(url_list) - set(done_url_list)  # url_list清單 - 已跑過的url
    process_url = list(process_url)
    print(process_url)

    for u in process_url:

        page_soup = get_soup(u)
        time.sleep(randint(5, 8))

        try:
            # 產品編號
            part_id = page_soup.select('p[class="partNumber"]')[0].text.split(" ")[1]
            # print(part_id)

            # 產品名稱
            itemName = page_soup.select('a[class="itemName"]')[1].h6.text
            # print(itemName)

            # 產品副標題_產品名
            try:
                sub_itemName = page_soup.select('span[class="itemFacts"]')[0].text.split(',')[0]
                # print(sub_itemName)
            except Exception:
                sub_itemName = ''

            # 產品副標題_顏色
            try:
                color = page_soup.select('span[class="itemFacts"]')[0].text.split(',')[1].strip()
                # print(color)
            except Exception:
                color = ''

            # 價格
            try:
                price = page_soup.select('div[class="itemPrice-wrapper"]')[0].text.strip()
                # print(price)
            except Exception:
                price = ''

            # 購買次數
            try:
                purchase = page_soup.select('p[class="partNumber"]')[1].text.split(" ")[0]
                # print(p_time)
            except Exception:
                purchase = ''

            # 評分
            try:
                rating = page_soup.select('div[class="pr-snippet-stars pr-snippet-stars-png "]')
                # print(rating)
            except Exception:
                rating = ''

            #             # 設計師
            #             designer = page_soup.select('div[class="tab-pane_box"]')[5].select('div')[-1].text
            #             print(designer)
            #             time.sleep(randint(1,2))

            # 圖片網址
            img_list = []
            img_urls = page_soup.select('div[class="col-sm-12 col-md-10 col-lg-10 col slides"] a')
            for img in img_urls:
                img_url = 'https://www.ikea.com.tw' + img['href']
                print(img_url)
            img_list.append(img_url)

            # 產品資訊_內容
            product_information = page_soup.select('div[class="tab-pane_box"]')[0].text.replace('\n產品資訊\n', '').replace(
                '\n', '')
            # print(product_information)

            # 尺寸_內容
            size = page_soup.select('div[class="tab-pane_box"]')[1].text.split("\n\n\n")
            sizes = str(size[1:]).replace('\\n', '')
            # print(sizes)

            # 你要知道
            try:
                you_know = page_soup.select('div[class="tab-pane_box"]')[4].text.replace('你要知道', '').replace('\n',
                                                                                                             '').strip()
                # print(you_know)
            except:
                you_know = ''

            done_url_list.append(url)  # 將把抓完資料的url加入list中

        except Exception as e:
            print(e.args)
            pass

        # 建立Dict
        object_json = {'part_id': part_id,
                   'item_name': itemName,
                   'part_name': sub_itemName,
                   'color': color,
                   'price': price,
                   'purchase_time': purchase,
                   'rating': rating,
                   'page_url': url,
                   'images_url': img_list,
                   'production_information': product_information,
                   'size': sizes,
                   'you_know': you_know

                   }

        # 寫入json
        print(object_json)
        dump_json_file(object_json, part_id, resource_path)


def main():

    keys_list = ["sofas/fabric-sofas", "sofas/leather-sofas"]
#     keys_list = ["sofas/sofa-beds", "sofas/armchairs"]
#     keys_list = ["dining-tables/tables"]
#     keys_list = ["dining-seating/chairs-incl-covers-folding-chairs", "dining-seating/bar-stools-incl-covers"]
#     keys_list = ["beds/double-beds", "beds/single-beds", "beds/day-beds"]
#     keys_list = ["work-desks/home-desks", "work-desks/study-for-children"]

    for i in keys_list:
        get_page_url(i)
        time.sleep(randint(5,10))


if __name__ == '__main__':

    try:
        main()

    except Exception as e:
        print(e.args)
        time.sleep(randint(10, 15))
        pass