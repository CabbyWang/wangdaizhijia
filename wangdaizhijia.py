# coding:utf8
import re
import csv
import requests
from time import sleep
from bs4 import BeautifulSoup
from pypinyin import lazy_pinyin
from selenium import webdriver
# from contextlib import contextmanager
from itertools import chain

import models
from models import DBSession
from models import Base, Product, PlatData, ProblemPlat, PlatDetail, Rate


HEADERS = {"Cookie": "__jsluid_s=9d956f36619899229cc1c7de040697ee; WDZJptlbs=1; Hm_lvt_9e837711961994d9830dcd3f4b45f0b3=1578825667; _ga=GA1.2.26629386.1578825668; gr_user_id=30eafcf0-424e-45d4-8a89-74cc6090cf98; PHPSESSID=dribu5hagot7gs3apfu83mt365; Z6wq_e6e3_request_protocol=https; Z6wq_e6e3_con_request_uri=http%3A%2F%2Fpassport.wdzj.com%2Fuser%2Fqqconnect%3Fop%3Dcallback%26refer%3Dhttps%3A%2F%2Fshuju.wdzj.com%2Fproblem-1.html; Z6wq_e6e3_con_request_state=c1ab5fb04479d18b70396a1bc1a6c893; Z6wq_e6e3_saltkey=TyxJQkkQ; uid=2074816; login_channel=1; pc_login=1; Z6wq_e6e3_auth=8063Gp%2Fv9iFt%2F%2BYAotmp5G9oI%2Fv5wrh75liZHz86WaONpDr%2B4Vf2gfi4OFE%2BZH9MLQHjhGgtv4vDKfu19glz1IlqCbeF; auth_token=578d9sbdwleUvAOLbbCiY1%2FMgnfrNu%2Fw2c2f4qbYafLvaykCxbjdjNKvoJZE01Jq%2B9pN7%2Fyf5jpKkHsXcbzbVkYrUr0R; wdzj_session_source=https%253A%252F%252Fshuju.wdzj.com%252Fproblem-1.html; Hm_lpvt_9e837711961994d9830dcd3f4b45f0b3=1579451152; WDZJ_FRONT_SESSION_ID=5b1c9efdb4164a6d88ac6d042799173115429452769416644; _pk_id.1.b30f=5cb328c39cdc1fba.1578825667.7.1579451153.1579451153.; _pk_ses.1.b30f=*; gr_session_id_1931ea22324b4036a653ff1d3a0b4693=9ed98f81-2a30-49a8-bf12-a18a4130852c; gr_cs1_9ed98f81-2a30-49a8-bf12-a18a4130852c=user_id%3A2074816; gr_session_id_1931ea22324b4036a653ff1d3a0b4693_9ed98f81-2a30-49a8-bf12-a18a4130852c=true; _gid=GA1.2.1874952450.1579451154; Z6wq_e6e3_ulastactivity=ce54IWEAXNZCo4pV%2BaJsH%2FUqGKBamSGVGiYYZ4F8DtSpUt5Cque%2B",
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
"Content-Type": "text/html; charset=utf-8"}


MONTHS_2019 = [
    '2019-01-012019-01-31', '2019-02-012019-02-28', '2019-03-012019-03-31',
    '2019-04-012019-04-30', '2019-05-012019-05-31', '2019-06-012019-06-30',
    '2019-07-012019-07-31', '2019-08-012019-08-31', '2019-09-012019-09-30',
    '2019-10-012019-10-31', '2019-11-012019-11-30', '2019-12-012019-12-31'
]
MONTHS_2018 = [
    '2018-01-012018-01-31', '2018-02-012018-02-28', '2018-03-012018-03-31',
    '2018-04-012018-04-30', '2018-05-012018-05-31', '2018-06-012018-06-30',
    '2018-07-012018-07-31', '2018-08-012018-08-31', '2018-09-012018-09-30',
    '2018-10-012018-10-31', '2018-11-012018-11-30', '2018-12-012018-12-31'
]
MONTHS_2017 = [
    '2017-01-012017-01-31', '2017-02-012017-02-28', '2017-03-012017-03-31',
    '2017-04-012017-04-30', '2017-05-012017-05-31', '2017-06-012017-06-30',
    '2017-07-012017-07-31', '2017-08-012017-08-31', '2017-09-012017-09-30',
    '2017-10-012017-10-31', '2017-11-012017-11-30', '2017-12-012017-12-31'
]


