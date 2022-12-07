import requests
import os
from bs4 import BeautifulSoup
import pickle
import numpy
import pandas as pd
import re
import time
import random

# 验证码
# http://xxxxxxxxxs6qbnahsbvxbghsnqh4rj6whbyblqtnmetf7vell2fmxmad.onion/entrance/code76.php
captcha = ""

# 登录界面
# http://xxxxxxxxxs6qbnahsbvxbghsnqh4rj6whbyblqtnmetf7vell2fmxmad.onion/entrance/logins.php
login = "http://lfwpmgou2lz3jnt7mg3gorzkfnhnhgumbijn4ubossgs3wzsxkg6gvyd.onion/member.php?mod=logging&action=login&loginsubmit=yes&frommessage=&loginhash={}&inajax=1"
login1 = "http://lfwpmgou2lz3jnt7mg3gorzkfnhnhgumbijn4ubossgs3wzsxkg6gvyd.onion/forum-37-1.html"
login2 = "http://lfwpmgou2lz3jnt7mg3gorzkfnhnhgumbijn4ubossgs3wzsxkg6gvyd.onion/member.php?mod=logging&action=login&infloat=yes&frommessage=&inajax=1&ajaxtarget=messagelogin"
login3 = "http://lfwpmgou2lz3jnt7mg3gorzkfnhnhgumbijn4ubossgs3wzsxkg6gvyd.onion/misc.php?mod=seccode&action=update&idhash={}&modid=member::logging"

