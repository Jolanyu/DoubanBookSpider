# coding=UTF-8
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
import requests
import urllib.request


def getHtml(url):
    try:
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
    startPage = 0
    endPage = 38
    bookClass = "教育"
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
