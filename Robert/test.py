import datetime
from threading import Timer

ToRemindWordListFile = r'io/ToRemindWordListFile.txt'


def remind(inc):
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

    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    print('wordList:', wordList)
    print('toRemindDict:', toRemindDict)
    print('laterRemindDict:', laterRemindDict)
    t = Timer(inc, remind, (inc,))
    t.start()


def BuildNextWordList(toRemindDict, laterRemindDict):
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
            file.write(
                key + ' #'
                + nextTime.strftime('%Y-%m-%d %H:%M')
                + ' #' + str(level) + '\n')


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


remind(2)
