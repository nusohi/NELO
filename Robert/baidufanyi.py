#coding=utf-8
import http.client
import hashlib
from urllib import parse
import random, requests, json

class BaiduFanyi():
    appid = '20181208000245605'
    secretKey = 'DJ2IohZ7Z30LRysm_PEI'
    httpClient = None
    myurl = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
    fromLang = 'en'
    toLang = 'zh'

    def GetUrl(self, query):
        q = query
        salt = random.randint(32768, 65536)
        sign = self.appid + q + str(salt) + self.secretKey
        m1 = hashlib.md5()
        m1.update(sign.encode(encoding='utf-8'))
        sign = m1.hexdigest()
        self.myurl += '?appid=' + self.appid
        self.myurl += '&q='     + parse.quote(q)
        self.myurl += '&from='  + self.fromLang
        self.myurl += '&to='    + self.toLang
        self.myurl += '&salt='  + str(salt)
        self.myurl += '&sign='  + sign
        return self.myurl

if __name__=="__main__":
    bdfy = BaiduFanyi()
    url = bdfy.GetUrl('hello')
    print(url)
    html = requests.get(url)
    print(html.json())
