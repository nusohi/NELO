import requests
import json
from bs4 import BeautifulSoup
import os
dir_path = os.path.abspath(os.path.dirname(__file__))

cookie = 'TGC=eyJhbGciOiJIUzUxMiJ9.ZXlKNmFYQWlPaUpFUlVZaUxDSmhiR2NpT2lKa2FYSWlMQ0psYm1NaU9pSkJNVEk0UTBKRExVaFRNalUySW4wLi5fRVhJbmpPaVE5NzVnc1NHYjVQVnJRLlJyNm15MnhLNFhsN3VPODIxMXVGd3BSX01mTXJlQUpMTHRUdl9YMmtNREx0ZDg1dEtyblpDaEdneTBPaUxNMFgyQUVUSkc0UlpyZ25PRG9zLWlkbmx5blV3eXp2OC1HZkFxUjk4WGF4Sm53ZWpfZlo5OENZRng0S0FuTTdhR3YwWHFkN2dmeFU4bzdSUUg4UjVVeHNneGxXUUlRdGtnQ3Bhb19rNTVVTlU3OWQ5b3M4M0NWMV9LVVZJLXhGd1Nxa25VVTZ3UHFVSWpBUElFT3AwVWJzWDdEU2cyN0w3dG9tMGhfU2FZZ0Y4c2JmVFczdFNVUHY3SEtnRjlOYUlCMy0uLS0wenpJQlU0eEhJSEVsTk4tVV82QQ==.xppT1exc1EtdeqN1fTXSUBS7cHr71dWCm4td4jQA32venCOpFp6Ouqa3iJOAiXpe5WEyPfoZSW74CshNAsDT4w; cloud_sessionID=4c7330f7cfca85b563f5877728e2bd83; _csrf-cloud=e3d5075444007a0ea2cc42f4c53a186b0e88d38cc6b2f128fba00152600f87b0a%3A2%3A%7Bi%3A0%3Bs%3A11%3A%22_csrf-cloud%22%3Bi%3A1%3Bs%3A32%3A%22Tsq2MTKsaC5gt0Zr3PcSl3K3xiryzJFx%22%3B%7D'

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


class ExamReminder():

    @classmethod
    def check(self):
        self.LoadExams(self)
        last_len_exams = len(self.exams)

        html = DownloadHtml.get()
        examsList = ParseExamList.get(html)

        # cookie过期
        if examsList == None:
            return {
                'status' : 'wrong',
                'examList': []
            }

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
        text = f'查询到 {len(examList)} 条考试信息：\n'
        text += '------------------------------\n'
        for exam in examList:
            for key, value in exam.items():
                text += str(key) + ':' + str(value) + '\n'
            text += '------------------------------\n'
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
