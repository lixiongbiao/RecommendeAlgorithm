# -*- coding: utf-8 -*-
"""
Created on Fri Sep 23 11:14:02 2016

@author: Troy 
"""

from scipy.sparse import csr_matrix
from scipy.io import mmread

def load_items(filename):    #读取商品及下标对应数据
    df=open(filename)
    items=dict()              #下标为值 产品为值字典
    items_reverse=dict()      #产品为键 下标为值字典
    for line in df.readlines():
        line=line.strip().split('\t')
        items[int(line[0])]=line[1]      #此处商品下标对应字典中 需要将键值从字符串形式转换为整形，以便后续找对应产品时键值数据类型一致
 #       items_reverse(line[1])=int(line[0])
    df.close()
    return items,items_reverse
    
def load_visit_sparse_matrix(filename):   #读取用户访问行为对应稀疏矩阵
    data=mmread(filename)
    data=csr_matrix(data)
    return data

    
class Recommender():   #推荐函数类     类型命名切记下划线使用
    def __init__(self,items_filename,visit_filename):   #构造推荐类，输入为产品及下标对应文件和历史访客访问记录文件(稀疏矩阵)
        self.items,self.items_reverse=load_items(items_filename)    #下标为键 产品位值 字典  和产品为键 下标为值字典
        self.visit_sparse_matrix=load_visit_sparse_matrix(visit_filename)   #历史访问行为稀疏矩阵

    def similarity(self,visit_vector,reco_numble,Distance='Jaccard Distance',method='UBCF'):    #计算相关性，输入为一个横向量：一个用户的访问稀疏向量 或者一个产品的URL    
        if Distance=='Jaccard Distance':
            if method=='UBCF':
                distance_list=[0  for i in range(self.visit_sparse_matrix.shape[0])]   #切记初始化没有设置空间 后续赋值就不能索引  只能append
                for i in range(self.visit_sparse_matrix.shape[0]):    #分解计算新用户与历史用户浏览行为的杰卡德距离 ： q/(q+r+p)   q+r+p=两用户所有浏览产品总和 - 公共浏览页面总和
                    distance_list[i]=(self.visit_sparse_matrix[i].dot(visit_vector.T).todense()[0,0])/(len(visit_vector.nonzero()[0])+len(self.visit_sparse_matrix[i].nonzero()[0])-self.visit_sparse_matrix[i].dot(visit_vector.T).todense()[0,0])  #前者巧妙通过两个稀疏向量点积和得到公共浏览页面总和！
                                                                #此处取[0,0]是为了取矩阵乘积后唯一的一个元素  下标为0,0
                max_similarity=[]
                similarity_degree=[]
                for i in range(reco_numble):    #计算相似度排名前n的用户
                    while max(distance_list)==1:   #首先将相似度为1 的去掉，因为他们完全一样 没推荐价值
                        distance_list[distance_list.index(1)]=0
                    max_similarity.append(distance_list.index(max(distance_list)))
                    similarity_degree.append(max(distance_list))
                    distance_list[distance_list.index(max(distance_list))]=0
                return max_similarity,similarity_degree
            if method=='PBCF':
                
                
                return
                
                
                
        
                
    
    
    
                  #函数返回值为排在前n个的相似性用户或者产品下标    
    
    
    def recommender_new_user(self,user_visit, method='UBCF',reco_numble=2,Distance='Jaccard Distance'):    #推荐函数，输入为新用户访问产品名称记录列表，推荐方法（默认为基于用户），推荐产品个数或者基于多少个用户推荐
        recommend_product_dict=dict()       
        recommend_product_list=[]
        if method=='UBCF' and isinstance(user_visit,list):      #判断方法为基于用户  且输入为用户访问记录列表才执行
            user_visit_dict=dict()
            row,col,data=[],[],[]    #构建用户访问系数矩阵
            max_similarity_user=[]   #最大相似性的用户列表，个数基于reco_numble而定
            for item in user_visit:
                if isinstance(item,str):
                    if item not in self.items:
                        continue         #如果用户访问记录中产品不存在于历史训练字典中 则自动过滤
                    row.append(0);
                    col.append(int(self.items_reverse[item]))  #讲访问产品对应下标列置为1  代表访问
                    data.append(1)
                    user_visit_dict[item]=1
                elif isinstance(item,int):
                    if item not in self.items_reverse:
                        continue         #如果用户访问记录中产品不存在于历史训练字典中 则自动过滤
                    row.append(0);
                    col.append(item)  #讲访问产品对应下标列置为1  代表访问
                    data.append(1)
                    user_visit_dict[self.items[item]]=1
            user_sparse_visit=csr_matrix((data,(row,col)),shape=(1,len(self.items.keys())))   #构建访问稀疏一维向量，维度为历史产品数总数（为了后续计算相似性时维度一致）
            max_similarity_user,max_similarity_degree=self.similarity(user_sparse_visit,reco_numble,Distance,method)   #获得相关用户序号 进行后续推荐
            
            
            for i in range(reco_numble): 
                trainning_user_dict=dict()    #需要推荐的用户字典
                for row,col in zip(self.visit_sparse_matrix[max_similarity_user[i]].nonzero()[0],self.visit_sparse_matrix[max_similarity_user[i]].nonzero()[1]):     #此时循环选择的是该用户稀疏向量中的不为零的 列下标  行下表恒为0，   .nonzero() 返回两个数组
                    trainning_user_dict[str(self.items[col])]=1    #获得相似度大的历史用户访问记录字典
                for item in trainning_user_dict:
                    if item not in user_visit_dict:
                        recommend_product_dict[item]=1
            for item in recommend_product_dict:
                recommend_product_list.append(item)
            print ("Method=%s\nUser_similarity:" %(method))
            for i in max_similarity_degree:
                print(i,end=' ')
            print()
            for item,i in zip(recommend_product_list,range(5)):   #i条件控制最多推荐5个产品
                print(item,end=' ')
            return
            
            
        elif method=='PBCF' and isinstance(user_visit,str):     #判断方法为基于产品的推荐，且输入的为一个产品名称 才执行后续
            pass
        
        
        
        else:
            print ("This method has not been developed, We will perfect the algorithm in the future!")
            return 
        
            
                
if __name__=='__main__':
    reco=Recommender('items_numble.txt','visit_sparse_matrix.mtx')   
    reco.recommender_new_user([154])
    #reco.recommender_new_user(['http://www.ehaier.com/product/comment/9667.html','http://www.ehaier.com/product/9667.html?ebi=ref-se-1-1'],reco_numble=3)
        