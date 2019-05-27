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


@itchat.msg_register(itchat.content.TEXT, isGroupChat=True, isFriendChat=True)
def text_reply(msg):
    printMsg(msg)   # 控制台输出
    friend = itchat.search_friends(userName=msg['FromUserName'])
    if friend == None:
        chatroom_name = msg['User']['NickName'].strip('\'')
        friend=itchat.search_chatrooms(name=chatroom_name)[0]
    msgText = msg.text.strip()

    # 加入friend列表
    if msgText == FriendPass and not (friend['RemarkName'] in friendList or friend['NickName'] in friendList):
        if friend['RemarkName'] != '':
            AddNewFriend(friend['RemarkName'])
        else:
            AddNewFriend(friend['NickName'])
        
        print("-----------> new friend " + friend['RemarkName'])
        return "Welcome!"

    if friend['RemarkName'] in friendList or friend['NickName'] in friendList:
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
        if friend['RemarkName'] == 'nuso' :
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
    if not os.path.exists(FriendList):
        open(FriendList, 'w').close()
    with open(FriendList, 'r', encoding="UTF-8") as FriendListFile:
        list = FriendListFile.read().split('\n')
        list.remove('')
        for friend in list:
            friendList.append(friend)


def printMsg(msg):
    friend = itchat.search_friends(userName=msg['FromUserName'])
    if friend == None:
        chatroom_name = msg['User']['NickName'].strip('\'')
        friend=itchat.search_chatrooms(name=chatroom_name)[0]
    print('\n', msg.text)

    info_text = ''
    try:
        info_text += 'from:' + friend['NickName'] 
        info_text += '\t中的：' + msg['ActualNickName']
    except:
        pass
    print('----------->', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        , info_text
        , ')')


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


def RemindExams(inc, check_status=True):
    response = ExamReminder.check()
    if response['status'] != 'new' and check_status:
        print('已查询考试信息，没有新的考试消息')
    else:
        nuso_toUserName = UpdateUserName()
        itchat.send(
            ExamReminder.format_exam(response['examList']),
            toUserName=nuso_toUserName
        )
        print('已发送考试信息----------------------------------------')
        print(ExamReminder.format_exam(response['examList']))

    t = Timer(inc, RemindExams, (inc,))
    t.start()


# 多线程
threads = []
t1 = threading.Thread(target=RemindWords, args=(5*60,))
threads.append(t1)
t2 = threading.Thread(target=RemindExams, args=(10*60,))
threads.append(t2)
t3 = threading.Thread(target=RemindExams, args=(6*60*60,False,))
threads.append(t3)

if __name__ == '__main__':
    itchat.auto_login(hotReload=True, enableCmdQR=False)     # enableCmdQR=True
    LoadFriendList()
    # RemindWords(5 * 60)

    for t in threads:
        t.setDaemon(True)
        t.start()

    itchat.run()
