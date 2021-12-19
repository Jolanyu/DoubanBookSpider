from bs4 import BeautifulSoup
import re
import pandas as pd
import time
import requests
import urllib.request


def getHtml(url):
    try:
        headers = {
            'Cookie':'bid=2D9W0HJxWyA; dbcl2="162857698: Z5Il+C1GKKs"; ck=GnLi; gr_user_id=b800a6ea-72d5-410f-b51e-fe270a77d17f; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03=e7ae3f1c-4ea3-4d0f-98ab-ec516bc0a564; gr_cs1_e7ae3f1c-4ea3-4d0f-98ab-ec516bc0a564=user_id%3A1; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03_e7ae3f1c-4ea3-4d0f-98ab-ec516bc0a564=true; __utma=30149280.1632251690.1639577701.1639577701.1639577701.1; __utmc=30149280; __utmz=30149280.1639577701.1.1.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmt_douban=1; push_noty_num=0; push_doumail_num=0; __utmb=30149280.2.10.1639577701',
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


def informationToCsv(html):
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
        bookDict['book_category'] = "文学"
        bookDict['book_publisher'] = publisher
        bookDict['book_summary'] = summary
        bookDict['create_time'] = timeStr
        bookDict['update_time'] = timeStr
        print(bookDict)
        bookList = []
        bookList.append(bookDict)
        bookDataFrame = pd.DataFrame(bookList)
        bookDataFrame.to_csv("books.csv", mode='a', header=False,
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

#https://book.douban.com/tag/%E5%B0%8F%E8%AF%B4
if __name__ == "__main__":
    startPage = 6
    endPage = 10
    for i in range(startPage, endPage+1):
        url = "https://book.douban.com/tag/%E5%B0%8F%E8%AF%B4?start=" + \
            str(i*20)+"&type=S"
        html = getHtml(url)
        urlList = getBookUrl(html)
        print(urlList)
        for url in urlList:
            html = getHtml(url)
            informationToCsv(html)
    # getBookUrl()
