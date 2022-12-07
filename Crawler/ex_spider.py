import requests
import os
from bs4 import BeautifulSoup
import pickle
import numpy
import pandas as pd

# 验证码
# http://xxxxxxxxxs6qbnahsbvxbghsnqh4rj6whbyblqtnmetf7vell2fmxmad.onion/entrance/code76.php
captcha = "http://xxxxxxxxxs6qbnahsbvxbghsnqh4rj6whbyblqtnmetf7vell2fmxmad.onion/entrance/code76.php"

# 登录界面
# http://xxxxxxxxxs6qbnahsbvxbghsnqh4rj6whbyblqtnmetf7vell2fmxmad.onion/entrance/logins.php
login = "http://xxxxxxxxxs6qbnahsbvxbghsnqh4rj6whbyblqtnmetf7vell2fmxmad.onion/entrance/logins.php"

base = "http://xxxxxxxxxs6qbnahsbvxbghsnqh4rj6whbyblqtnmetf7vell2fmxmad.onion/"

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
        code = s.get(self.captcha, headers=self.headers, proxies = self.proxies)

        with open('code.jpg', 'wb') as file:
            file.write(code.content)
            file.close

        cap = input("验证码：")
        data = {
        	"lgid": "598140",
        	"lgpass": "exchange666",
        	"sub_code": cap,
        	"lgsub": "进入系统",
        }

        index = s.post(login, headers=headers, data=data, proxies=proxies)
        self.save_page("index",index)

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
        soup = BeautifulSoup(open('index.html'), "lxml")
        table = soup.select('table[class=table_indexpost]')
        # print(table[0].a)
        for a in table[0].find_all('a'):
            category = a.get_text()
            link = a['href']
            # print(category)
            self.nav[category] = base+link
            # print(self.nav[category])

    def getMaxPage(self,name):
        try:
            self.category = name
            s = self.loadSession()
            url = self.nav[name]
            print("正在爬取页数...")
            cate = s.get(url,headers=headers,proxies=proxies)
            soup = BeautifulSoup(cate.text, "lxml")
            # 页码
            span = soup.select('span[class=button_page]')
            maxPage = int(span[-1].get_text().strip())
        except:
            print("发生错误，重新获取Session...")
            self.saveSession()
            s = self.loadSession()
            url = self.nav[name]
            print("正在爬取页数...")
            cate = s.get(url,headers=headers,proxies=proxies)
            soup = BeautifulSoup(cate.text, "lxml")
            # 页码
            span = soup.select('span[class=button_page]')
            maxPage = int(span[-1].get_text().strip())
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
    def getURL(self,link):
        s = self.loadSession()
        aPage = s.get(link,proxies=proxies,headers=headers)
        soup = BeautifulSoup(aPage.text, "lxml")
        # 获取标题所在a标签
        title_a = soup.select('div[class=navbar] div[class=length_500] .text_p_link')
        # print(title_a)
        info_list = []
        for a in title_a:
            # 字典必须定义在for里面
            trans_data = {}
            infoAll = a.parent.parent.parent
            # print(infoAll,sep='\n')
            # 每个交易的类别
            trans_data['category'] = self.category
            # 每个交易的ID
            trans_data['ID'] = infoAll.td.string
            # 每个交易的发布时间
            trans_data['post_time'] = infoAll.contents[1].string
            # 每个交易的发布人
            trans_data['OP'] = infoAll.contents[2].string
            # 每个交易的标题
            trans_data['title'] = infoAll.contents[3].string
            # 每个交易的比特币价值
            trans_data['price_bc'] = infoAll.contents[4].string
            # 每个交易的链接
            trans_data['url'] = a["href"]
            info_list.append(trans_data)
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
        soup = BeautifulSoup(aPage.text, "lxml")
        # soup = BeautifulSoup(open("高尔夫.html"), "lxml")
        # self.save_page("车主",aPage)
        # 获取标题所在a标签
        trans_info = {}
        info_table = soup.select('table[class=v_table_1] td')
        info_detail = soup.select('.div_masterbox')[0]
        info_imgs = soup.select('.div_masterbox img')
        # 交易编号
        trans_info["tran_ID"] = info_table[3].string
        # 商品单价
        trans_info["price_us"] = info_table[5].get_text()
        # 商家最后上线时间
        trans_info["last_time"] = info_table[7].string
        # 本单成交量
        trans_info["sold"] = info_table[-5].string
        # 商品描述
        trans_info["content"] = info_detail.get_text()
        # 附件
        trans_info["media"] = []
        for info_img in info_imgs:
            trans_info["media"].append(info_img['src'])

        # print(trans_info)
        return trans_info


# http://xxxxxxxxxs6qbnahsbvxbghsnqh4rj6whbyblqtnmetf7vell2fmxmad.onion/viewtopic.php?tid=39958

    # 爬取一个种类的所有详细信息
    def getDetails(self,name):
        base_link = "http://xxxxxxxxxs6qbnahsbvxbghsnqh4rj6whbyblqtnmetf7vell2fmxmad.onion/"
        df = pd.read_csv("./data/{}.csv".format(name))
        uris = df["url"]
        max = len(uris)
        i = 0
        info_list = []
        for uri in uris:
            i += 1
            link = base_link+uri
            print(link)
            print("正在爬取'{}'第{}个交易...".format(name,i))
            try:
                trans_dic = self.getDetail(link)
                info_list.append(trans_dic)
            except:
                print("爬取交易时出错！！！")
                trans_dic = {"tran_ID":link}
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
        # self.getNav()
        # self.getMaxPage(name)
        # self.getURLs()
        # self.getDetail("http://xxxxxxxxxs6qbnahsbvxbghsnqh4rj6whbyblqtnmetf7vell2fmxmad.onion/viewtopic.php?tid=21700")
        count = self.getDetails(name)
        return count

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
        self.count += t
        # self.lock.release()




if __name__ == '__main__':
    # dS = DarkSpider(proxies,headers,captcha,login)
    # dS.run("其它")
    lock = Lock()

    cat = ["数据","服务","虚拟","实体","技术","其它","基础","影视","私拍","卡料"]
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
    count = 0
    for p in proc_record:
        count += p.count

    print("所有数据爬取完成！总共爬取了{}条数据！".format(count))




# # 打印当前IP
# r = s.get("http://api.ipify.org?format=json", proxies = proxies)
# print(r.text)


# # 切换ip
# os.system('brew services restart tor')
