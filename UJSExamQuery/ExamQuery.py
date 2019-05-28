import requests
import json
from bs4 import BeautifulSoup
import os
dir_path = os.path.abspath(os.path.dirname(__file__))

cookie = 'TGC=eyJhbGciOiJIUzUxMiJ9.ZXlKNmFYQWlPaUpFUlVZaUxDSmhiR2NpT2lKa2FYSWlMQ0psYm1NaU9pSkJNVEk0UTBKRExVaFRNalUySW4wLi5Ta2xhUmVFRzNWN3RMcFkyck5SVmVnLmtSOEwyYlZ4UWxfZlRDYnBtR2xSZlRLM1FPX2w5Q1lJcWI2OTltT2M0NUVBYXJrWEZmbEx0aWtWbjJxY3oxU2k2VzhWQ0EyWnB6c092WnUwNkRkd1BCX1BaM3dfSFRTSVMxVkFGejJWT0h0bEI0RWRGa21yWEUxWm15RkZHclRiekxOd2paSkpIRTR0MUgtcFQ4UndDSFNMOVo1dkdJZW42TEkxeDVVUVNETkxxcFVBV3JvNTVraG94Wm9PNmZKWU0zLVlyVWwydUY0MkM4RUJYbXlfSzFNMVJCZFg3Y3A5NDZ0WHZ2bnl0bXhaZURjMTc3OUgtLVhkSWFTNUFJQ2UuT0ZCNW55SzdtTEtBLVVFMTRPQUpIdw==.-flM5OCKA4MGUCkmZ__3ib9oap_XPUZwt5bobNX13xXTm1eP3BAw5qmbNLzP6oqQtnLa9Yce9r-eKE37FaqFrw; cloud_sessionID=0cfbb0741a4a189e1f50b70220b6b880; _csrf-cloud=0f3e73b48c3e0377c1b017601c5ce0a787e4c64e09abb23f70a2a83206d86631a%3A2%3A%7Bi%3A0%3Bs%3A11%3A%22_csrf-cloud%22%3Bi%3A1%3Bs%3A32%3A%2260wr4Rbl2JXsgAaPZfY_oFyAt33Je_aM%22%3B%7D'

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
        with open(dir_path + '/io/latest.html', 'w', encoding='utf-8') as file:
            file.write(html.text)
        return html.text


class ParseExamList():
    @classmethod
    def get(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find_all('table')[0]

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


class ExamReminder():

    @classmethod
    def check(self):
        self.LoadExams(self)
        last_len_exams = len(self.exams)

        html = DownloadHtml.get()
        examsList = ParseExamList.get(html)

        # new exam info
        if self.CheckExams(self, examsList):
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
        text = ''
        for exam in examList:
            for key, value in exam.items():
                text += str(key) + ':' + str(value) + '\n'
            text += '\n'
        return text

    def CheckExams(self, examList):
        if len(self.exams) != len(examList):
            return False
        for i in range(len(self.exams)):
            if self.exams[i] != examList[i]:
                return False
        return True
        



    def LoadExams(self):
        # 创建文件夹及文件
        if not os.path.exists(dir_path + '/io'):
            os.mkdir(dir_path + '/io')
        exam_file_path = dir_path + '/io/ExamList.json'
        if not os.path.exists(exam_file_path):
            open(exam_file_path, 'w').close()
            self.exams=[]
            return
        
        with open(exam_file_path, 'r', encoding='utf-8') as file:
            self.exams_json = json.loads(file.read())
        if self.exams_json['exams'] != None:
            self.exams = self.exams_json['exams']
        else:
            self.exams = []


if __name__ == '__main__':
    res = ExamReminder.check()
