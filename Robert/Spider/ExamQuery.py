import requests
import json
import datetime
import re
from bs4 import BeautifulSoup
import os
dir_path = os.path.abspath(os.path.dirname(__file__))
import sys 
sys.path.append("..") 
import Conf.conf


conf = Conf.conf.Conf()


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
    def get(cls):
        cookies = parse_cookie(conf.get('ExamCookie'))
        html = requests.get(self.url, cookies=cookies)
        return html.text


class ParseExamList():
    @classmethod
    def get(cls, html):
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
    def clean_old(cls, exam_list):
        new_exam_list = []
        today = datetime.datetime.now()

        date_pattern = re.compile(r'.*(\d{4}).(\d{2}).(\d{2}).*')   # 2019-04-18 2019年06月21

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
    def check(cls, clean_old=True):
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
    def format_exam(cls, examList):
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
