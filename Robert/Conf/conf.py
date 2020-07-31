'''
@Description: 可手动更新的配置
@Author: nuso
@LastEditors: nuso
@Date: 2020-07-31 08:32:01
@LastEditTime: 2020-07-31 08:35:44
'''
import os
import sys
sys.path.append("..") 
father_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))

import json
import time
import asyncio
import threading
import Utils.Single

@util.Single.Singleton
class Conf:
    conf_path = os.path.join(father_path, 'conf.json')
    conf = {}
    update = False

    def __init__(self):
        self.Load()
        t = threading.Thread(target=self.AutoSave)
        t.setDaemon(True)
        t.start()
        

    def get(self, key):
        return self.conf[key]

    def put(self, key, value):
        if self.conf.__contains__(key):
            if isinstance(self.conf[key], bool):
                self.conf[key] = False if value.lower() in ('no', 'false', 'f', '0', 'n') else True
            elif isinstance(self.conf[key], int):
                self.conf[key] = int(value)
            elif isinstance(self.conf[key], float):
                self.conf[key] = float(value)
            elif isinstance(self.conf[key], str):
                self.conf[key] = value
        if value.isdigit():
            self.conf[key] = int(value)
        else:
            self.conf[key] = value
        update = True
        self.Save()

    def show(self, all=False):
        msg = ''
        for key in self.conf.keys():
            msg += key + ', '
        msg = msg[:-2]
        if all:
            msg += '\n\n'
            for key, value in self.conf.items():
                msg += key + ' : ' + str(value)[:15] + '\n'

        return f"当前配置：\n{msg}" 


    def Load(self):
        with open(self.conf_path, 'r') as file:
            self.conf = json.load(file)
    
    def Save(self):
        with open(self.conf_path, 'w') as file:
            json.dump(self.conf, file, indent=2)
            self.update = False
            print('[conf] 配置更新 :')
            print(self.conf)

    def AutoSaveThread(self):
        t = self.AutoSave()   # 自动保存 coroutine
        loop = asyncio.get_event_loop() # 获取EventLoop
        loop.run_until_complete(t)
        loop.close()

    def AutoSave(self):
        while(True):
            Conf_AutoSaveTime = self.get('ConfAutoSaveTime')
            time.sleep(Conf_AutoSaveTime)
            if self.update:
                self.Save()
