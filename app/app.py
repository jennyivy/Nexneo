from sanic import Sanic, response
from sanic.exceptions import ServerError
import asyncpg
import requests
import json
import redis
import faiss
import numpy as np
import pickle
import sys
import os
import yaml
parent_dir = os.path.join(os.getcwd(),'..')
sys.path.append(parent_dir)
from app.recom import recommend
from log.logs import * 

app = Sanic('test')

r_user = redis.Redis(host='localhost', port=6379, db=0)

def check_database_connection():
    try:
        # 在这里添加您的数据库连接逻辑
        r = redis.Redis(host='localhost', port=6379, db=0)
        return True
    except Exception as e:
        return False
    
@app.route("/api/health", methods=["GET"])
async def health(request):
    try:
        # 检查数据库连接是否可用
        db_status = check_database_connection()
        if not db_status:
            raise ServerError("Database connection failed", status_code=500)
        # 在这里添加其他的健康检查逻辑
        return response.json({"status": "ok"})
    except Exception as e:
        # 如果发生任何错误，返回一个错误的响应
        raise ServerError("Health check failed", status_code=500)   
        # 如果一切正常

# 定义预测接口
@app.route('/rec_home', methods=['POST'])
async def rec_home(request):
    data=request.json
#    print(data)
    if not request.json or not data.get('cust_id') or not data.get('user_id'):
        app_log.info(f'参数传入出错')
        return response.json({'message':'参数传入出错'}, status=400)
    cust_id = data.get('cust_id')
    user_id = data.get('user_id')
    rec_num = data.get('rec_num', 10) #  默认返回10个id
    app_log.info(f'cust_id:{cust_id}, user_id:{user_id}')
   #  db_status =  check_database_connection()

   # if not db_status:
   #     app_log.info(f'服务器出错')
   #     return response.json({'message':'数据库连接错误'}, status=500)
    
    configs_file= open('config/config.yaml', 'r', encoding='utf-8')
    configs=yaml.load(configs_file, yaml.FullLoader)

    recommder=recommend(cust_id, user_id, rec_num, configs, r_user, item_id=None)
    res= recommder.online_recomm()
    app_log.info(f'返回产品列表:{res}')
    return response.json({'sku_num':rec_num, 'sku_ids':res}, status=200)


@app.route('/rec_detail', methods=['POST'])
async def rec_detail(request):
    # 
    user_id = request.args.get('user_id')
    if not user_id:
        return json({'error': 'No user_id uploaded'}) 
    # 返回预测结果
    # to be added
    return 

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, workers=4, access_log=False)
