# -*- coding: utf-8 -*-
"""
Created on Wed Aug 29 22:27:40 2018

@author: ecupl
"""

###################决策树ID3算法##################
'''1、了解算法ID3——信息增益'''
import numpy as np
'''计算分类别信息熵'''
b = 128+60+64+64+64+132+64+32+32      #购买
nb = 64+64+64+128+64                  #未购买
E_cate = -((b/(b+nb))*np.log2(b/(b+nb)) + (nb/(b+nb))*np.log2(nb/(b+nb)))   #分类信息熵
'''计算子节点信息熵'''
y = 64+64+128+64+64     #年轻类
yb = 64+64                  #年轻购买
ynb = 64+64+128             #年轻不购买
E_y = -((yb/(yb+ynb))*np.log2(yb/(yb+ynb)) + (ynb/(yb+ynb))*np.log2(ynb/(yb+ynb)))
e = 128+64+32+32        #中年类
eb = 128+64+32+32           #中年购买
E_e = -(eb/(eb+enb))*np.log2(eb/(eb+enb))
o = 60+64+64+132+64     #老年类
ob = 60+64+133              #年轻购买
onb = 64+63                 #年轻不购买
E_o = -((ob/(ob+onb))*np.log2(ob/(ob+onb)) + (onb/(ob+onb))*np.log2(onb/(ob+onb)))
'''计算信息增益'''
Py = y/(y+e+o)
Pe = e/(y+e+o)
Po = o/(y+e+o)
G_age = E_cate - (Py*E_y + Pe*E_e + Po*E_o)
'''G_age=0.2666969558634843'''

'''ID3算法实现'''
import numpy as np
import math, copy, pickle

'''定义类'''
class ID3Tree(object):
    '''1、初始化'''
    def __init__(self):         #构造方法
        self.tree={}            #生成树
        self.dataset=[]         #数据集
        self.labels=[]          #标签集
        
    '''2、数据导入函数'''
    def loadDataSet(self,path,labels):
        datalist=[]
        with open(path,"r") as f:          #二进制形式读取文件
            content=f.read()
        rows = content.splitlines()     #分割文本，按行转换为一维表
        datalist=[row.split("\t") for row in rows if row.strip()]  #用制表符分割每个样本的变量值
        self.dataset = datalist
        self.labels = labels
    '''3、执行决策树函数'''
    def train(self):
        labels = copy.deepcopy(self.labels)     #深度复制lebels，相当于备份
        
        self.tree = self.buildTree(self.dataset,labels)

    '''4、创建决策树主程序'''
    def buildTree(self,dataset,labels):
        catelist=[data[-1] for data in dataset]     #抽取数据源标签列
        '''程序终止，只有一种分类标签'''
        if catelist.count(catelist[0]) == len(catelist):
            return catelist[0]
        '''只有一个变量，无法再分'''
        if len(dataset[0])==1:
            return self.maxCate(catelist)
        '''算法核心：返回最优特征轴'''
        bestfeat = self.getBestFeat(dataset)
        bestfeatlabel = labels[bestfeat]
        tree={bestfeatlabel:{}}
        del labels[bestfeat]
        '''抽取最优特征轴的列向量'''
        uniqueVals = set([data[bestfeat] for data in dataset])      #特征轴的值
        for value in uniqueVals:
            sublabels=labels[:]
            splitdata = self.splitdataset(dataset,bestfeat,value)
            subTree = self.buildTree(splitdata,sublabels)
            tree[bestfeatlabel][value]=subTree
        return tree
    
    '''5、计算出现次数最多的类别标签'''
    def maxCate(self,catelist):
        items = dict([(i, catelist.count(i),) for i in catelist])    
        maxc = list(items.keys())[list(items.values()).count(max(list(items.values())))]
        return maxc

    '''6、计算最优特征'''
    def getBestFeat(self,dataset):
        numFeatures = len(dataset[0])-1    #计算特征维
        baseEntropy = self.computeEntropy(dataset)      #计算信息熵，基础的
        bestgain=0          #初始化信息增益
        bestFeature = -1    #初始化最优特征轴
        for x in range(numFeatures):
            uniqueVals = set([data[x] for data in dataset])
            newEntropy=0
            for value in uniqueVals:
                subdataset = self.splitdataset(dataset,x,value)     #切分数据集，取出需要计算的部分
                pro = len(subdataset)/len(dataset)
                newEntropy += pro*self.computeEntropy(subdataset)
            gain = baseEntropy - newEntropy         #计算最大增益
            if gain>bestgain:
                bestgain = gain
                bestFeature = x
        return  bestFeature
    
    '''7、计算信息熵'''
    def computeEntropy(self,dataset):
        cates = [i[-1] for i in dataset]
        datalen = len(dataset)
        items = dict([(cate, cates.count(cate)) for cate in cates])
        Entropy=0
        for key in items.keys():
            pro = float(items[key])/datalen
            Entropy -=pro*np.log2(pro)
        return Entropy
    
    '''8、划分数据集'''
    def splitdataset(self,dataset,axis,value):
        rtnlist=[]
        for data in dataset:
            if data[axis]==value:
                rtndata=data[:axis]
                rtndata.extend(data[axis+1:])
                rtnlist.append(rtndata)
        return rtnlist
    
    '''9、持久化决策树——储存树'''
    def storeTree(self,inputTree,filename):
        with open(filename,'w') as file:
            pickle.dump(inputTree,file)
    
    '''10、读取树'''
    def loadTree(self,filename):
        with open(filename,'r') as file:
            fr=pickle.load(file)
        return fr
    '''11、决策树预测'''
    def predict(self,inputTree,featLabels,testVec):
        felist=list(inputTree.keys())        #寻找树根节点的特征
        root=felist[0]
        secondDict=inputTree[root]      #树根节点对应的判断值或者是子结构
        rootIndex = featLabels.index(root)      #树根节点的位置index
        key = testVec[rootIndex]        #测试集数据在树根节点特征轴上的值
        subtree = secondDict[key]       #根据测试集的值所对应的结果
        '''判断subroot是树结构还是值'''
        if isinstance(subtree,dict):
            testlabel = self.predict(subtree,featLabels,testVec)    #递归分类
        else:
            testlabel = subtree
        return testlabel
        

