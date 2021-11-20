import tensorflow as tf
import os
import numpy as np
import pyprind
import pickle
from tokenPos import search
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import torch
import torch.nn.functional as F
import time


class CosineSimilarityTest(torch.nn.Module):
    def __init__(self):
        super(CosineSimilarityTest, self).__init__()

    def forward(self, x1, x2):
        x2 = x2.t()
        x = x1.mm(x2)

        x1_frobenius = x1.norm(dim=1).unsqueeze(0).t()
        x2_frobenins = x2.norm(dim=0).unsqueeze(0)
        x_frobenins = x1_frobenius.mm(x2_frobenins)

        final = x.mul(1/x_frobenins)
        return final


def coSim(vec1,vec2):
    num = vec1.dot(vec2.T)
    denom = np.linalg.norm(vec1) * np.linalg.norm(vec2)
    sim = num / denom
    return sim

def getRow(pos):
    return pos[0]

def getColumn(pos):
    return pos[1]

import numpy as np
from bert4keras.backend import keras
from bert4keras.models import build_transformer_model
from bert4keras.tokenizers import Tokenizer
from bert4keras.snippets import to_array
import jieba

config_path = './fine-tune5/bert_config.json'
checkpoint_path = './fine-tune5/bert_model.ckpt'
dict_path = './fine-tune5/vocab.txt'

tokenizer = Tokenizer(dict_path, do_lower_case=True, pre_tokenize=lambda s: jieba.cut(s, HMM=False))  # 建立分词器
model = build_transformer_model(config_path, checkpoint_path)  # 建立模型，加载权重




with open("./bert_final_emb.pickle","rb") as f:
    emb = pickle.load(f)

corpus = [line.split() for line in open("./seg.txt", 'r', encoding='utf-8').readlines()]

Keyword = {
  "毒品":["毒品", '丙酮', '飞行员', '迷幻药','二类', '烟油', '大嘛', '笑气', '四号', '医师', "兴奋剂", "摇头丸", "贩毒", "可卡因", "吗啡", "鸦片", "白粉", "镇静剂",'素', "罂粟", "吸毒者", "海洛因",'苯乙腈','蓖麻','神仙水','麻黄素','烟盒', "大麻", "冰毒",'冰','冻品','甲基苯丙胺','毒素','苯基','巴比妥钠','麻黄碱','安非他命','七氟烷','力月西','埋包','葉子','燃料','叶粉','冰票'],
  "赌博":["菠菜", "出千", "埋雷", '暗雷','扫雷', '类游戏','老牌', "猪蹄", "财神", "娱乐", "发牌", "资金盘",'时时彩', "百家乐", '六合彩', "中奖", "开奖", "发财", "投注", "澳门", "赢球", "博彩", "体育", "葡京", "彩票", "电玩", '龙虎',"棋牌", "赌", "冰球", "金花", "赌场", "赌注", "赌城", "太阳城", "赌博", "彩金",'地下','杀猪盘','合约','现金','飞艇','分分彩','开元','红包','期货','币圈','迪士尼','捕鱼','小蘑菇','体育彩票','赌场','足彩','豬盤','综合盘','出神',],
  "料":["料", "内料","CVV","包活", "外料", "轨道料", '卡料',"下料", "洗料",'刷料', "洗拦截料",'测活', "挂马", "刷货", "鹅场", "猫场",'外汇',"料站",'螃蟹','小丑','卖料','手输机','料主','写卡','盾','四要素','四件套','料子','四大行','盗刷','四件','鱼料','可过','精洗','原轨','原密','银行账号','布卡','美亚','跑分','裸号','写卡器','带磁','螺号','万事达','工农建','跳蹬'],
  "色情":['色情网站','动漫','导航','儿童','黄色',"约会",'引色流', "亚洲",'麻豆','柚木','幼女','幼幼','草榴','主播','情色','真人','小视频','韩国', "牲交", "偷窥", "欧美", "长腿", "肛交", "三级", "成人", "看片", "丝袜", "足浴", "偷拍", '下海',"调教", "骚", "阴毛",  "无码", "臀", "屁股", "性爱", "情欲", "巨乳", "吹箫", "美乳", "开档", "高潮", "熟女", "操", "啪啪", "偷情", "做爱", "出轨", "性", "少妇", "肥臀",'爱丽丝','黄网','门','萝莉','艳照门','换脸','色站','门事件','裸聊','乱伦','黄播','福利','狼友','呦呦','色粉',"站街",'出台','楼凤','福利姬','童车'],
  "黑客":['渗透','入侵','工具包','黑产','脱库','脱裤','伪基站','黑帽','编程','工程学','暗网','小白','黑客工具','社会','漏洞','木马','社工','逆向','钓鱼','爬虫','刷货','黑客技术','盗刷','攻击','社工库','攻防','明网','网赚','灰产','复制卡','网络安全','勒索','撞库','星天乐','黑灰产','养号','黑市','社群','建站','拿站','病毒','抓包','免杀','注入','挖矿','爆破','群发器','信息安全','米特尼克','提权','库','影网','反侦察','悬剑','红盟','参透','单兵','红黑','盗号','破解','扫号器','表网','域名','源代码','撸货','远控','骇客','肉鸡'],
  "枪支":['枪支','装备','军事','手枪','制造','警用','八件套','弹药','炸药','管制','武器','新型','枪支弹药','枪管','黑枪','简易','枪械','气枪','军迷','板球','扳机','秃鹰','掌心雷','骚本','季候风','粮','气狗','狗粮','雷管','冲锋枪','精仿','膛线','连发','黑火药','火工品','精度高','博莱塔','防弹','单警','缅北','季戊四醇','走私','供弹','旋风','笔枪','消音器','泰瑟','捷克','反扫枪'],
  "洗钱":['洗黑钱','洗钱',"水房", "声佬", "刷机佬", "接数佬", "卡佬", "车手",'洗车','洗衣机','洗币','洗白','洗款','反洗钱','代洗','帮洗','钱桶','黑钱','黑款'],
  "羊毛":['羊毛','出租','返佣','跑分','交友粉',"红锁","黑刀",'黑号','稳赚','暴利','网赚','韭菜','接码','点卡','刷单','薅羊毛','苹果推信','蓝号','套现','卡发','洋韭菜','撸货','刷货','鱼','耗','耗羊毛','毛料','裤','韭菜苗'],
  "黑产":['亡单','沙手','残单','虚拟卡','引流','出粉','接码','刷货','乌鸦','黑产','灰产','白产','黑料','黑卡','网赚','黑金','黑货','盗刷','接黑','防喝茶','黑五产','洗黑钱','深区','菠菜','包活'],
  "诈骗":['狗推','诈骗','敲诈','骗术','电诈','网赚','躺赚','骗局','裸聊','盗刷','欺诈','骗色','网诈','勒索','套路','网骗','钓鱼','骗保','纯诈','鸡托','搅诈','骗炮'],
  "个人信息":['手机号','个人信息','资料','裸号','数据库','账号密码','联系方式','脱库','微信号','宝妈','个人资料','个人资料','个码','裸贷','身份证','户籍','料子','人裙','人轨']
}






