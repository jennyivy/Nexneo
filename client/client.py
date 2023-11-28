import requests
import json
import pickle
from time import time

url = 'http://localhost:8000/rec_home'
params={"cust_id":'merchant_id_0', "user_id":'6478320551548919808', "rec_num":10}

headers = {"Content-Type": "application/json"}
batch_test_file=open('batch_test.pkl', 'rb')
batch_params=pickle.load(batch_test_file)
t1=time()
cnt=0
for params in batch_params:
    data=json.dumps(params)
    cnt+=1
    response = requests.post(url, headers = headers, data=data)
    if cnt==10:
        break
t2=time()
elapsed=t2-t1
print('elapsed time is %f seconds.' % elapsed)

