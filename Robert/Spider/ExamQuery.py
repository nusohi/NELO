import requests
import json
import datetime
from bs4 import BeautifulSoup
import os
dir_path = os.path.abspath(os.path.dirname(__file__))

cookie = '_csrf-cloud=85a286079bd88bb0cb09b9b4ece0ce7bb0169d5af5221e4ef2b9b0b998374c2fa%3A2%3A%7Bi%3A0%3Bs%3A11%3A%22_csrf-cloud%22%3Bi%3A1%3Bs%3A32%3A%22Ygm3DQnjzGApCZAAl12Iyij9jDDZ-z7C%22%3B%7D; TGC=eyJhbGciOiJIUzUxMiJ9.ZXlKNmFYQWlPaUpFUlVZaUxDSmhiR2NpT2lKa2FYSWlMQ0psYm1NaU9pSkJNVEk0UTBKRExVaFRNalUySW4wLi5Kcm9ReHkxYTd1bVk5QzRaQVFpNzB3LlNvRXFySmttSmdmVFpZWE1rSmlVZko1TnBhNW85cVpSZmN3MTM5Zmo0R21UbXdFNTVDOVpLTi1FYzlxNFJ4Q24xSnhSZEZSVVktRkFOaXRzU3k2VkRqZUlaLVZzSkdiTlNrY0JNMUdWaENiTndTdUFVTF9oaGVEck9xQk5rRVdqWkVCQmRPQWlOSkRBWTZQOUxwUVJLTTg0UmJycldTcnAtUDJ2OW1nbkpIU0RmN0t1V0p3M2V5ZlAtM2IwZzNRUFRrVEVqOGMxSVkzb1BPVWtubnR1dkp3czZMcWd1RzY2QmVYU1ZuUTc4Q19jQWlNYU1jell3ZkhCWXJRMUhmaUQuNnhsa2Q5Rm4tSVRqQk5yaTV5VlpvZw==.YuUTzk4mFw2lDsE1sQohhQYZa8aIU1kqCudfNoTg1NCvC-X055H9SEaeQCEpynOHovrbex6QOs25oeQKwMbmSA; cloud_sessionID=234f5fb57377088c8cf6f4c9a869408c'

def parse_cookie(cookie):
    cookies_dict = {}
    for item in cookie.strip().split(';'):
        key, value = item.split('=', 1)
        cookies_dict[key] = value
    return cookies_dict

class DownloadHtml():
    url = 'http://yun.ujs.edu.cn/jwgl/exam/mobile'
    cookies = parse_cookie(cookie)

    @classmethod
    def get(self):
        html = requests.get(self.url, cookies=self.cookies)
        return html.text


class ParseExamList():
    @classmethod
    def get(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        _table = soup.find_all('table')

        # 如果没有表格---cookie过期
        if len(_table) == 0:
            return None

        table = _table[0]

        # Table Head
        table_heads = []
        for th in table.find_all('th'):
            table_heads.append(th.text)

        # Table Body : Exams
        exams = []
        for tr in table.find('tbody').find_all('tr'):
            td = tr.find_all('td')
            if(td[1].text != ''):
                exam = {}
                exam[table_heads[0]] = td[0].text
                exam[table_heads[1]] = td[1].text
                exam[table_heads[2]] = td[2].text
                exams.append(exam)

        exam_json = {'exams': exams}

        with open(dir_path + '/io/ExamList.json', 'w', encoding='utf-8') as file:
            json_str = json.dumps(exam_json, indent=4, ensure_ascii=False)
            file.write(json_str)

        return exams

    @classmethod
    def clean_old(self, exam_list):
        new_exam_list = []
        today = datetime.datetime.now()

        for exam in exam_list:
            date_str = exam['时间'].split('(')[1].split(')')[0]     # 2019-04-18
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            if date > today:
                new_exam_list.append(exam)
        
        return new_exam_list



class ExamReminder():

    @classmethod
    def check(self, clean_old=True):
        oldList = self.LoadExams(self)

        html = DownloadHtml.get()
        examsList = ParseExamList.get(html)

        # cookie过期
        if examsList == None:
            return {
                'status' : 'wrong',
                'examList': []
            }

        # 清洗已考的
        if clean_old:
            examsList = ParseExamList.clean_old(examsList)
            oldList = ParseExamList.clean_old(oldList)

        # new exam info
        if examsList == oldList:
            return {
                'status': 'latest',
                'examList': examsList
            }
        else:
            return {
                'status': 'new',
                'examList': examsList
            }

    @classmethod
    def format_exam(self, examList):
        text = f'查询到 {len(examList)} 条考试信息：\n'
        text += '------------------------------\n'
        for exam in examList:
            for key, value in exam.items():
                text += str(key) + ':' + str(value) + '\n'
            text += '------------------------------\n'
        return text

    def LoadExams(self):
        # 创建文件夹及文件
        if not os.path.exists(dir_path + '/io'):
            os.mkdir(dir_path + '/io')
        exam_file_path = dir_path + '/io/ExamList.json'
        if not os.path.exists(exam_file_path):
            open(exam_file_path, 'w').close()
            self.exams=[]
            return []
        
        with open(exam_file_path, 'r', encoding='utf-8') as file:
            self.exams_json = json.loads(file.read())
        if self.exams_json['exams'] != None:
            self.exams = self.exams_json['exams']
        else:
            self.exams = []
        
        return self.exams


if __name__ == '__main__':
    res = ExamReminder.check()
    print(res)
