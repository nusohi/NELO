import requests
import json
import datetime
import re
from bs4 import BeautifulSoup
import os
dir_path = os.path.abspath(os.path.dirname(__file__))

cookie = 'TGC=eyJhbGciOiJIUzUxMiJ9.ZXlKNmFYQWlPaUpFUlVZaUxDSmhiR2NpT2lKa2FYSWlMQ0psYm1NaU9pSkJNVEk0UTBKRExVaFRNalUySW4wLi44bGRPcEZ2WEtHNVNLcHZNUlkzREJnLmpld0V5LVdEcFJfX20yaGFqY21ySGxKM1MzM3RUaTlLWjdmV3pxcVNVc3dvVUx3MDB1QWJUdmhkMXBEaFhWOUNUaWVXTUZuUV9YblRuTHJDSmZWM1lqY2RVai0xdWwzcHhWbERhMk54QTVpaUtXUlVzVzZFWkN5dFJ2a09lUHZtQ1FTYUtLSVBVSjhxajA1NTY0MVFZR25Mb1hrWlIwYVVuRXFGMDFURmZhU1AwQzU0WlctaEdjMnFoSlFXYk5ZWXcwOHdsMHhhVFFRTGx1TWVIYjBFWFFPX2NNOEIxaldBNDlZY1B0VlFMZUNsamFtYXBuZENfTTV6dkNMNHp6OXYuSWxuUl9KVWQ3czY4Q0JERjJubDJ3Zw==.o02_BpU2TqOAEGFOgHSyK5ZkXA6eYkfTdLhhFXaVJwkvq8-93na7G_phka7f2J6XKpzusrQxANYX2Dtt4PgobQ; cloud_sessionID=752de73dcbbcd04086318d5a7aa96a63; _csrf-cloud=11bca40db57d83f7638439470c37b38e6ca2b0116781bf5944fb1a32d8f72fc9a%3A2%3A%7Bi%3A0%3Bs%3A11%3A%22_csrf-cloud%22%3Bi%3A1%3Bs%3A32%3A%22Zfo69IMkwIG155hI51IMV4vQEEDWJiO9%22%3B%7D'

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

        date_pattern = re.compile(r'(\d{4}).(\d{2}).(\d{2})')   # 2019-04-18 2019年06月21

        for exam in exam_list:
            match = date_pattern.match(exam['时间'])
            if match == None:
                continue
            date_group = match.groups()
            date = datetime.datetime(int(date_group[0]), int(date_group[1]), int(date_group[2]))

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
