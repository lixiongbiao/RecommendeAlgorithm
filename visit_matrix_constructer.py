# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22 16:41:12 2016

@author: asus-4837
"""

from scipy.sparse import csr_matrix
from scipy.io  import mmwrite,mmread
import pandas as pd

df=pd.read_csv('visit_order.txt')
items=dict()    #商品对应下标字典          key=商品  value=下标
items_reverse=dict()   #下标对应商品字典   key=下标   value=商品
visit=dict()     #用户访问行为字典
n=0
for line in range(int(len(df)*0.1)):
    if df.ix[line,1] not in items:
        items[df.ix[line,1]]=n
        items_reverse[n]=df.ix[line,1]
        n+=1
    if df.ix[line,2]  not in visit:
        visit[df.ix[line,2]]={df.ix[line,1]:1}
    else:
        if df.ix[line,1] in visit[df.ix[line,2]]:
            continue
        else:
            visit[df.ix[line,2]][df.ix[line,1]]=1
n=0   #构建系数矩阵用户数下标
row=[]   #稀疏矩阵三大参数
col=[]
data=[]
for user in visit:        #此时每一个user是一个键值对应字符，切不可认为还是个字典 ！！！
    for item in visit[user]:     #因此此处仍然得取字典对应键值才能得到对应的子字典！ 
        row.append(n)    
        col.append(items[item])     #把用户浏览过的网页对应下标设置为1
        data.append(1)
    n+=1
    
#构建稀疏矩阵
visit_matrix=csr_matrix((data,(row,col)))
mmwrite('visit_sparse_matrix',visit_matrix)

df=open('items_numble.txt','w')
for i in range(len(items_reverse.keys())):    #将产品及对应下标 按字典中下标顺序存入文档中
    df.write(str(i)+'\t'+str(items_reverse[i])+'\n')
df.close()
    
    
