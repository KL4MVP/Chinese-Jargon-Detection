import requests
import os
from bs4 import BeautifulSoup
import pickle
import numpy
import pandas as pd
import re

# 验证码
# http://xxxxxxxxxs6qbnahsbvxbghsnqh4rj6whbyblqtnmetf7vell2fmxmad.onion/entrance/code76.php
captcha = "http://c2p3hg35jalss7b2a6hkmhzflgevkonqt7g6jze62ro2g4h4wmzwobid.onion/jcaptcha.jpg"

# 登录界面
# http://xxxxxxxxxs6qbnahsbvxbghsnqh4rj6whbyblqtnmetf7vell2fmxmad.onion/entrance/logins.php
login = "http://c2p3hg35jalss7b2a6hkmhzflgevkonqt7g6jze62ro2g4h4wmzwobid.onion/login"

product = "http://c2p3hg35jalss7b2a6hkmhzflgevkonqt7g6jze62ro2g4h4wmzwobid.onion/product"

base = "http://c2p3hg35jalss7b2a6hkmhzflgevkonqt7g6jze62ro2g4h4wmzwobid.onion"

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
        "username":"598140",
        "password":"exchange666",
        "captcha":cap
        }

        index = s.post(login, headers=headers, data=data, proxies=proxies)
        product_pege = s.get(product, headers=headers, proxies=proxies)
        self.save_page("product_pege",product_pege)

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
        soup = BeautifulSoup(open('product_pege.html'), "lxml")
        table = soup.find("div",class_="filter-item-wrapper col-md-11")
        # print(table[0].a)
        for a in table.find_all('a')[1:]:
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
            pages = soup.find("div",class_="laypage-main")
            span = pages.select('a')
            maxPage = int(span[-2].get_text().strip())
        except Exception as e:
            print(e)
            maxPage = 1
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
        title_a = soup.select("tbody tr")[:-1]
        # print(title_a,len(title_a))
        info_list = []
        for a in title_a:
            # 字典必须定义在for里面
            trans_data = {}
            infoAll = a.select("td")
            # print(infoAll,sep='\n')
            # 每个交易的类别
            trans_data['category'] = self.category
            # 每个交易的标题
            trans_data['title'] = infoAll[0].get_text()
            # 每个交易的浏览量
            trans_data['views'] = infoAll[2].get_text()
            # 每个交易的发布时间
            trans_data['post_time'] = infoAll[3].get_text()
            # 每个交易的信誉
            trans_data['credibility'] = infoAll[4].get_text()
            # 每个交易的比特币价值
            trans_data['price_us'] = infoAll[5].get_text()
            # 每个交易的链接
            trans_data['url'] = base + infoAll[0].a["href"]
            info_list.append(trans_data)
        # print(info_list)
        return info_list


    # 获取一个种类的所有交易链接和信息
    def getURLs(self):
        name = self.category
        link_base = "{}/page/{}"
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
        # soup = BeautifulSoup(open("黑客.html"), "lxml")
        # print(soup.prettify())
        pattern = "img\[(.*?)\]"
        info_imgs = re.findall(re.compile(pattern),soup.prettify())
        # self.save_page("淘宝",aPage)
        # 获取标题所在a标签
        trans_info = {}
        info_OP = soup.find("div",class_="pubds-1")
        info_detail = soup.find("div",class_="detail-body photos")

        # 卖家店铺
        trans_info["OP"] = info_OP.select("p")[0].get_text()
        # 卖家昵称
        trans_info["nickname"] = info_OP.select("p")[1].get_text()
        # 卖家店铺链接
        trans_info["OP_link"] = base + info_OP.find("a")["href"]
        # 商品描述
        content = info_detail.get_text()
        trans_info["content"] = re.sub(re.compile(pattern),"",content)
        # 附件
        trans_info["media"] = []
        for info_img in info_imgs:
            trans_info["media"].append(base + info_img)

        # print(trans_info)
        return trans_info


# http://xxxxxxxxxs6qbnahsbvxbghsnqh4rj6whbyblqtnmetf7vell2fmxmad.onion/viewtopic.php?tid=39958

    # 爬取一个种类的所有详细信息
    def getDetails(self,name):
        df = pd.read_csv("./data/{}.csv".format(name))
        uris = df["url"]
        max = len(uris)
        i = 0
        info_list = []
        for uri in uris:
            i += 1
            link = uri
            print(link)
            print("正在爬取'{}'第{}个交易...".format(name,i))
            try:
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
        # self.getNav()
        # self.getMaxPage(name)
        # self.getURL("http://c2p3hg35jalss7b2a6hkmhzflgevkonqt7g6jze62ro2g4h4wmzwobid.onion/product/eaa846e312434950923a55a50a83b74e")
        # self.getURLs()
        # self.getDetail("http://c2p3hg35jalss7b2a6hkmhzflgevkonqt7g6jze62ro2g4h4wmzwobid.onion/product/detail/7e8925511d1d4d0da94898a630920e30")
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
    # dS.run("影视音像")



    lock = Lock()

    # cat = ["数据资源","影视音像","虚拟物品","私人专拍","服务业务","技术技能","实体物品","卡料CVV","其他类别"]
    cat = ["数据资源","虚拟物品","私人专拍","服务业务","技术技能","实体物品","卡料CVV","其他类别"]
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
