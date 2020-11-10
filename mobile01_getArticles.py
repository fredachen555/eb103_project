import requests, os, time, random
from bs4 import BeautifulSoup

headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/84.0.4147.105 Safari/537.36"}

mobile01_path = r'./mobile01a'
if not os.path.exists(mobile01_path):
    os.mkdir(mobile01_path)

for i in range(1, 2):

    url = 'https://www.mobile01.com/topiclist.php?f=360&p=1'

    res = requests.get(url=url, headers=headers)
    # print(res.status_code)
    soup = BeautifulSoup(res.text, 'html.parser')
    # print(soup.prettify())

    article_title_html = soup.select('div[class="c-listTableTd__title"]')
    # print(article_title_html)

    for each_article in article_title_html:
        try:
            print('============================================')
            print(each_article.a.text)
            article_title = each_article.a.text
            print('https://www.mobile01.com/'+each_article.a['href'])
            article_url = 'https://www.mobile01.com/'+each_article.a['href']
            article_res = requests.get(article_url, headers=headers)
            article_soup = BeautifulSoup(article_res.text, 'html.parser')
            article_content = article_soup.select('div[itemprop="articleBody"]')
            aritcle_content_text = article_content[0].text
            print(aritcle_content_text)
            with open(r'%s/%s.txt' % (mobile01_path, article_title), 'w', encoding= 'utf-8') as w:
                w.write(aritcle_content_text)
            print()
        except AttributeError as e:
            print('============')
            print(each_article)
            print(e.args)
            print('============')

        time.sleep(random.randint(2, 6))

    next_page_url = 'https://www.mobile01.com/topiclist.php?f=360&p=%s' % i
    # print(next_page_url)
    url = next_page_url