'''训练树'''
dtree =ID3Tree()
dtree.loadDataSet(r"D:\mywork\test\ML\dataset_ID3.dat",['age','revenue','student','credit'])
dtree.train()
print(dtree.tree)

'''储存和读取树'''
dtree.storeTree(str(dtree.tree),'data.tree')
mytree=dtree.loadTree('data.tree')
print(mytree)

'''决策树分类预测'''
dtree = ID3Tree()       #实例化
labels=['age','revenue','student','credit']
testdata=['0','1','0','0']
mytree = dtree.loadDataSet('data.tree')
print(dtree.predict(mytree,labels,testdata))


###################决策树C4.5算法##################
import numpy as np
import math, copy, pickle

'''定义类'''
class C45Tree(object):
    '''1、初始化'''
    def __init__(self):         #构造方法
        self.tree={}            #生成树
        self.dataset=[]         #数据集
        self.labels=[]          #标签集
        
    '''2、数据导入函数'''
    def loadDataSet(self,path,labels):
        datalist=[]
        with open(path,"r") as f:          #二进制形式读取文件
            content=f.read()
        rows = content.splitlines()     #分割文本，按行转换为一维表
        datalist=[row.split("\t") for row in rows if row.strip()]  #用制表符分割每个样本的变量值
        self.dataset = datalist
        self.labels = labels
    '''3、执行决策树函数'''
    def train(self):
        labels = copy.deepcopy(self.labels)     #深度复制lebels，相当于备份
        
        self.tree = self.buildTree(self.dataset,labels)

    '''4、创建决策树主程序'''
    def buildTree(self,dataset,labels):
        catelist=[data[-1] for data in dataset]     #抽取数据源标签列
        '''程序终止，只有一种分类标签'''
        if catelist.count(catelist[0]) == len(catelist):
            return catelist[0]
        '''只有一个变量，无法再分'''
        if len(dataset[0])==1:
            return self.maxCate(catelist)
        '''算法核心：返回最优特征轴'''
        bestfeat, bestfeatvalue = self.getBestFeat(dataset)
        bestfeatlabel = labels[bestfeat]
        tree={bestfeatlabel:{}}
        del labels[bestfeat]
        '''抽取最优特征轴的列向量'''
        for value in bestfeatvalue:
            sublabels=labels[:]
            splitdata = self.splitdataset(dataset,bestfeat,value)
            subTree = self.buildTree(splitdata,sublabels)
            tree[bestfeatlabel][value]=subTree
        return tree
    
    '''5、计算出现次数最多的类别标签'''
    def maxCate(self,catelist):
        items = dict([(i, catelist.count(i),) for i in catelist])    
        maxc = list(items.keys())[list(items.values()).count(max(list(items.values())))]
        return maxc

    '''6、计算最优特征'''
    def getBestFeat(self,dataset):
        numFeatures = len(dataset[0])-1    #计算特征维
        totality = len(dataset)     #数据集数量
        baseEntropy = self.computeEntropy(dataset)      #计算信息熵，基础的
        conditionEntropy=[]     #初始化条件熵
        slpitInfo = []          #特征轴基础熵
        allFeatVList = []       #特征轴数值的子集
        bestgain=0          #初始化信息增益
        for x in range(numFeatures):
            featList=[data[x] for data in dataset]      #取出特征列的值
            [split,featureValueList] = self.computeSplitInfo(featList)      #特征轴基础熵，和特征轴数值的子集
            allFeatVList.append(featureValueList)
            slpitInfo.append(split)
            newEntropy=0
            for value in featureValueList:
                subdataset = self.splitdataset(dataset,x,value)     #切分数据集，取出需要计算的部分
                pro = len(subdataset)/float(totality)
                newEntropy += pro*self.computeEntropy(subdataset)
            conditionEntropy.append(newEntropy)     #各个特征轴的条件熵
        gain=baseEntropy*np.ones(numFeatures) - np.array(conditionEntropy)  #ID3信息增益数组
        gainRatio = gain/np.array(slpitInfo)        #C4.5信息增益率数组
        bestFeatureIndex = np.argsort(-gainRatio)[0]   #将增益率的Index从大到小排序，并选取最大的Index
        bestFeatureValue = allFeatVList[bestFeatureIndex]   #信息增益率最大的所有特征值
        return bestFeatureIndex,bestFeatureValue
    
    '''7、计算信息熵'''
    def computeEntropy(self,dataset):
        cates = [i[-1] for i in dataset]
        datalen = len(dataset)
        items = dict([(cate, cates.count(cate)) for cate in cates])
        Entropy=0
        for key in items.keys():
            pro = float(items[key])/datalen
            Entropy -=pro*np.log2(pro)
        return Entropy
    
    '''8、计算特征轴的基础熵'''
    def computeSplitInfo(self,featureList):
        nums = len(featureList)
        valuenums = list(set(featureList))
        valuecounts = [featureList.count(value) for value in valuenums]
        prolist = [float(valuecount)/nums for valuecount in valuecounts]
        Elist = [pro*np.log2(pro) for pro in prolist]
        splitInfo = -np.sum(Elist)      #返回特征轴基础熵
        return splitInfo,valuenums    #返回特征轴、特征值的子集（去重）
    
    '''9、划分数据集'''
    def splitdataset(self,dataset,axis,value):
        rtnlist=[]
        for data in dataset:
            if data[axis]==value:
                rtndata=data[:axis]
                rtndata.extend(data[axis+1:])
                rtnlist.append(rtndata)
        return rtnlist
    
    '''10、持久化决策树——储存树'''
    def storeTree(self,inputTree,filename):
        with open(filename,'w') as file:
            pickle.dump(inputTree,file)
    
    '''11、读取树'''
    def loadTree(self,filename):
        with open(filename,'r') as file:
            fr=pickle.load(file)
        return fr
    '''12、决策树预测'''
    def predict(self,inputTree,featLabels,testVec):
        felist=list(inputTree.keys())        #寻找树根节点的特征
        root=felist[0]
        secondDict=inputTree[root]      #树根节点对应的判断值或者是子结构
        rootIndex = featLabels.index(root)      #树根节点的位置index
        key = testVec[rootIndex]        #测试集数据在树根节点特征轴上的值
        subtree = secondDict[key]       #根据测试集的值所对应的结果
        '''判断subroot是树结构还是值'''
        if isinstance(subtree,dict):
            testlabel = self.predict(subtree,featLabels,testVec)    #递归分类
        else:
            testlabel = subtree
        return testlabel

