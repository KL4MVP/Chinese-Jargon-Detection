import requests
import os
from bs4 import BeautifulSoup
import pickle
import numpy
import pandas as pd
import time
import random



# 登录界面
# http://xxxxxxxxxs6qbnahsbvxbghsnqh4rj6whbyblqtnmetf7vell2fmxmad.onion/entrance/logins.php

login1 = "http://sfdu2jstlnp7whqlzpojopr5jxehxz4dveqfl67v6mfrwoj3nq6cnrad.onion/site/loginp?invita="
login2 = "http://sfdu2jstlnp7whqlzpojopr5jxehxz4dveqfl67v6mfrwoj3nq6cnrad.onion?invita="

base = "http://sfdu2jstlnp7whqlzpojopr5jxehxz4dveqfl67v6mfrwoj3nq6cnrad.onion"

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
    def __init__(self,proxies,headers,login):
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

        login_page = s.get(login2, headers=headers,proxies=proxies)
        # print(login_page.text)
        login_page = s.get(login1, headers=headers,proxies=proxies)
        # print(login_page.text)
        self.save_page("login",login_page)

        soup = BeautifulSoup(login_page.text,"lxml")
        # soup = BeautifulSoup(open("login.html"),"lxml")

        csrf = soup.find("input",type="hidden")["value"]
        captcha_href = soup.find("img",id="loginform-verifycode-image")["src"]
        self.captcha = base + captcha_href
        print(csrf)
        print(captcha_href)
        code = s.get(self.captcha, headers=self.headers, proxies = self.proxies)

        with open('code.jpg', 'wb') as file:
            file.write(code.content)
            file.close

        cap = input("验证码：")
        data = {
        "_csrf-f":csrf,
        "LoginForm[username]":"598102",
        "LoginForm[password]":"exchange666",
        "LoginForm[verifyCode]":cap
        }

        index = s.post(login1, headers=headers,proxies=proxies,data=data)
        self.save_page("index",index)

        with open("{}.pickle".format(name),'wb') as f:
            pickle.dump(s,f)
        print("Session保存成功。")

    def loadSession(self,name):
        with open("{}.pickle".format(name),'rb') as f:
            session = pickle.load(f)
        return session


    def getNav(self):
        soup = BeautifulSoup(open('index.html'), "lxml")
        table = soup.find("div",class_="main-menu")
        names = table.select("li.static")
        # print(names,len(names))
        for name in names:
            category = name.get_text().strip()
            link = name.a['href']
            print(category)
            self.nav[category] = base+link
            print(self.nav[category])

# http://sfdu2jstlnp7whqlzpojopr5jxehxz4dveqfl67v6mfrwoj3nq6cnrad.onion/site/index?goods_cate_id=3&page=19&per-page=18
    def getMaxPage(self,name):
        # try:
        self.category = name
        s = self.loadSession()
        # print(self.nav)
        url = self.nav[name]
        print("正在爬取'{}'的页数...".format(name))
        # count = 0
        # maxPage = self.rec(s,url,count=count)
        # self.maxPage = maxPage
        # print("ctmd:",maxPage)
        # return maxPage
        cate = s.get(url,headers=headers,proxies=proxies)
        # self.save_page("服务",cate)
        soup = BeautifulSoup(cate.text, "lxml")
        # print(cate.text)
        # 下一页
        link_next = base + soup.find("li",class_="next").a["href"]
        self.urls.extend(self.getURL(soup))
        print(link_next)
        while True:
            try:
                next_page = s.get(link_next,headers=headers,proxies=proxies)
                soup = BeautifulSoup(next_page.text, "lxml")
                self.urls.extend(self.getURL(soup))
                print(link_next.split("/")[-1],"数据保存成功")
                link_next = base + soup.find("li",class_="next").a["href"]
                time.sleep(random.uniform(1.5,5))

            except Exception as e:
                print(e)
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
        # soup = BeautifulSoup(open("服务.html"), "lxml")

        # 获取标题所在li标签
        title_li = soup.find_all("div",class_="product-description text-center")
        info_list = []
        for a in title_li:
            # 字典必须定义在for里面
            trans_data = {}
            # 每个交易的类别
            trans_data['category'] = self.category
            # 每个交易的标题
            trans_data['title'] = a.find("a").get_text()
            # 每个交易的美元价值
            trans_data['price_us'] = a.find("span",class_="regular-price").get_text().strip("$")
            # 每个交易的链接
            trans_data['url'] = base+a.find("a")["href"]
            info_list.append(trans_data)
        # print(info_list)
        # print(len(info_list))
        return info_list




    # 爬取每个交易的详细信息
    def getDetail(self,link,name):
        s = self.loadSession(name)
        aPage = s.get(link,proxies=proxies,headers=headers)
        soup = BeautifulSoup(aPage.text, "lxml")
        # soup = BeautifulSoup(open("伊朗特工.html"), "lxml")
        # self.save_page("伊朗特工",aPage)
        # 获取标题所在a标签
        trans_info = {}
        info_table = soup.find("form",id="goodsorderid")
        info_detail = soup.find("div",class_="tab-content")
        info_imgs = soup.select('img')
        # print(info_imgs)
        # 本单成交量
        trans_info["sold"] = info_table.find("a").get_text()
        # 库存
        trans_info["store"] = info_table.find("div","availability").get_text().strip()
        # 商品更新时间
        trans_info['post_time'] = info_detail.select("span")[-1].get_text()
        # 信用
        trans_info['credibility'] = info_detail.select("span")[-2].get_text()
        # 卖家
        trans_info['seller'] = info_detail.select("span")[-3].get_text()
        # 商品描述
        trans_info["content"] = info_detail.select("div #tab_one")[-1].get_text().strip()
        # 附件
        trans_info["media"] = []
        for info_img in info_imgs:
            trans_info["media"].append(base+info_img['src'])

        # print(trans_info)

        return trans_info


