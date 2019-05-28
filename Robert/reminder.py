import datetime
import re
import os
from threading import Timer
from conf import ToRemindWordListFile, AlphabetFile, OldWordListFile



def remind():
    BuildToRemindFile()
    with open(ToRemindWordListFile, 'r', encoding='utf-8') as file:
        wordList = file.read().split('\n')
        wordList.remove('')
    toRemindDict = {}
    laterRemindDict = {}
    for wordLine in wordList:
        words = wordLine.split(' #')
        word = words[0]
        nextTime = datetime.datetime.strptime(words[1], '%Y-%m-%d %H:%M')
        level = int(words[2])
        if datetime.datetime.now() > nextTime:
            toRemindDict[word] = level
        else:
            laterRemindDict[word] = [words[1], level]

    # 提醒完要存进文件的
    BuildNextWordList(toRemindDict, laterRemindDict)

    print('------------------------')
    print('| ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    print('| wordList:', len(wordList))
    print('| toRemindDict:', len(toRemindDict))
    print('| laterRemindDict:', len(laterRemindDict))
    print('------------------------')
    
    return toRemindDict


def BuildToRemindFile():
    wordDict = {}
    if not os.path.exists(AlphabetFile):
        open(AlphabetFile, 'w').close()

    # 从alpha中取
    with open(AlphabetFile, 'r', encoding='utf-8') as alphaFile:
        wordList = alphaFile.read().split('\n')
        wordList.remove('')
    with open(AlphabetFile, 'w', encoding='utf-8') as alphaFile:
        alphaFile.write('')
    # 整理数据
    for line in wordList:
        words = line.split(' #')
        words[1] = words[1].replace('@', '')
        wordDict[words[0]] = words[1]
    # 放到ToRemind中去
    with open(ToRemindWordListFile, 'a+', encoding='utf-8') as toRemindFile:
        for word in wordDict:
            toRemindFile.write(word + ' #' + wordDict[word] + ' #' + '1\n')


def BuildNextWordList(toRemindDict, laterRemindDict):
    oldWordList = []
    with open(ToRemindWordListFile, 'w', encoding='utf-8') as file:
        # 还没到时间的单词们
        for key in laterRemindDict:
            file.write(
                key + ' #'
                + laterRemindDict[key][0] + ' #'
                + str(laterRemindDict[key][1]) + '\n')
        # 此轮已提醒过的
        for key in toRemindDict:
            level = toRemindDict[key]
            nextTime = switch[level]()
            level += 1
            if(level == 5):
                oldWordList.append(key)
            else:
                file.write(
                    key + ' #'
                    + nextTime.strftime('%Y-%m-%d %H:%M')
                    + ' #' + str(level) + '\n')
    with open(OldWordListFile, 'a+', encoding='utf-8'):
        for word in oldWordList:
            file.write(
                word + ' #'
                + datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                + '\n')


def case1():
    return datetime.datetime.now() + datetime.timedelta(hours=2)


def case2():
    return datetime.datetime.now() + datetime.timedelta(hours=8)


def case3():
    return datetime.datetime.now() + datetime.timedelta(days=1)


def case4():
    return datetime.datetime.now() + datetime.timedelta(days=2)


switch = {
    1: case1,
    2: case2,
    3: case3,
    4: case4
}
