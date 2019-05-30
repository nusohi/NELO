import os
import sys
PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__)))
PROJECT_PATH += '\\'

IS_SERVER = False
enableCmdQR = False if not IS_SERVER else True

#  robert.py
FriendPass = '魁'
FriendList = PROJECT_PATH + r'io/FriendList.txt'
friendList = []
nuso_toUserName = '@70454dd54b296a0ae59557f90e5da44e81d52b02bbcf7fc92acaeccb938120a6'

# Reminder.py
ToRemindWordListFile = PROJECT_PATH + r'English/io/ToRemindWordListFile.txt'
AlphabetFile = PROJECT_PATH + r'English/io/alphabet.txt'
OldWordListFile = PROJECT_PATH+ r'English/io/oldWordList.txt'

# dictionary.py
alphabetPath = PROJECT_PATH + r'English/io/alphabet.txt'

# weather.py
CityCodePath = PROJECT_PATH + r'Spider/io/CityCode.json'
CityNamePath = PROJECT_PATH + r'Spider/io/CityName.json'