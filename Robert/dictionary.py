# coding="utf-8"
import re
import requests
import json
import datetime
from bs4 import BeautifulSoup
import baidufanyi
from conf import alphabetPath


class Dictionary():

    baidu = baidufanyi.BaiduFanyi()
    # 匹配单词和短语
    vocaPattern = re.compile(r"^[a-zA-Z]{2,15}$")

    def IsWord(self, text):
        return bool(re.match(self.vocaPattern, text))

    def IsWordOrPhrase(self, text):
        texts = re.split(r"\s+", text)
        for word in texts:
            if not self.IsWord(word):
                return False
        return True

    # 获取翻译的json 没有记录
    def GetTranslation(self, text):
        text = text.strip()
        url = self.baidu.GetUrl(text)
        html = requests.get(url)
        transJson = html.json()
        result = self.parseTransJson(transJson)
        # 记录单词text
        remindTime = datetime.datetime.now() + datetime.timedelta(hours=2)
        with open(alphabetPath, 'a+') as file:
            file.write(
                text + ' #' + remindTime.strftime('%Y-%m-%d %H:%M') + '\n')
        return result

    # 获取翻译的json
    def JustGetTranslation(self, text):
        text = text.strip()
        url = self.baidu.GetUrl(text)
        html = requests.get(url)
        transJson = html.json()
        result = self.parseTransJson(transJson)
        return result
    # 解析json

    def parseTransJson(self, transJson):
        trans = ''
        transList = []
        transList = transJson['trans_result']
        try:
            for transDict in transList:
                trans += transDict['dst'] + ' '
        except:
            print('查词出错')
            print(transJson)

        return trans


if __name__ == '__main__':
    dic = Dictionary()
    trans = dic.GetTranslation('hello')
    print(trans)
