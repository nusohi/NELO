'''
@Description: 每日随机单词推送
@Author: nuso
@LastEditors: nuso
@Date: 2020-07-29 22:27:20
@LastEditTime: 2020-07-31 18:13:53
'''
import os
import sys
path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(path)
from conf import CONF
from dictionary import LocalDictionary
import time
import threading
import random

class DayDayWord:
    def __init__(self):
        self.todayWords = []
        self.pureWords = []
        self.dictionary = LocalDictionary()
        self.prepareCount = 100     # 一次准备 100 个
        self.sunrise = 9
        self.sunset = 23
        self.index = 0
        self.__Load__()
        self.__Prepare__()

    def Get(self, num=5):
        string = ''
        for word in self.todayWords[:num]:
            string += word + '\n\n'

        # 剩余单词不足需及时补充
        if num*2 >= len(self.todayWords):
            t = threading.Thread(target=self.__Prepare__)
            t.start()
            
        self.todayWords = self.todayWords[num:]

        string += '----> 每日单词提醒'
        return string

    # 准备下一次的所有单词
    def __Prepare__(self):
        for i in range(self.prepareCount):
            if self.index >= len(self.pureWords):
                break
            word = self.pureWords[self.index]
            text = f'【{word}】'
            text += self.dictionary.Translate(word)
            self.todayWords.append(text)
            self.index += 1

    def __Load__(self):
        with open(CONF['KaoYanWords']) as f:
            self.pureWords = f.read().split('\n')
        random.shuffle(self.pureWords)
        


if __name__ == '__main__':
    day = DayDayWord()
    s = day.Get()
    print(s)
