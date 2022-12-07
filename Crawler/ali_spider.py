import requests
import os
from bs4 import BeautifulSoup
import pickle
import numpy
import pandas as pd
import time
import re
import random
from svgCaptchaCrack import svgCrack

# 验证码
# http://alibaba2kw6qoh6o.onion/captcha
captcha = "http://alibaba2kw6qoh6o.onion/captcha"

# 登录界面
# http://xxxxxxxxxs6qbnahsbvxbghsnqh4rj6whbyblqtnmetf7vell2fmxmad.onion/entrance/logins.php
login = "http://alibaba2kw6qoh6o.onion/login"

base = "http://alibaba2kw6qoh6o.onion"

proxies = {'http':'http://127.0.0.1:8118','https':'https://127.0.0.1:8118'}

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:82.0) Gecko/20100101 Firefox/82.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Content-Type": "application/x-www-form-urlencoded",
    "Connection": "keep-alive"

}

class DarkSpider:
    def __init__(self,proxies,headers,captcha,login):
        self.proxies = proxies
        self.headers = headers
        self.captcha = ""
        self.login = login
        self.nav = {}
        self.maxPage = 0
        self.urls = []
        self.category = ""

    def saveSession(self,name):
        s = requests.Session()
        pre = s.get(base, headers=self.headers, proxies = self.proxies)
        # print(s.cookies)
        # cookie_dict = requests.utils.dict_from_cookiejar(s.cookies)
        # print(cookie_dict)
        # headers.update(cookie_dict)
        # print(headers)
        # print(pre.text)
        # self.save_page("base",pre)
        soup = BeautifulSoup(pre.text,'lxml')
        code1_uri = soup.select("img")[0]
        # print(code1_uri["src"])
        code1_url = base+code1_uri["src"]+"="
        code1 = s.get(code1_url, headers=self.headers, proxies = self.proxies)
        # print(code1.text)
        # with open('code1.svg', 'wb') as file:
        #     file.write(code1.content)
        #     file.close

        # 破解验证码
        cap1 = svgCrack(code1.text)

        # cap1 = input("验证码：")
        # print(s.cookies)
        header_test = {
            "Host": "alibaba2kw6qoh6o.onion",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Referer": "http://alibaba2kw6qoh6o.onion/",
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": "12",
            "Origin": "http://alibaba2kw6qoh6o.onion",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        login_page1 = s.post(base,headers=header_test, data={"captcha":cap1},proxies=proxies)
        # self.save_page("login1",login_page1)
        # print(login_page1.status_code)
        # print(login_page1.headers)
        # time.sleep(3)
        login_page2 = s.get(base,headers=headers, proxies=proxies)
        self.save_page("login2",login_page2)
        soup = BeautifulSoup(login_page2.text,'lxml')
        soup = BeautifulSoup(open("login2.html"),'lxml')
        code2_uri = soup.find("div",class_="flex-end")
        code2_uri = re.findall(re.compile("url\('(.*?)'\)"),str(code2_uri))
        # print(code2_uri)
        code2_url = base+code2_uri[0]
        code2 = s.get(code2_url, headers=self.headers, proxies = self.proxies)
        # with open('code2.svg', 'wb') as file:
        #     file.write(code2.content)
        #     file.close
        #
        # cap2 = input("验证码：")

        cap2 = svgCrack(code2.text)

        data = {
        	"name": "598110",
        	"passwd": "exchange666",
        	"captcha": cap2
        }

        login_page3 = s.post(login, headers=headers, data=data, proxies=proxies)
        # print(login_page3.text)
        self.save_page("login3",login_page3)


        index = s.get(base+"/shop/", headers=headers, proxies=proxies)
        # print(index.text)
        self.save_page("index",index)


        with open("session_{}.pickle".format(name),'wb') as f:
            pickle.dump(s,f)
        print("Session_{}保存成功。".format(name))

    def loadSession(self,name,fail):
        if fail > 0:
            self.saveSession(name)
            with open("session_{}.pickle".format(name),'rb') as f:
                session = pickle.load(f)
            return session
        if os.path.exists("session_{}.pickle".format(name)):
            with open("session_{}.pickle".format(name),'rb') as f:
                session = pickle.load(f)
            return session
        else:
            print("获取Session中...")
            self.saveSession(name)
            with open("session_{}.pickle".format(name),'rb') as f:
                session = pickle.load(f)
            return session

    def getNav(self):
        soup = BeautifulSoup(open('index.html'), "lxml")
        div = soup.find("div",class_="categories")
        table = div.select("a")
        # print(table)
        for a in table:
            category = a.get_text().strip()
            link = a['href']
            # print(category)
            self.nav[category] = base+link
            # print(self.nav[category])

    def getMaxPage(self,name):
        try:
            self.category = name
            s = self.loadSession(name,0)
            url = self.nav[name]
            print("正在爬取页数...")
            cate = s.get(url,headers=headers,proxies=proxies)
            # self.save_page(name,cate)
            soup = BeautifulSoup(cate.text, "lxml")
            # 页码
            ul = soup.find("ul",class_="pagination text-center")
            li = ul.select("li")
            maxPage = int(li[-1].a['href'].split("=")[-1])
        except Exception as e:
            print(e)
            print("发生错误，重新获取Session...")
            self.saveSession(name)
            s = self.loadSession(name,0)
            url = self.nav[name]
            print("正在爬取页数...")
            cate = s.get(url,headers=headers,proxies=proxies)
            # self.save_page(name,cate)
            soup = BeautifulSoup(cate.text, "lxml")
            # 页码
            ul = soup.find("ul",class_="pagination text-center")
            li = ul.select("li")
            maxPage = int(li[-1].a['href'].split("=")[-1])
            print("{}类别最多有%d页".format(name) % maxPage)
            self.maxPage = maxPage
            return maxPage
        else:
            print("{}类别最多有%d页".format(name) % maxPage)
            self.maxPage = maxPage
            return maxPage


    def save_page(self,name,file):
        f = open("{}.html".format(name), "wb")
        f.write(file.content)
        f.close()
        print("{}页面保存成功。".format(name))

    # 在每页获取交易链接
    def getURL(self,s,link,):
        # s = self.loadSession(fail)
        aPage = s.get(link,proxies=proxies,headers=headers)
        soup = BeautifulSoup(aPage.text, "lxml")
        div = soup.find("div",class_="col-md-6 pt-3 pl-md-3 pr-md-3")
        # 获取标题所在a标签
        title_a = div.findAll("a",class_="ads d-flex")
        # print(title_a)
        info_list = []
        for a in title_a:
            # 字典必须定义在for里面
            trans_data = {}

            # 每个交易的类别
            trans_data['category'] = self.category
            # # 每个交易的ID
            # trans_data['ID'] = infoAll.td.string
            # # 每个交易的发布时间
            # trans_data['post_time'] = infoAll.contents[1].string
            # # 每个交易的发布人
            # trans_data['OP'] = infoAll.contents[2].string
            # 每个交易的标题
            trans_data['title'] = a.find("b",class_="title spot").get_text().strip()
            # # 每个交易的比特币价值
            # trans_data['price_bc'] = infoAll.contents[4].string
            # 每个交易的链接
            trans_data['url'] = base+a["href"]
            info_list.append(trans_data)
            # print(trans_data)
        return info_list


    # 获取一个种类的所有交易链接和信息
    def getURLs(self):
        name = self.category
        link_base = "{}?page={}"
        fail=0
        # self.maxPage = 1
        for i in range(self.maxPage):
            try:
                # time.sleep(random.uniform(0.5,1.5))
                print("获取'{}'第{}页的简要信息...".format(name,i+1))
                link = link_base.format(self.nav[name],i+1)
                s = self.loadSession(name,0)
                brief_info = self.getURL(s,link)
                # print(brief_info,sep='\n')
                # self.urls = self.urls + brief_info
                self.urls.extend(brief_info)
            except Exception as e:
                print(e)
                fail += 1
                print("Fail:",fail)
                # time.sleep(random.uniform(0.5,1.5))
                print("获取'{}'第{}页的简要信息...".format(name,i+1))
                link = link_base.format(self.nav[name],i+1)
                s = self.loadSession(name,fail)
                brief_info = self.getURL(s,link)
                # print(brief_info,sep='\n')
                # self.urls = self.urls + brief_info
                self.urls.extend(brief_info)
        save = self.urls
        save_csv = pd.DataFrame(save)
        save_csv.to_csv("./data/{}.csv".format(name),encoding="utf-8")
        print("{}的简要信息已保存到 {}.csv 中,共计{}条数据。".format(name,name,len(save)))


    # 爬取每个交易的详细信息
    def getDetail(self,s,link):
        # s = self.loadSession()
        aPage = s.get(link,proxies=proxies,headers=headers)
        soup = BeautifulSoup(aPage.text, "lxml")
        # soup = BeautifulSoup(open("高尔夫.html"), "lxml")
        # self.save_page("车主",aPage)
        # 获取标题所在a标签
        trans_info = {}
        # info_table = soup.select('table[class=v_table_1] td')
        info_detail = soup.find("div",class_="mb-5")
        # info_imgs = soup.select('.div_masterbox img')
        # # 交易编号
        # trans_info["tran_ID"] = info_table[3].string
        # # 商品单价
        # trans_info["price_us"] = info_table[5].get_text()
        # # 商家最后上线时间
        # trans_info["last_time"] = info_table[7].string
        # # 本单成交量
        # trans_info["sold"] = info_table[-5].string
        # 商品描述
        trans_info["content"] = info_detail.get_text().strip()
        # 附件
        # trans_info["media"] = []
        # for info_img in info_imgs:
        #     trans_info["media"].append(info_img['src'])

        # print(trans_info)
        return trans_info


# http://xxxxxxxxxs6qbnahsbvxbghsnqh4rj6whbyblqtnmetf7vell2fmxmad.onion/viewtopic.php?tid=39958

    # 爬取一个种类的所有详细信息
    def getDetails(self,name):
        # base_link = "http://xxxxxxxxxs6qbnahsbvxbghsnqh4rj6whbyblqtnmetf7vell2fmxmad.onion/"
        df = pd.read_csv("./data/{}.csv".format(name))
        uris = df["url"]
        max = len(uris)
        i = 0
        info_list = []
        fail=0
        for uri in uris:

            i += 1
            link = uri
            print(link)
            print("正在爬取'{}'第{}个交易...".format(name,i))
            try:
                s = self.loadSession(name,0)
                trans_dic = self.getDetail(s,link)
                info_list.append(trans_dic)
            except Exception as e:
                print(e)
                print("爬取交易时出错！！！")
                fail += 1
                print("{} Fail:".format(name),fail)
                s = self.loadSession(name,fail)
                trans_dic = self.getDetail(s,link)

                # trans_dic = {"tran_ID":link}
                info_list.append(trans_dic)
                continue
            # print(trans_dic)
        # print(info_list)
        save_csv = pd.DataFrame(info_list)
        save_csv.to_csv("./data/{}_detail.csv".format(name),encoding="utf-8")
        print("{}的详细信息已保存到 {}_detail.csv 中,共计{}条数据。".format(name,name,len(info_list)))
        return len(info_list)




    def run(self,name):
        # for i in range(5):
        #     print("请求第 %d 次Session" % int(i+1))
        #     self.saveSession(i+1)
        # self.saveSession(0)
        # s = self.loadSession()
        # self.getNav()
        # self.getMaxPage(name)
        # self.getURL("http://alibaba2kw6qoh6o.onion/shop/data?page=2")
        # self.getURLs()
        # self.getDetail("http://xxxxxxxxxs6qbnahsbvxbghsnqh4rj6whbyblqtnmetf7vell2fmxmad.onion/viewtopic.php?tid=21700")
        count = self.getDetails(name)
        # return count

from multiprocessing import Process, Lock

class MyProcess(Process):
    def __init__(self,category,lock):
        Process.__init__(self)
        self.category = category
        self.lock = lock
        self.count = 0
    def run(self):
        # self.lock.acquire()
        print('Pid: ' + str(self.pid) + " Process name:" + self.name + " 爬取的类别: " + self.category)
        dS = DarkSpider(proxies,headers,captcha,login)
        t = dS.run(self.category)
        # self.count += t
        # self.lock.release()




if __name__ == '__main__':

    # dS = DarkSpider(proxies,headers,captcha,login)
    # dS.run("工商")



    lock = Lock()
    # # #
    # # # cat = ["数据","服务","虚拟","实体","技术","其它","基础","影视","私拍","卡料"]
    # # cat = ["数据","教程","服务","CVV","影视","禁书","实物","求购","棋牌","菠菜","网贷","金融","工商","其他"]
    # cat = ["数据","影视","其他"]
    #
    cat = ["禁书","工商"]
    #
    proc_record = []
    for c in cat:
        # dS = DarkSpider(proxies,headers,captcha,login)
        # dS.run(c)
        # p = multiprocessing.Process(target=dS.run(), args=(c,))
        p = MyProcess(c,lock)
        p.daemon = True
        p.start()
        proc_record.append(p)
    for p in proc_record:
        p.join()
    # count = 0
    # for p in proc_record:
    #     count += p.count
    #
    # print("所有数据爬取完成！总共爬取了{}条数据！".format(count))




# # 打印当前IP
# r = s.get("http://api.ipify.org?format=json", proxies = proxies)
# print(r.text)


# # 切换ip
# os.system('brew services restart tor')
