#coding:utf-8
import sys
from phprpc.phprpc import PHPRPC_Client
rpc=PHPRPC_Client("http://www.cloudapi.info/b8_api.py?code=HW4MlGesu5RJUcMZmfWSXd8vdrz3uXWs")
comment={"ip":"127.0.0.1","text":"招聘兼职"}
print rpc.api_test_comment(comment)