base = "http://lfwpmgou2lz3jnt7mg3gorzkfnhnhgumbijn4ubossgs3wzsxkg6gvyd.onion/"

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
    def __init__(self,proxies,headers,captcha):
        self.proxies = proxies
        self.headers = headers
        self.captcha = captcha
        self.login = ""
        self.nav = {}
        self.maxPage = 0
        self.urls = []
        self.category = ""


    def saveSession(self,name):
        s = requests.Session()

        login_info2 = s.get(login2, headers=headers, proxies=proxies)
        # self.save_page("login_info2",login_info2)

        soup = BeautifulSoup(login_info2.text,'lxml')
        pattern1 = 'seccode_(.*)"'
        pattern2 = 'loginhash=(.*?)"'
        res1 = re.findall(re.compile(pattern1),soup.prettify())
        res2 = re.findall(re.compile(pattern2),soup.prettify())
        seccodehash = res1[0]
        loginhash = res2[0]

        print("seccodehash:",seccodehash)
        print("loginhash:",loginhash)

        login_info3 = s.get(login3.format(seccodehash), headers=headers, proxies=proxies)
        # print("3:",s.cookies)
        # self.save_page("login_info3",login_info3)
        soup = BeautifulSoup(login_info3.text,'lxml')
        imgs = soup.findAll("img",class_="vm")
        link = imgs[-1]["src"]
        captcha_link = base + link
        # print(captcha_link)
        headers["Referer"] = login1
        code = s.get(captcha_link, headers=headers, proxies=proxies)

        with open('code.png', 'wb') as file:
            file.write(code.content)
            file.close

        login_info1 = s.get(login1, headers=headers, proxies=proxies)
        # self.save_page("login_info1",login_info1)
        soup = BeautifulSoup(login_info1.text,"lxml")

        # soup = BeautifulSoup(open("login_info1.html"),"lxml")
        # print(soup.prettify())

        info = soup.find("input",attrs={"name":"formhash"})
        formhash = info['value']
        print("formhash:",formhash)



        cap = input("验证码：")
        data = {
        "formhash":formhash,
        "referer":login1,
        "loginfield":"username",
        "username":"598140",
        "password":"exchange666",
        "answer":"",
        "seccodehash":seccodehash,
        "seccodemodid":"member::logging",
        "seccodeverify":cap
        }

        login_link = login.format(loginhash)
        # index = s.get(base, headers=headers, proxies=proxies)
        index = s.post(login_link, headers=headers, data=data, proxies=proxies)
        print(index.text)


        with open("{}.pickle".format(name),'wb') as f:
            pickle.dump(s,f)
        print("Session保存成功。")

    def loadSession(self,name):
        self.category = name
        with open("{}.pickle".format(name),'rb') as f:
            session = pickle.load(f)
        return session
    # def loadSession(self):
    #     if os.path.exists("session.pickle"):
    #         with open("session.pickle",'rb') as f:
    #             session = pickle.load(f)
    #         return session
    #     else:
    #         print("获取Session中...")
    #         self.saveSession()
    #         with open("session.pickle",'rb') as f:
    #             session = pickle.load(f)
    #         return session

    def getNav(self):
        soup = BeautifulSoup(open('index.html'), "lxml")
        table = soup.select('div#category_1 table.fl_tb td dt a')
        # print(table)
        for a in table:
            category = a.get_text()
            link = a['href']
            print(category)
            self.nav[category] = base+link
            print(self.nav[category])

    def getMaxPage(self,name):
        try:
            self.category = name
            s = self.loadSession()
            url = self.nav[name]
            print("正在爬取页数...")
            cate = s.get(url,headers=headers,proxies=proxies)
            soup = BeautifulSoup(cate.text, "lxml")
            # 页码
            a = soup.select('a[class=last]')
            maxPage = int(a[-1].get_text().strip("."))
        except:
            print("发生错误，重新获取Session...")
            self.saveSession()
            s = self.loadSession()
            url = self.nav[name]
            print("正在爬取页数...")
            cate = s.get(url,headers=headers,proxies=proxies)
            soup = BeautifulSoup(cate.text, "lxml")
            # 页码
            a = soup.select('a[class=last]')
            maxPage = int(a[-1].get_text().strip("."))
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
        # self.save_page("数据",aPage)
        soup = BeautifulSoup(aPage.text, "lxml")
        # soup = BeautifulSoup(open("数据.html"), "lxml")

        # 获取标题所在a标签
        title_a = soup.findAll("tbody",id=re.compile("normalthread_*"))
        # print(len(title_a))
        info_list = []
        for a in title_a:
            # 字典必须定义在for里面
            try:
                trans_data = {}
                OP_info = a.select("cite a")[0]
                content_info = a.find("a",class_="s xst")
                view_info = a.find("td",class_="num")
                # 每个交易的类别
                trans_data['category'] = self.category
                # 每个交易的发布人
                trans_data['OP'] = OP_info.get_text()
                # 每个交易的发布人链接
                trans_data['OP_link'] = base + OP_info['href']
                # 每个交易的标题
                trans_data['title'] = content_info.get_text()
                # 每个交易的链接
                trans_data['url'] = base + content_info["href"]
                # 每个交易的回复数
                trans_data['reply'] = view_info.a.get_text()
                # 每个交易的查看量
                trans_data['view'] = view_info.em.get_text()
                info_list.append(trans_data)
            except:
                trans_data = {}
                OP_info = a.select("cite")[0]
                content_info = a.find("a",class_="s xst")
                view_info = a.find("td",class_="num")
                # 每个交易的类别
                trans_data['category'] = self.category
                # 每个交易的发布人
                trans_data['OP'] = OP_info.get_text()
                # 每个交易的发布人链接
                trans_data['OP_link'] = ""
                # 每个交易的标题
                trans_data['title'] = content_info.get_text()
                # 每个交易的链接
                trans_data['url'] = base + content_info["href"]
                # 每个交易的回复数
                trans_data['reply'] = view_info.a.get_text()
                # 每个交易的查看量
                trans_data['view'] = view_info.em.get_text()
                info_list.append(trans_data)
            # print(trans_data)
        return info_list

