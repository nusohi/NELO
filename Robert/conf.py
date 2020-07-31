'''
@Description: 
@Author: nuso
@LastEditors: nuso
@Date: 2019-05-27 14:16:19
@LastEditTime: 2020-07-31 10:44:40
'''

import os
import sys
from platform import system
PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__)))
PROJECT_PATH += '/'

IS_SERVER = system() == 'Linux'
enableCmdQR = False if not IS_SERVER else True

#  robert.py
FriendPass = '魁'
FriendList = PROJECT_PATH + r'io/FriendList.txt'
friendList = []
nuso_toUserName = '@70454dd54b296a0ae59557f90e5da44e81d52b02bbcf7fc92acaeccb938120a6'

# Reminder.py
ToRemindWordListFile = PROJECT_PATH + r'English/io/ToRemindWordListFile.txt'
AlphabetFile = PROJECT_PATH + r'English/io/alphabet.txt'
OldWordListFile = PROJECT_PATH + r'English/io/oldWordList.txt'

# dictionary.py
alphabetPath = PROJECT_PATH + r'English/io/alphabet.txt'

# weather.py
CityCodePath = PROJECT_PATH + r'Spider/io/CityCode.json'
CityNamePath = PROJECT_PATH + r'Spider/io/CityName.json'

# daydaywords.py
CONF = {
    'KaoYanWords': PROJECT_PATH + r'English/io/KaoYanWords.txt',
    '词汇表': PROJECT_PATH + r'English/io/词汇表.json',
}
