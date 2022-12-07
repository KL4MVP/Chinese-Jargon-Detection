import requests
import os
from bs4 import BeautifulSoup
import pickle
import numpy
import pandas as pd
import time
import re

# 验证码
# http://7zj4oshsyhokgus6fyk7pmdiubu4mkjpjjprjkvopnhnwylr522tymqd.onion/other/vcode4
captcha = "http://7zj4oshsyhokgus6fyk7pmdiubu4mkjpjjprjkvopnhnwylr522tymqd.onion/other/vcode4"

# 登录界面
# http://xxxxxxxxxs6qbnahsbvxbghsnqh4rj6whbyblqtnmetf7vell2fmxmad.onion/entrance/logins.php
login = "http://7zj4oshsyhokgus6fyk7pmdiubu4mkjpjjprjkvopnhnwylr522tymqd.onion/user/login"

base = "http://7zj4oshsyhokgus6fyk7pmdiubu4mkjpjjprjkvopnhnwylr522tymqd.onion"

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
        self.captcha = captcha
        self.login = login
        self.nav = {}
        self.maxPage = 0
        self.urls = []
        self.category = ""

    def saveSession(self):
        s = requests.Session()
        base_page = s.get(base, headers=self.headers, proxies = self.proxies)

        login_page = s.get(login,headers=headers, proxies = self.proxies)
        soup = BeautifulSoup(login_page.text,'lxml')
        hash = soup.select('input[name=hash]')[0]
        hash = hash['value']
        print(hash)

        code = s.get(self.captcha, headers=self.headers, proxies = self.proxies)
        with open('code.png', 'wb') as file:
            file.write(code.content)
            file.close

        cap = input("验证码：")
        data = {
        	"username": "598140",
        	"password": "exchange666",
        	"vcode": cap,
        	"hash": hash
        }

        index = s.post(login, headers=headers, data=data, proxies=proxies)
        # print(index.text)
        # self.save_page("index",index)

        default = s.get("http://7zj4oshsyhokgus6fyk7pmdiubu4mkjpjjprjkvopnhnwylr522tymqd.onion/default",headers=headers, proxies=proxies)
        # print(default.text)
        self.save_page("default",default)

        with open("session.pickle",'wb') as f:
            pickle.dump(s,f)
        print("Session保存成功。")

    def loadSession(self):
        if os.path.exists("session.pickle"):
            with open("session.pickle",'rb') as f:
                session = pickle.load(f)
            return session
        else:
            print("获取Session中...")
            self.saveSession()
            with open("session.pickle",'rb') as f:
                session = pickle.load(f)
            return session

    def getNav(self):
        soup = BeautifulSoup(open('default.html'), "lxml")
        table = soup.find_all("div",class_="row no-gutters")
        # print(table[-1].find_all('div',class_="title"))
        for div in table[-1].find_all('div',class_="title"):
            category = div.contents[1].get_text().strip()
            link = div.contents[3].a['href']
            # print(category)
            self.nav[category] = base+link
            # print(self.nav[category])

    def rec(self,s,link,count):
        try:
            next_page = s.get(link,headers=headers,proxies=proxies)
            soup = BeautifulSoup(next_page.text, "lxml")
            # 下一页
            a = soup.select('a[class=page-link]')[-1]
            link_next = a['href']
            count = self.rec(s,link_next,count)
            print("第{}页".format(count))
        except:
            print("出错啦。")
        count += 1
        print(link_next)
        # print("返回上一层")
        return count



    def getMaxPage(self,name):
        # try:
        self.category = name
        s = self.loadSession()
        # print(self.nav)
        url = self.nav[name]+"?mode=text"
        print("正在爬取'{}'的页数...".format(name))
        # count = 0
        # maxPage = self.rec(s,url,count=count)
        # self.maxPage = maxPage
        # print("ctmd:",maxPage)
        # return maxPage
        cate = s.get(url,headers=headers,proxies=proxies)
        # self.save_page("技术",cate)
        soup = BeautifulSoup(cate.text, "lxml")
        # 下一页
        a = soup.select('a[class=page-link]')
        link_next = a[-1]['href']
        self.urls.extend(self.getURL(soup))
        # print(link_next)
        while True:
            try:
                next_page = s.get(link_next,headers=headers,proxies=proxies)
                soup = BeautifulSoup(next_page.text, "lxml")
                # 下一页
                a = soup.select('a[class=page-link]')
                self.urls.extend(self.getURL(soup))
                print(link_next.split("/")[-1],"数据保存成功")
                test = a[8]
                link_next = a[-1]['href'].replace("&mode=img","&mode=text")

            except:
                break
        save = self.urls
        save_csv = pd.DataFrame(save)
        save_csv.to_csv("./data/{}.csv".format(name),encoding="utf-8")
        print("{}的简要信息已保存到 {}.csv 中,共计{}条数据。".format(name,name,len(save)))


    def save_page(self,name,file):
        f = open("{}.html".format(name), "wb")
        f.write(file.content)
        f.close()
        print("{}页面保存成功。".format(name))


    # 在每页获取交易链接
    def getURL(self,soup):
        # s = self.loadSession()
        # aPage = s.get(link,proxies=proxies,headers=headers)
        # soup = BeautifulSoup(aPage.text, "lxml")
        # soup = BeautifulSoup(open("技术.html"), "lxml")

        # 获取标题所在li标签
        title_li = soup.find_all("li",class_="mb-3 border-bottom pb-1")
        info_list = []
        for a in title_li:
            # 字典必须定义在for里面
            trans_data = {}
            # 每个交易的类别
            trans_data['category'] = self.category
            # 每个交易的发布时间
            trans_data['post_time'] = a.find("span",class_="text-muted small").get_text().strip()
            # 每个交易的标题
            trans_data['title'] = a.find("a",target="_blank").get_text()
            # 每个交易的比特币价值
            trans_data['price_us'] = a.find("span",class_="badge badge-pill badge-danger").get_text().strip("$")
            # 每个交易的链接
            trans_data['url'] = base+a.find("a",target="_blank")["href"]
            info_list.append(trans_data)
        # print(info_list)
        # print(len(info_list))
        return info_list


    # 获取一个种类的所有交易链接和信息
    def getURLs(self):
        name = self.category
        link_base = "{}&pagea={}#pagea"
        for i in range(self.maxPage):
            print("获取'{}'第{}页的简要信息...".format(name,i+1))
            link = link_base.format(self.nav[name],i+1)
            brief_info = self.getURL(link)
            # print(brief_info,sep='\n')
            # self.urls = self.urls + brief_info
            self.urls.extend(brief_info)
        save = self.urls
        save_csv = pd.DataFrame(save)
        save_csv.to_csv("./data/{}.csv".format(name),encoding="utf-8")
        print("{}的简要信息已保存到 {}.csv 中,共计{}条数据。".format(name,name,len(save)))


    # 爬取每个交易的详细信息
    def getDetail(self,link):
        s = self.loadSession()
        aPage = s.get(link,proxies=proxies,headers=headers)
        # print(aPage.text)
        soup = BeautifulSoup(aPage.text, "lxml")
        # soup = BeautifulSoup(open("数据.html"), "lxml")
        # self.save_page("股票",aPage)
        # 获取标题所在a标签
        trans_info = {}
        info_table = soup.find("div",class_="product-info")
        info_detail = soup.find("div",class_="product-content").contents
        info_imgs = soup.select('.product-content a')[1:]
        # print(type(info_detail))
        # print(info_imgs[1:])
        # 卖家店铺
        trans_info["OP"] = info_table.find("a",class_="btn btn-primary")['href']
        # 商品单价
        trans_info["price_bc"] = info_table.find("p",class_="product_price").get_text()
        # 商家最后上线时间
        trans_info["last_time"] = soup.find("span",class_="badge badge-success p-1").get_text()
        # 本单成交量
        trans_info["sold"] = info_table.find(text=re.compile("库存")).parent.parent.previous_sibling.previous_sibling.get_text()
        # 库存
        trans_info["store"] = info_table.find(text=re.compile("库存")).parent.parent.get_text()
        # 商品描述
        desc = ''.join((str(x) for x in info_detail))
        desc = re.sub(re.compile("<a.*</a>"),"",desc)
        trans_info["content"] = re.sub(re.compile("<style .*</div>",re.DOTALL),"",desc)



        # 附件
        # 我真nm是个天才，?:表示不算分组
        # p1 = re.compile('src="(.*?)"')
        # p2 = re.compile('href="(.*?)"')
        p3 = re.compile('(?:src|href)="(.*?)"')
        # p4 = re.compile('src="(.*?)"|href="(.*?)"')
        trans_info["media"] = re.findall(p3,str(info_imgs))
        trans_info["media"] = [base+x for x in trans_info["media"]]


        # print(trans_info)
        return trans_info