# http://lfwpmgou2lz3jnt7mg3gorzkfnhnhgumbijn4ubossgs3wzsxkg6gvyd.onion/forum-2-1.html
# http://lfwpmgou2lz3jnt7mg3gorzkfnhnhgumbijn4ubossgs3wzsxkg6gvyd.onion/forum-2-3.html
    # 获取一个种类的所有交易链接和信息
    def getURLs(self):
        name = self.category
        link_base = self.nav[name].split("/")[-1][0:-6]
        # print(link_base)
        for i in range(self.maxPage):
            print("获取'{}'第{}页的简要信息...".format(name,i+1))
            link = base+link_base+"{}.html".format(i+1)
            brief_info = self.getURL(link)
            # print(brief_info,sep='\n')
            # self.urls = self.urls + brief_info
            self.urls.extend(brief_info)
        save = self.urls
        save_csv = pd.DataFrame(save)
        save_csv.to_csv("./data/{}.csv".format(name),encoding="utf-8")
        print("{}的简要信息已保存到 {}.csv 中,共计{}条数据。".format(name,name,len(save)))


    # 爬取每个交易的详细信息
    def getDetail(self,link,name):
        s = self.loadSession(name)
        aPage = s.get(link,proxies=proxies,headers=headers)
        soup = BeautifulSoup(aPage.text, "lxml")
        # soup = BeautifulSoup(open("彩票.html"), "lxml")
        # print(soup.prettify())
        # self.save_page("网贷",aPage)
        # 获取标题所在a标签
        trans_info = {}
        info_table = soup.find("td",id=re.compile("postmessage_.*?"))
        # info_detail = soup.select('.div_masterbox')[0]
        # info_imgs = soup.find_all("img")

        info_imgs = info_table.find_all("img",file=re.compile(".*"))
        info_imgs2 = info_table.find_all("img",src=re.compile(".*"))
        # 交易发布时间
        trans_info["post_time"] = soup.find("em",id=re.compile("authorposton.*?")).get_text()
        if info_table.find("span",class_="price-real"):
            # 商品单价
            trans_info["price_us"] = info_table.find("span",class_="price-real").i.get_text()
            # 本单成交量
            trans_info["sold"] = info_table.find("span",class_="count-rest").get_text()
            # 库存
            trans_info["store"] = info_table.find("span",class_="count-take").get_text()
        else:
            # 商品单价
            trans_info["price_us"] = ""
            # 本单成交量
            trans_info["sold"] = ""
            # 库存
            trans_info["store"] = ""
        # 商品描述
        trans_info["content"] = info_table.get_text()
        # 附件
        trans_info["media"] = []
        for info_img in info_imgs:
            trans_info["media"].append(info_img['file'])
        for info_img in info_imgs2:
            trans_info["media"].append(info_img['src'])

        # print(len(trans_info["media"]))
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
        for url in urls:
            i += 1
            link = url
            print(link)
            print("正在爬取'{}'第{}个交易...".format(name,i))
            try:
                trans_dic = self.getDetail(link,name)
                info_list.append(trans_dic)
                time.sleep(random.uniform(1,2))
            except Exception as e:
                print(e)
                print("爬取交易时出错！！！")
                trans_dic = {"post_time":link}
                info_list.append(trans_dic)
                time.sleep(random.uniform(1,2))
                continue
            # print(trans_dic)
        # print(info_list)
        save_csv = pd.DataFrame(info_list)
        save_csv.to_csv("./data/{}_detail.csv".format(name),encoding="utf-8")
        print("{}的详细信息已保存到 {}_detail.csv 中,共计{}条数据。".format(name,name,len(info_list)))
        return len(info_list)




    def run(self,name):
        # self.saveSession(name)
        # s = self.loadSession()
        # self.getNav()
        # self.getMaxPage(name)
        # self.getURL("http://lfwpmgou2lz3jnt7mg3gorzkfnhnhgumbijn4ubossgs3wzsxkg6gvyd.onion/forum-2-1.html")
        # self.getURLs()
        # self.getDetail("http://lfwpmgou2lz3jnt7mg3gorzkfnhnhgumbijn4ubossgs3wzsxkg6gvyd.onion/thread-70598-1-1.html")
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
        dS = DarkSpider(proxies,headers,captcha)
        t = dS.run(self.category)
        # self.count += t
        # self.lock.release()




if __name__ == '__main__':
    dS = DarkSpider(proxies,headers,captcha)
    dS.run("其它黑灰产业")

    # lock = Lock()
    # #
    # # # cat = ["数据资料","卡料信息","器械药品","关系服务","雇佣求职区","身份护照","色情成人","其它黑灰产业"]
    # cat = ["数据资料","卡料信息","关系服务","雇佣求职区","色情成人"]
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
    #     # time.sleep(1)
    # for p in proc_record:
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