words = [line.split() for line in open("./dupin_filter.txt", 'r', encoding='utf-8').readlines()]

KeyW = Keyword["个人信息"]
KeyW.insert(0,'[CLS]')
KeyW.insert(len(KeyW),'[SEP]')
print(KeyW)

token_ids, segment_ids = tokenizer.encode(KeyW,flag=True)
KeyV = model.predict([np.array([token_ids]), np.array([segment_ids])])

print(type(KeyV))
print(KeyV.shape)

pbar = pyprind.ProgBar(len(words),title='进度展示',monitor=True)

group_vector_output = np.array([]).reshape(0, 768)

t1 = time.time()

for word in words:
    #print(word)
    sen = corpus[int(word[2])]
    # print(sen)
    senten = emb[int(word[2])]
    vec = senten[sen.index(word[0])+1]
    # print(type(senten))
    #print(vec.shape)
    #print(vec)
    group_vector_output = np.vstack([group_vector_output, vec])
    pbar.update()
#print(group_vector_output)
#print(group_vector_output.shape)


'''
t1 = time.time()
word = "毒品"
print(word)
# sen = corpus[int(word[2])]
sen = corpus[5778]

print(sen)
# senten = emb[int(word[2])]
senten = emb[5778]
# vec = senten[sen.index(word[0])]
vec = senten[sen.index(word)]
'''

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
#x1 = torch.randn(5000000, 256).to(device)
#x2 = torch.randn(24, 256).to(device)
x1 = torch.from_numpy(group_vector_output).float().to(device)
#x1.to(device)
x2 = torch.from_numpy(KeyV[0]).float().to(device)
print(x2.size())


t2 = time.time()
print("加载时间为：{}".format(t2 - t1))

start_time = time.time()
simmodel = CosineSimilarityTest().to(device)

# 同时需要多卡计算时需要
# model = torch.nn.DataParallel(model)

final_value = simmodel(x1, x2)
#print(final_value)
print(final_value.size())

sims = torch.mean(final_value,1)
#print(sims)
print(sims.size())
#similarities = sims.numpy()
# 输出排序并输出topk的输出
#value, indec = torch.topk(final_value, 3, dim=0, largest=True, sorted=True)
#print(value)

end_time = time.time()
print("消耗时间为：{}".format(end_time - start_time))


with open("./CANDIDATE/GRCANDIDATE.txt","w") as f:
    for word,sim in zip(words,sims):
        f.write(word[0]+" ")
        f.write(str(sim.item()))
        f.write("\n")