# http://xxxxxxxxxs6qbnahsbvxbghsnqh4rj6whbyblqtnmetf7vell2fmxmad.onion/viewtopic.php?tid=39958

    # 爬取一个种类的所有详细信息
    def getDetails(self,name):
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
                trans_dic = self.getDetail(link,name)
                info_list.append(trans_dic)
                time.sleep(random.uniform(3,5))
            except Exception as e:
                print(e)
                print("爬取交易时出错！！！")
                trans_dic = {"sold":link}
                info_list.append(trans_dic)
                time.sleep(random.uniform(3,5))
                continue
            # print(trans_dic)
        # print(info_list)
        save_csv = pd.DataFrame(info_list)
        save_csv.to_csv("./data/{}_detail.csv".format(name),encoding="utf-8")
        print("{}的详细信息已保存到 {}_detail.csv 中,共计{}条数据。".format(name,name,len(info_list)))
        return len(info_list)

    def getDetailsFailed(self,name):
        df = pd.read_csv("./data/{}_fulldetail.csv".format(name))
        for index, row in df.iterrows():
            if len(row["sold"]) > 10:
                link = row["sold"]
                print(link)
        # print(df)
                print("正在爬取'{}'第{}个交易...".format(name,index))
                try:
                    trans_dic = self.getDetail(link,name)
                    # df.loc[index,:] = [index,trans_dic['sold'],trans_dic['store'],trans_dic['post_time'],trans_dic['credibility'],trans_dic['seller'],trans_dic['content'],trans_dic['media']]
                    df.loc[index,:] = trans_dic

                    print(df.loc[index,:])
                    time.sleep(random.uniform(3,5))
                except Exception as e:
                    print(e)
                    print("爬取交易时出错！！！")
                    time.sleep(random.uniform(3,5))
                    continue

        # print(df)
        df.to_csv("./data/{}_fulldetail1.csv".format(name),encoding="utf-8")
        print("{}的详细信息已保存到 {}_fulldetail1.csv 中。".format(name,name))




    def run(self,name):
        self.saveSession(name)
        self.getNav()

        # s = self.loadSession()

        # self.getMaxPage(name)
        # self.getDetail("http://sfdu2jstlnp7whqlzpojopr5jxehxz4dveqfl67v6mfrwoj3nq6cnrad.onion/goods/info?id=19268",name)
        # self.getURL("test")
        # self.getURLs()
        # self.getDetail("http://xxxxxxxxxs6qbnahsbvxbghsnqh4rj6whbyblqtnmetf7vell2fmxmad.onion/viewtopic.php?tid=21700")
        # count = self.getDetails(name)
        self.getDetailsFailed(name)
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
        dS = DarkSpider(proxies,headers,login1)
        t = dS.run(self.category)
        # self.count += t
        # self.lock.release()




if __name__ == '__main__':
    dS = DarkSpider(proxies,headers,login1)
    dS.run("数据")



    # lock = Lock()
    # # cat = ["数据","服务","虚拟","实体","技术","其它","基础","影视","私拍","卡料"]
    # # cat = ["数据","教程","虚拟","服务","cvv","实物","棋牌","影视","博彩","网贷","金融","工商"]
    # cat = ["数据","教程","虚拟","服务","cvv"]
    #
    # proc_record = []
    # for c in cat:
    #     # dS = DarkSpider(proxies,headers,captcha,login)
    #     # dS.run(c)
    #     # p = multiprocessing.Process(target=dS.run(), args=(c,))
    #     p = MyProcess(c,lock)
    #     p.daemon = True
    #     p.start()
    #     proc_record.append(p)
    # for p in proc_record:
    #     p.join()




    # cat = ["网贷","金融","工商"]
    # proc_record = []
    # for c in cat:
    #     # dS = DarkSpider(proxies,headers,captcha,login)
    #     # dS.run(c)
    #     # p = multiprocessing.Process(target=dS.run(), args=(c,))
    #     p = MyProcess(c,lock)
    #     p.daemon = True
    #     p.start()
    #     p.join()




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