'''训练数据集'''
dtree=C45Tree()
dtree.loadDataSet(r"D:\mywork\test\ML\dataset_ID3.dat",['age','revenue','student','credit'])
dtree.train()

'''测试数据'''
mytree=dtree.tree
re=dtree.predict(mytree,['age','revenue','student','credit'],['0','1','0','0'])
print(re)


###################Scikit-learn与回归树##################
'''cart树选择最优分隔点'''
#leafType:叶子节点线性回归函数
#errType:最小剩余方差实现函数
#ops:允许的方差下降值，最小切分样本数
def getBestFeat(dataSet, leafType=regLeaf, errType=regErr, ops=(1,4)):
    tolS = ops[0]                           #允许的方差下降值
    tolN = ops[1]                           #最小切分样本数
    '''---算法终止条件1开始---'''
    splitdataSet = set(dataSet[:,-1].T.tolist()[0])
    if splitdataSet == 1:                   #只有一个观测值？？？
        return None, leafType(dataSet)
    '''计算最优划分方差、划分列、划分值'''
    m,n = dataSet.shape()                   #数据集的行和列
    S = errType(dataSet)                    #数据集的总体方差
    bestS = np.inf                          #初始化最优方差
    bestIndex = -1                          #初始化最优列
    bestValue = 0                           #初始化最优值
    for index in range(n-1):                #遍历变量
        for value in set(dataSet[:,index]): #遍历变量的值
            mat0,mat1 = binSplit(dataSet, index, value) #二元划分数据集，函数
            '''判断是否小于最小叶节点个数'''
            if mat0.shape[0]<tolN or mat1.shape[0]<tolN:
                continue
            newS = errType(mat0) + errType(mat1)
            if newS < bestS:
                bestS = newS
                bestIndex = index
                bestValue = value
    
    '''---算法终止条件2开始：返回的是值节点类型---'''
    if (S-bestS)<tolS:
        return None,leafType(dataSet)
    
    '''---算法终止条件3开始：最小叶节点个数小于指定值'''
    mat0,mat1 = binSplit(dataSet, index, value) #二元划分数据集，函数
    '''判断是否小于最小叶节点个数'''
    if mat0.shape[0]<tolN or mat1.shape[0]<tolN:
        return None,leafType(dataSet)
    
    '''---算法终止条件4：返回子树节点类型，还需继续递归回归'''
    return bestIndex, bestValue
    
