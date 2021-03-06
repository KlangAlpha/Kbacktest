#!/usr/bin/env python

# Klang backtest server

import asyncio
import json
import logging
import websockets
import traceback

from threading import Lock
logging.basicConfig()

import threading
import sys,os 
import backtest
from multiprocessing import Process


from Klang import Kl,Klang
Klang.Klang_init(); #加载所有股票列表

mutex = Lock ()

ws = None 

def await_run(coroutine):
    try:
        coroutine.send(None)
    except StopIteration as e:
        return e.value

# 因为是需要在Klang执行，所以需要await_run执行 sync消息
def resp_msg(message):

    message['type'] = K_RET
    msg = json.dumps(message)

    await_run(ws.send(msg))


async def execute(handler,data):
    
    # 1.  获取内容
    sourcecode = data['content']+"\n"

    # 2. 执行 busy lock 执行锁
    mutex.acquire()
    if sys.platform == 'linux' or sys.platform =='linux2':
        p = Process(target=backtest.execute,args=(sourcecode,resp_msg,Kl))
    else: # windows ,macosx multiprocess 有bug
        p = threading.Thread(target=backtest.execute,args=(sourcecode,resp_msg,Kl))
    p.start()
    p.join()

    # unlock

    mutex.release()   #之行完成，解锁，发通知给web用户
    print('执行完成')

    # 3. 执行完成 
    await handler.done()

# server 和klang执行服务器交互
# Klang msg type
#K_REG          = "K_REG"   #服务器发送给管理这服务器上线
#K_UNREG        = "K_UNREG" #服务器发送给管理者服务器离开
K_HEARTBEAT    = "K_HEART" #心跳包 
K_EXE          = "K_EXE"  #管理者发送给服务器
K_DONE         = "K_DONE" #服务器返回给管理者
K_CMD          = "K_CMD"  #管理者发送给服务器
K_RET          = "K_RET"  #服务器返回给管理者

class KlangMSG():
    def __init__(self,websocket):
        self.websocket = websocket

    def pack_exe(self,exe):
        msg = {
            "type":"K_EXE"
        }
        msg.update(exe)
        data = json.dumps(msg)
        self.websocket.send(data)

    def pack_cmd(self,cmd):
        msg = {
            "type":"K_CMD"
        }
        msg.update(cmd)
        data = json.dumps(msg)
        self.websocket.send(data)
    
 
    async def parse(self,msg):
        
        if msg["type"] == K_EXE:
            await execute(self,msg)    
        if msg["type"] == K_DONE:
            mutex.acquire()
            self.state = 0
            self.exe_user = None
            mutex.release()


    async def done(self):
        msg ={"type":K_DONE}
        data = json.dumps(msg)
        await self.websocket.send(data)


#klang backtest server
server_host = 'ws://localhost:9088/kbtserver'
#server_host = 'wss://klang.org.cn:8099/kbtserver'
#server_host = 'ws://klang.org.cn:9099/kbtserver'

async def conn_server():

    global ws #for DISPALY

    while True:
        try:
            async with websockets.connect(server_host) as websocket:
                print("connect success!",server_host)
                websocket.handler = KlangMSG(websocket)
                ws = websocket

                while True:
                    data = await websocket.recv()
                    msg = json.loads(data)
                    await websocket.handler.parse(msg)
                    if msg['type'] == K_EXE: # 每次测试需要创建新的进程，进程退出可能会让websocket连接失败
                        websocket.close() #所以直接重新连接
                        break

        except BaseException as e:
            traceback.print_stack()
            if isinstance(e, KeyboardInterrupt):
                break

        print("connect server error,try again ",server_host)
        await asyncio.sleep(2)
if __name__ == '__main__':
    
    asyncio.get_event_loop().run_until_complete(conn_server())