def encode_response(resp):
    if resp.encoding == 'ISO-8859-1':
        resp.encoding = 'utf-8'


def CrawlFailed(Exception):
    pass

def crawl_products():
    url = "https://files.wdzjimages.com/shuju/product/search.json"
    print("crawl products...")
    response = requests.get(url)
    status = response.status_code
    if status != 200:
        print("crawl failed. (status is not 200)")
        raise CrawlFailed('crawl failed')
    products = response.json()
    for product in products:
        session = DBSession()
        new_product = Product(
            plat_id = product.get('platId'),
            name = product.get('platName'),
            old_name = product.get('oldPlatName'),
            pingyin = product.get('allPlatNamePin'),
            pin = product.get('autoPin')
        )
        session.add(new_product)
        session.commit()
        session.close()

def crawl_plat_data(shuju_date="2020-01-062020-01-12"):
    """
    平台成交数据 https://shuju.wdzj.com/platdata-1.html
    """
    url = "https://shuju.wdzj.com/plat-data-custom.html"
    form_data = {
        "type": 0,
        "shujuDate": shuju_date
    }
    response = requests.post(url, data=form_data)
    status = response.status_code
    if status != 200:
        print("crawl failed. (status is not 200)")
        raise CrawlFailed('crawl failed')
    plats_data = response.json()
    for plat_data in plats_data:
        plat_id = plat_data.get('wdzjPlatId')
        session = DBSession()
        new_platdata = PlatData(
            plat_id=plat_data.get('wdzjPlatId'),
            amount=plat_data.get('amount'),
            incomeRate=plat_data.get('incomeRate'),
            loanPeriod=plat_data.get('loanPeriod'),
            netInflowOfThirty=plat_data.get('netInflowOfThirty'),
            stayStillOfTotal=plat_data.get('stayStillOfTotal'),
            fullloanTime=plat_data.get('fullloanTime'),
            regCapital=plat_data.get('regCapital'),
            timeOperation=plat_data.get('timeOperation'),
            totalLoanNum=plat_data.get('totalLoanNum'),
            bidderNum=plat_data.get('bidderNum'),
            avgBidMoney=plat_data.get('avgBidMoney'),
            top10DueInProportion=plat_data.get('top10DueInProportion'),
            borrowerNum=plat_data.get('borrowerNum'),
            avgBorrowMoney=plat_data.get('avgBorrowMoney'),
            top10StayStillProportion=plat_data.get('top10StayStillProportion'),
            developZhishu=plat_data.get('developZhishu'),
            newbackground=plat_data.get('newbackground'),
            shuju_date=shuju_date
        )
        session.add(new_platdata)
        session.commit()
        session.close()


def crawl_all_plats_detail():
    """爬取所有平台的详细信息"""
    # 1. 获取所有平台的url
    # 2. 分别爬取
    response = requests.get('https://shuju.wdzj.com/platdata-1.html')
    if response.status_code != 200:
        raise CrawlFailed('crawl failed...')
    html = BeautifulSoup(response.text, features="lxml")
    plat_ids = [tr.attrs['data-platid'] for tr in html.select('.normal-table #platTable tr')]
    # hrefs = [a.attrs['href'] for a in html.select('.normal-table #platTable a[href^="//shuju"]')]
    for plat_id in plat_ids:
        # 分别爬取平台详细信息
        # url = "https://www.wdzj.com/zhishu/detail-{id}.html".format(id=plat_id)
        crawl_plat_detail(plat_id)


