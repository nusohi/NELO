import os
import sys
path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(path)

from UJSExamQuery.ExamQuery import *  # import ExamQuery
from conf import FriendPass, FriendList, friendList, nuso_toUserName
import itchat
import threading
from threading import Timer
import time
import json
import re
import weather
import dictionary
import reminder


# 查天气
wea = weather.Weather()
# 查单词
dict = dictionary.Dictionary()


@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
    printMsg(msg)   # 控制台输出
    friend = itchat.search_friends(userName=msg['FromUserName'])
    msgText = msg.text.strip()

    # 加入friend列表
    if msgText == FriendPass and not friend['RemarkName'] in friendList:
        AddNewFriend(friend['RemarkName'])
        print("-----------> new friend " + friend['RemarkName'])
        return "Welcome!"

    if friend['RemarkName'] in friendList:
        print("-----------> 来自FriendList")
        # 有'天气'字眼 -> 查天气
        for txt in wea.weatherCode:
            if re.search(txt, msgText):
                return wea.getWeather(msgText)

        # 有单词或短语 -> 查单词
        if dict.IsWordOrPhrase(msgText):
            translation = dict.GetTranslation(msgText)
            return translation

        # 最后没有关键词直接查天气
        cityName = wea.FindCityName(msgText)
        if(cityName):
            return wea.getWeatherByName(cityName)

        return 'server received...'
    else:
        print("-----------> 不在friendList的人")
        print('-----------> friend list :', friendList)


def UpdateUserName():
    nuso_friend = itchat.search_friends(remarkName='nuso')
    for nuso in nuso_friend:
        nuso_toUserName = nuso['UserName']
        return nuso_toUserName


def AddNewFriend(name):
    with open(FriendList, 'a+', encoding="UTF-8") as FriendListFile:
        FriendListFile.write(name + '\n')
    friendList.append(name)


def LoadFriendList():
    with open(FriendList, 'r', encoding="UTF-8") as FriendListFile:
        list = FriendListFile.read().split('\n')
        list.remove('')
        for friend in list:
            friendList.append(friend)


def printMsg(msg):
    friend = itchat.search_friends(userName=msg['FromUserName'])
    print('\n', msg.text)
    print('----------->', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
          'from:', friend['NickName'], '(remark:', friend['RemarkName'], ',UserName:', msg['FromUserName'], ')')


def RemindWords(inc):
    toRemindDict = reminder.remind()
    remindText = ''
    for word in toRemindDict:
        remindText += str(toRemindDict[word]) + ' '
        remindText += word + ' '
        remindText += dict.JustGetTranslation(word) + '\n'
    nuso_toUserName = UpdateUserName()
    itchat.send(remindText, toUserName=nuso_toUserName)
    t = Timer(inc, RemindWords, (inc,))
    t.start()


def RemindExams(inc):
    response = ExamReminder.check()
    if response['status']=='new':
        nuso_toUserName = UpdateUserName()
        itchat.send(
            ExamReminder.format_exam(response['examList']),
            toUserName=nuso_toUserName
        )
        print('已发送考试信息----------------------------------------')
        print(ExamReminder.format_exam(response['examList']))
    else:
        print('已查询考试信息，没有新的考试消息')

    t = Timer(inc, RemindExams, (inc,))
    t.start()


# 多线程
threads = []
t1 = threading.Thread(target=RemindWords, args=(5*60,))
threads.append(t1)
t2 = threading.Thread(target=RemindExams, args=(10*60,))
threads.append(t2)

if __name__ == '__main__':
    itchat.auto_login(hotReload=True, enableCmdQR=False)     # enableCmdQR=True
    LoadFriendList()
    # RemindWords(5 * 60)

    for t in threads:
        t.setDaemon(True)
        t.start()

    itchat.run()