'''二元划分数据集函数'''    
def binSplit(dataSet, index, value):
    mat0 = dataSet[dataSet[:,index]>value,:]
    mat1 = dataSet[dataSet[:,index]<=value,:]
    return mat0,mat1

'''剪枝策略'''
def prune(tree, testData):
    '''没有测试集输入，运行getMean，程序退出'''
    if testData.shape[0] == 0:
        return getMean(tree)

'''Scikit-learn案例'''
import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor
'''1、数据可视化函数'''
def plotfig(x,xtest,y,yp):
    plt.figure()
    plt.scatter(x,y,c='k',label='data')
    plt.plot(xtest,yp,c='r',label='max_depth=5',linewidth=2)
    plt.xlabel('data')
    plt.ylabel('target')
    plt.title("Decision Tree Regression")
    plt.legend()
    plt.show()
    
'''2、执行决策树'''
x=np.linspace(-5,5,200)
siny = np.sin(x)
y=siny+np.random.rand(1,len(siny))*1.5
#将X转换为二维进行训练
x=np.mat(x).T
y=y.tolist()[0]
clf = DecisionTreeRegressor(max_depth=4)
clf.fit(x,y)
#预测新数据
xtest=np.arange(-5,5,0.05)[:,np.newaxis]
yn=clf.predict(xtest)
#将数据转换为一维画图
X=[x[i,0] for i in range(len(x))]
Xtest=[xtest[i,0] for i in range(len(xtest))]
plotfig(X,Xtest,y,yn)










