import asyncpg
import json
import redis
import faiss
import numpy as np
import pickle
import sys
import os
import yaml
import collections
from time import time

class recommend(object):

    def __init__(self, custom_id, user_id, rec_num, configs, r_user, item_id=None):
        self.custome_id = custom_id
        self.user_id = user_id
        self.item_id = item_id
        self.rec_num = rec_num
        self.configs=configs
        self.index = self.configs['index_path']
        self.sku_file=self.configs['sku_file']
        self.hot_skus = self.configs['hot_sku_file']
        self.online_skus = self.configs['online_sku_file']
        self.r_user = r_user

    def get_data(self):
        r_online_sku = open(self.online_skus, 'rb')
        r_hot_sku = open(self.hot_skus, 'rb')
        cust_id_val = self.r_user.get(self.custome_id)
        cust_id_value = json.loads(cust_id_val)
        r_online_sku=pickle.load(r_online_sku)
        r_hot_sku=pickle.load(r_hot_sku)

        return cust_id_value, r_online_sku, r_hot_sku
    
    def get_user_vector(self):
        cust_id_val, r_online_sku, r_hot_sku = self.get_data()
        user_id_action=cust_id_val[self.user_id]
        sku_ids=user_id_action['sku']
        ADT_ids=user_id_action['ADT']
        ADF_ids=user_id_action['ADF']
        order_ids=user_id_action['order']
        index=faiss.read_index(self.index)
        index.make_direct_map()
        sku_id_file=open(self.sku_file, 'rb')
        items_list=pickle.load(sku_id_file)
        user_sku_vec, user_adt_vec, user_adf_vec, user_order_vec = np.array([]), np.array([]), np.array([]), np.array([])
        if sku_ids:
            sku_id_index=[items_list.index(item) for item in sku_ids]
            sku_vec=np.array([index.reconstruct(ele) for ele in sku_id_index])
            user_sku_vec=np.mean(sku_vec, axis=0, keepdims=True)
                
        if ADT_ids:
            adt_id_index=[items_list.index(item) for item in ADT_ids]
            adt_id_vec=np.array([index.reconstruct(ele) for ele in adt_id_index])
            user_adt_vec=np.mean(adt_id_vec, axis=0, keepdims=True)

        if ADF_ids:
            adf_id_index=[items_list.index(item) for item in ADF_ids]
            adf_id_vec=np.array([index.reconstruct(ele) for ele in adf_id_index])
            user_adf_vec=np.mean(adf_id_vec, axis=0, keepdims=True)

        if order_ids:
            order_id_index=[items_list.index(item) for item in order_ids]
            order_id_vec=np.array([index.reconstruct(ele) for ele in order_id_index])
            user_order_vec=np.mean(order_id_vec, axis=0, keepdims=True)

        return [user_sku_vec, user_adt_vec, user_adf_vec, user_order_vec]
    
    def recall(self):
        user_vec=self.get_user_vector()
        recall_dict=collections.defaultdict(list)
        index=faiss.read_index(self.index)
        for ele in user_vec:
            if ele.size!=0:
                D, I = index.search(ele, self.rec_num) # 对相同ID，distance取平均。
              #  print(D[0], I[0])
                for i, ele in enumerate(I[0]):
               #     print(ele)
                    recall_dict[ele].append(D[0][i])
       # print(recall_dict)
        for key, val in recall_dict.items():
            recall_dict[key]=sum(val)/len(val)

        return recall_dict


    def rank(self):
        dic=self.recall()
        ordered_dic=sorted(dic.items(), key = lambda x:x[1])
       # print(ordered_dic)
        index_list=[ele[0] for ele in ordered_dic[:self.rec_num]]
        sku_id_file=open(self.sku_file, 'rb')
        items_list=pickle.load(sku_id_file)
        # print(index_list)
       #  print(items_list)
        return [items_list[index] for index in index_list]
    
    def online_recomm(self):
        res=[]
        cust_id_value, r_online_sku, r_hot_sku=self.get_data()
        if self.user_id not in cust_id_value: # 新用户用热销兜底
            for i in range(self.rec_num):
                if r_hot_sku[i] in r_online_sku:
                    res.append(r_hot_sku[i])
                else:
                    continue
        else:
            res=self.rank()

        return res
    

if __name__=='__main__':
    custom_id = 'merchant_id_0'
    user_id = '6478320551548919808'
    rec_num=10
    configs_file= open('../config/config.yaml', 'r', encoding='utf-8')
    configs=yaml.load(configs_file, yaml.FullLoader)
    r_user=redis.Redis(host='localhost', port=6379, db=0)
    test_file=open('../client/batch_test.pkl', 'rb')
    test_params=pickle.load(test_file)
    t1=time()
    cnt=0
    for ele in test_params:
        custom_id=ele['cust_id']
        user_id=ele['user_id']
        rec_num=ele['rec_num']

        recommder=recommend(custom_id, user_id, rec_num, configs,r_user, item_id=None)
        cnt+=1
        if cnt==100:
            break

    t2=time()

    print(t2-t1)
