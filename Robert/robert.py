import os
import sys
import itchat
import threading
import time
import json
import re
import random
from threading import Timer
path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(path)

from Spider.ExamQuery import *  # import ExamQuery
from Spider.ElecQuery import *
from Spider import weather
from English import dictionary
from English import reminder
from English import daydaywords
from conf import FriendPass, FriendList, friendList, nuso_toUserName, enableCmdQR
import Conf


conf = Conf.conf.Conf()

# 查天气
wea = weather.Weather()
# 查单词
dict = dictionary.Dictionary()
# 每日单词提醒
daydayword = daydaywords.DayDayWord()


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

    # 消息处理 - 在 friendList 上的人
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

        # 有'魁'字 -> 控制信息
        if friend['RemarkName'] == 'nuso' and msgText.startswith('魁'):
            msgText = msgText.strip('魁').strip()

            keys = msgText.split(' ')
            confKeywords = ['配置', 'conf']
            keyIntersection = [i for i in keys if i in confKeywords]
            if len(keyIntersection) != 0:
                allConfKeywords = ['all', '啊']
                keyIntersection = [i for i in keys if i in allConfKeywords]
                if len(keyIntersection) != 0:
                    return conf.show(all=True)
                else:
                    return conf.show()

            return ControlHandle(msgText)

        # 查询考试信息
        if msgText.startswith('考试'):
            response = ExamReminder.check()
            ExamInfo = ExamReminder.format_exam(response['examList'])
            if friend['RemarkName'] == 'nuso' :
                print('主动查询并发送考试信息' + '-' * 30 + f'\n{ExamInfo}')
                return ExamInfo
        
        # 查询电费信息
        if msgText.startswith('电费'):
            left_elec, msg = ElecQuery.get()
            if friend['RemarkName'] == 'nuso' :
                print('主动查询并发送电费信息' + '-' * 30 + f'\n{msg}')
                return msg

        # 最后没有关键词直接查天气
        cityName = wea.FindCityName(msgText)
        if(cityName):
            return wea.getWeatherByName(cityName)
        if friend['RemarkName'] == 'nuso' :
            return 'server received...' 
    else:
        print("-----------> 不在friendList的人")
        print('-----------> friend list :', friendList)


def SendToNuso(msg):
    _nuso_toUserName = UpdateUserName()
    itchat.send(msg, toUserName=_nuso_toUserName)


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
        _nuso_toUserName = UpdateUserName()
        itchat.send(
            ExamReminder.format_exam(response['examList']),
            toUserName=_nuso_toUserName
        )
        print('已发送考试信息----------------------------------------')
        print(ExamReminder.format_exam(response['examList']))

    t = Timer(inc, RemindExams, (inc,))
    t.start()

def __RemindExams__(inc, check_status=True):
    while(True):
        if not conf.get('AllowRemindExam'):
            time.sleep(inc)
            continue

        response = ExamReminder.check()
        _nuso_toUserName = UpdateUserName()

        if response['status'] == 'wrong':
            itchat.send(
                'cookie 过期，快更新！',
                toUserName=_nuso_toUserName
            )
            print('----> cookie 过期，未能正常查询.')

        elif response['status'] != 'new' and check_status:
            print('已查询考试信息，没有新的考试消息')

        else:
            itchat.send(
                ExamReminder.format_exam(response['examList']),
                toUserName=_nuso_toUserName
            )
            print('已发送考试信息----------------------------------------')
            print(ExamReminder.format_exam(response['examList']))
            
        time.sleep(inc)

def RemindElec(inv):
    while(True):
        if not conf.get('AllowRemindElec'):
            time.sleep(inc)
            continue

        left_elec, msg = ElecQuery.Run()
        _nuso_toUserName = UpdateUserName()
        if int(left_elec) < 30:
            itchat.send(msg, toUserName=_nuso_toUserName)

        print('-------------电费查询----')
        print(msg)
        time.sleep(inv)

def RemindDayDayWord(min, max):
    while(True):
        if 90000 < int(time.strftime("%H%M%S")) < 230000 and conf.get('AllowDailyWord'):
            words = daydayword.Get(conf.get('DailyWordCount'))
            _nuso_toUserName = UpdateUserName()
            itchat.send(words, toUserName=_nuso_toUserName)

        time.sleep(random.randint(min, max))

def ControlHandle(data):
    kv = data.split('\n')
    conf.put(kv[0], kv[1])
    print(f'ControlHandle 添加配置[len={len(kv)}]：{kv[0]} : {kv[1]}')
    return f'ControlHandle 添加配置[len={len(kv)}]：{kv[0]} : {kv[1]}'

if __name__ == '__main__':
    # itchat 登陆
    itchat.auto_login(hotReload=True, enableCmdQR=enableCmdQR)     # enableCmdQR=True

    # 加载作用对象列表
    LoadFriendList()

    # 多线程---（提醒事务）
    threads = []
    t1 = threading.Thread(target=RemindWords, args=(5*60,))
    threads.append(t1)
    t2 = threading.Thread(target=__RemindExams__, args=(20*60,))
    threads.append(t2)
    t3 = threading.Thread(target=__RemindExams__, args=(24*60*60,False,))
    threads.append(t3)
    t4 = threading.Thread(target=RemindElec, args=(1*60*60,))
    threads.append(t4)
    t5 = threading.Thread(target=RemindDayDayWord, args=(45*60, 1*60*60,))
    threads.append(t5)

    for t in threads:
        t.setDaemon(True)
        t.start()

    itchat.run()
