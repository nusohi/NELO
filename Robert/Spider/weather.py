# coding="utf-8"
if __name__ == '__main__':
    import os
    import sys
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.append(path)
import re
import requests
import json
import string
from bs4 import BeautifulSoup
from conf import CityCodePath, CityNamePath


class Weather():
    weatherCode = ['天气', 'weather', '下雨', '下雪', '有雨', '有雪']
    cityList = []
    cityNameList = []

    def __init__(self):
        self.HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 ''(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        self.LoadJson()

    def LoadJson(self):
        with open(CityNamePath, 'r', encoding="UTF-8") as cityNameFile:
            cityNameDict = json.load(cityNameFile)
            self.cityNameList = cityNameDict["cityNameList"]
        with open(CityCodePath, 'r', encoding="UTF-8") as cityFile:
            cityDict = json.load(cityFile)
            self.cityList = cityDict["cityList"]

    def FindCityName(self, txt='镇江'):
        for cityName in self.cityNameList:
            if re.search(cityName, txt):
                return cityName

    def GetCityCode(self, cityName):
        for city in self.cityList:
            if city["cityName"] == cityName:
                return city["code"]

    def ParseWeather(self, cityCode=101190301):
        url = 'http://www.weather.com.cn/weather/%s.shtml' % cityCode
        html = requests.get(url, self.HEADERS)  # , self.HEADERS
        html.encoding = 'utf-8'
        weather = ''
        # , from_encoding='utf-8'
        soup = BeautifulSoup(html.text, 'html.parser')
        for day in soup.find('div', {'id': '7d'}).find('ul').find_all('li'):
            date = day.find('h1').text
            detail = day.find_all('p')
            title = detail[0].text
            temphigh = str(detail[1].find('span')).split(
                "</span>")[0].lstrip("<span>")
            templow = detail[1].find('i').text
            windDirection = detail[2].find('span')['title']
            windLevel = detail[2].find('i').text
            # weather += (date + title+'\t['+templow+'~'+temphigh+'] '+ windDirection + windLevel+'\n')
            data = date.split('（')[0]
            weather += format(date.split('（')[0], '<3')
            weather += format(templow.split('℃')[0], '>4')
            weather += '~'
            if temphigh == 'None':
                weather += format('', '<5')
            else:
                weather += format(temphigh, '<4')
            weather += title + '\n'
        return weather

    def getWeather(self, msg):
        cityName = self.FindCityName(msg)
        if cityName == None:
            cityName = '镇江'
        weather = self.getWeatherByName(cityName)
        return weather

    def getWeatherByName(self, cityName):
        cityCode = self.GetCityCode(cityName)
        weather = cityName + ' 7天天气预报:\n'
        weather += self.ParseWeather(cityCode)
        return weather


if __name__ == '__main__':
    weather = Weather()
    wea = weather.getWeather("镇江")
    print(wea)
