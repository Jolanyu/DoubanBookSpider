# coding=UTF-8
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
import requests
import urllib.request


def getHtml(url):
    try:
        # headers ={'Accept':' text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        #             'Accept-Encoding':' gzip, deflate, br',
        #             'Accept-Language':' zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        #             'Cache-Control':' max-age=0',
        #             'Connection':' keep-alive',
        #             'Cookie':' ll="118173"; bid=1iQbWhYAXOM; _vwo_uuid_v2=D655EC661D666A8A76FE878BBD48D18DC|8ddc37444cef48249f22ecc6f86891bd; douban-fav-remind=1; gr_user_id=afd4d13d-8a4c-480f-bc86-43280b88b59b; _vwo_uuid_v2=D655EC661D666A8A76FE878BBD48D18DC|8ddc37444cef48249f22ecc6f86891bd; _ga=GA1.1.521507932.1609933925; _ga_RXNMP372GL=GS1.1.1639405375.2.0.1639405375.0; __utmz=30149280.1639917073.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmz=81379588.1639917073.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); ap_v=0,6.0; __utma=30149280.521507932.1609933925.1639997883.1640000396.3; __utmc=30149280; __utma=81379588.521507932.1609933925.1639997883.1640000396.3; __utmc=81379588; _pk_ses.100001.3ac3=*; viewed="3750803"; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03=06d903cb-5a75-4ff2-9238-acf9b8e706fb; gr_cs1_06d903cb-5a75-4ff2-9238-acf9b8e706fb=user_id%3A0; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03_06d903cb-5a75-4ff2-9238-acf9b8e706fb=true; __utmt_douban=1; __utmt=1; _pk_id.100001.3ac3=d02209b36d922bb8.1639917073.3.1640002881.1639997894.; __utmb=30149280.31.10.1640000396; __utmb=81379588.31.10.1640000396',
        #             'Host':' book.douban.com',
        #             'sec-ch-ua':' " Not A;Brand";v="99", "Chromium";v="96", "Microsoft Edge";v="96"',
        #             'sec-ch-ua-mobile':' ?0',
        #             'sec-ch-ua-platform':' "Windows"',
        #             'Sec-Fetch-Dest':' document',
        #             'Sec-Fetch-Mode':' navigate',
        #             'Sec-Fetch-Site':' none',
        #             'Sec-Fetch-User':' ?1',
        #             'Upgrade-Insecure-Requests':' 1',
        #             'User-Agent':' Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62',}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36 Edg/96.0.1054.53'
        }
        page = urllib.request.Request(url, headers=headers)
        page = urllib.request.urlopen(page)
        html = page.read()
    except:
        print("failed to geturl")
        return ''
    else:
        return html


def parsePage(html, str, flag=True):
    try:
        if flag:
            reStr = r'<span class="pl">'+str+r'.*?</span>(.*?)<br/>'
        else:
            reStr = r'<span class="pl">.*?'+str+r'.*?">(.*?)</a>'
        infoList = re.findall(reStr, html, re.S)
        if len(infoList) >= 1:
            return infoList[0].strip().replace("\n", "").replace(" ", "")
        else:
            return None
    except Exception as e:
        print(e)
        return None


def informationToCsv(html, bookClass):
    try:
        soup = BeautifulSoup(
            html, features="lxml")
        info = str(soup.select('#info')[0])
        pList = None
        summary = ""
        try:
            pList = soup.select('.intro')[0].find_all("p")
            for p in pList:
                summary = summary + p.string
            summary = summary.replace("\r", "")
            summary = summary.replace("(展开全部)", "")
        except Exception as e:
            print(e)
        title = soup.h1.span.string
        image = soup.select('#mainpic')[0].a['href']
        author = parsePage(info, "作者", False)
        publisher = parsePage(info, "出版社")
        translator = parsePage(info, "译者", False)
        isbn = parsePage(info, "ISBN")
        timeStr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

        bookDict = {}
        bookDict['book_isbn'] = isbn
        bookDict['bokk_title'] = title
        bookDict['book_image'] = image
        bookDict['book_author'] = author
        bookDict['book_translator'] = translator
        bookDict['book_category'] = bookClass
        bookDict['book_publisher'] = publisher
        bookDict['book_summary'] = summary
        bookDict['create_time'] = timeStr
        bookDict['update_time'] = timeStr
        print(bookDict)
        bookList = []
        bookList.append(bookDict)
        bookDataFrame = pd.DataFrame(bookList)
        csvName = bookClass + ".csv"
        bookDataFrame.to_csv(csvName, mode='a', header=False,
                             index=False, encoding='utf-8')
    except Exception as e:
        print(e)


def getBookUrl(html):
    soup = BeautifulSoup(
        html, features="lxml")
    aList = soup.select(".nbg")
    urlList = []
    for item in aList:
        urlList.append(item['href'])
    return urlList


# https://book.douban.com/tag/%E5%84%BF%E7%AB%A5%E6%96%87%E5%AD%A6?start=0&type=S
if __name__ == "__main__":
    startPage = 32
    endPage = 49
    bookClass = "美食"
    bookClassCode = urllib.parse.quote(bookClass)
    for i in range(startPage, endPage+1):
        url = "https://book.douban.com/tag/"+bookClassCode+"?start=" + \
            str(i*20)+"&type=S"
        print("正在爬第"+str(i+1)+"页 url:"+url)
        html = getHtml(url)
        urlList = getBookUrl(html)
        print(urlList)
        time.sleep(5)
        for url in urlList:
            time.sleep(5)
            html = getHtml(url)
            informationToCsv(html, bookClass)