def crawl_plat_detail(plat_id):
    """
    平台数据详情页(指数) https://www.wdzj.com/zhishu/detail-{plat_id}.html
    """
    url = "https://www.wdzj.com/zhishu/detail-{plat_id}.html".format(
        plat_id=plat_id
    )
    print("crawl plat {}".format(plat_id))
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print('crawl failed: code: {}, url: {}'.format(response.status_code, url))
        return
        # raise CrawlFailed('crawl failed!')
    encode_response(response)
    html = BeautifulSoup(response.text, features='lxml')
    try:
        texts = list(reversed([div.string.strip() for div in html.select('.fr .xlist li div')]))
    except AttributeError as ex:
        print('crawl failed: ex: {}, url: {}'.format(str(ex), url))
        return
    results = dict(zip(texts[0::2], texts[1::2]))
    trans_results = {}
    # 汉字转拼音
    for k, v in results.items():
        trans_results[''.join(lazy_pinyin(k))] = v
    trans_results['plat_id'] = plat_id
    new_detail = PlatDetail(**trans_results)
    session = DBSession()
    session.add(new_detail)
    session.commit()
    session.close()


def crawl_problem_plats():
    """
    问题平台 https://shuju.wdzj.com/problem-1.html
    """
    url = "https://shuju.wdzj.com/problem-list-all.html"
    params = {"year": ""}
    response = requests.get(url, params=params, headers=HEADERS)
    json_data = response.json()
    problem_plats = json_data.get('problemList')
    for problem_plat in problem_plats:
        new_problem_plat = ProblemPlat(
            plat_id=problem_plat.get('platId'),  # plat_id
            area=problem_plat.get('area'),  # 地区
            oneline_time=problem_plat.get('onlineTime'),  # 上线时间
            problem_date=problem_plat.get('problemTime'),  # 问题时间
            event_type=problem_plat.get('type'),  # 事件类型
            people_num=problem_plat.get('peopleNumber'),
            status1=problem_plat.get('status1'),  # 保留字段status1
            status2=problem_plat.get('status2')  # 保留字段status2
        )
        session = DBSession()
        session.add(new_problem_plat)
        session.commit()
        session.close()


def crawl_rate():
    """
    网贷天眼->网贷指数->资金流入率 https://www.p2peye.com/rating/
    以月份为单位https://www.p2peye.com/rating_2019_8
    """
    # 1. 获取所有月份对应网址 2019_1
    rating_url = "https://www.p2peye.com/rating"
    response = requests.get(rating_url, headers=HEADERS)
    if response.status_code != 200:
        raise CrawlFailed('crawl failed!')
    encode_response(response)
    html = BeautifulSoup(response.text, features='lxml')
    month_href = {}
    for a in html.select('.rating-time-list a'):
        month_href[a.string] = a.attrs.get('href')
    # 2. 获取所有数据
    for month, href in month_href.items():
        url = "https://www.p2peye.com{href}".format(href=href)
        browser = webdriver.Chrome()
        browser.get(url)
        sleep(2)
        source_page = browser.page_source
        browser.quit()
        html = BeautifulSoup(source_page, features='lxml')
        for tr in html.select('.main-bd .bd'):
            plat_name = tr.select_one('.name-plat').string  # 平台名
            standard = tr.select_one('.standard').string  # 资金流入率
            # 数据存储
            new_rate = Rate(
                plat_name=plat_name,
                standard=standard,
                month=month
            )
            session = DBSession()
            session.add(new_rate)
            session.commit()
            session.close()


def main():
    # 1. plats data
    for month in chain(MONTHS_2017, MONTHS_2018, MONTHS_2019):
        crawl_plat_data(shuju_date=month)
    # 2. plats detail
    crawl_all_plats_detail()
    # 3. problem plats
    crawl_problem_plats()
    # 4. rate
    crawl_rate()


if __name__ == '__main__':
    main()


# print 使用log