# http://xxxxxxxxxs6qbnahsbvxbghsnqh4rj6whbyblqtnmetf7vell2fmxmad.onion/viewtopic.php?tid=39958

    # 爬取一个种类的所有详细信息
    def getDetails(self,name):
        # base_link = "http://xxxxxxxxxs6qbnahsbvxbghsnqh4rj6whbyblqtnmetf7vell2fmxmad.onion/"
        df = pd.read_csv("./data/{}.csv".format(name))
        urls = df["url"]
        max = len(urls)
        i = 0
        info_list = []
        for link in urls:
            i += 1
            print(link)
            print("正在爬取'{}'第{}个交易...".format(name,i))
            try:
                # time.sleep(3)
                trans_dic = self.getDetail(link)
                info_list.append(trans_dic)
            except Exception as e:
                print(e)
                print("爬取交易时出错！！！")
                trans_dic = {"OP":link}
                info_list.append(trans_dic)
                continue
            # print(trans_dic)
        # print(info_list)
        save_csv = pd.DataFrame(info_list)
        save_csv.to_csv("./data/{}_detail.csv".format(name),encoding="utf-8")
        print("{}的详细信息已保存到 {}_detail.csv 中,共计{}条数据。".format(name,name,len(info_list)))
        return len(info_list)




    def run(self,name):
        # self.saveSession()
        # s = self.loadSession()
        # t1 = time.time()
        # self.getURL(name)
        # self.getNav()
        # self.getMaxPage(name)
        # t2 = time.time()
        # print(t2-t1)
        # self.getURLs()
        # self.getDetail("http://7zj4oshsyhokgus6fyk7pmdiubu4mkjpjjprjkvopnhnwylr522tymqd.onion/info/4865")
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
    # dS.run("数据")


    lock = Lock()
    # cat = ["担保私拍","洗车精洗","药品"]
    cat = ["四件套号卡","实物","担保私拍","洗车精洗","药品"]
    # cat = ["数据","查档定位","虚拟","服务","其它","四件套号卡","漏洞","实物","担保私拍","洗车精洗","药品","技术","站内充提"]
    # cat = ["数据","服务","虚拟","实体","技术","其它","基础","影视","私拍","卡料"]
    # proc_record = []
    # # 并行
    # for c in cat:
    #     # dS = DarkSpider(proxies,headers,captcha,login)
    #     # dS.run(c)
    #     # p = multiprocessing.Process(target=dS.run(), args=(c,))
    #     p = MyProcess(c,lock)
    #     p.daemon = True
    #     time.sleep(1)
    #     p.start()
    #     proc_record.append(p)
    # for p in proc_record:
    #     p.join()
    # 串行
    for c in cat:
        # dS = DarkSpider(proxies,headers,captcha,login)
        # dS.run(c)
        # p = multiprocessing.Process(target=dS.run(), args=(c,))
        p = MyProcess(c,lock)
        p.daemon = True
        # time.sleep(1)
        p.start()
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
