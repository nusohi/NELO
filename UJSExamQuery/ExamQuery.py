import requests
import json
from bs4 import BeautifulSoup
import os
dir_path = os.path.abspath(os.path.dirname(__file__))


class DownloadHtml():
    url = 'http://yun.ujs.edu.cn/jwgl/exam/mobile'
    cookies = {
        "TGC": "eyJhbGciOiJIUzUxMiJ9.ZXlKNmFYQWlPaUpFUlVZaUxDSmhiR2NpT2lKa2FYSWlMQ0psYm1NaU9pSkJNVEk0UTBKRExVaFRNalUySW4wLi5hdHNYTy1pU3VYMEItbmJheWgtN1VBLjBVM1FOaDBaLXpsYmljVGllUXotSzRWb0JjUmR2NlVmZTNjVDUzakwzNUJ0VmZsMl9LbEJ4aDJubmhDaVF6ZWRkR3FySFF4WmZGRVV5NnEtN0JDQVMtckpLQWktWjZvWG5PNWxiN180MWd0X1JKY1BJMWNsZDc1VGxtbzVZd3BJQjlsNmVpMUhJc0NMa3NRVVB6bHp3VV9mSTgwdGVkWlNNYVlGTjFRWW45bDYyZ3J5aWQ1XzBGUXZrQ2c0RDA1NjJwc0VZdkhXOVdzVVVrZmpHc0ltWU9vd0MycnZIWG9aWUNncjVhNjB2YVNpdTFHQmxDeWZnbTZzVTdrbkRuemwuZDdQTUFGMzl2VVptWllZUTV4NDlCdw==.6QzvgYiXM7ua_oEh1KX55eBL-Fbyb8yH5bUPYBfJgW2AbFdK_KPq6vPvVotffoZT9pgDDP7fiHrAXEoqyY0Twg",
        "cloud_sessionID": "d2b988a5fb171f6756dd8a33815d4dd7",
        "_csrf-cloud": "5deb661c274fdbf91b1bc6a0256333b24ec593dd74cd07af1925555330fb3d03a%3A2%3A%7Bi%3A0%3Bs%3A11%3A%22_csrf-cloud%22%3Bi%3A1%3Bs%3A32%3A%22qlpjW-kNhs-ar96lEj63GFnNwQdFcx_f%22%3B%7D"
    }

    @classmethod
    def get(self):
        html = requests.get(self.url, cookies=self.cookies)
        with open(dir_path + '/latest.html', 'w', encoding='utf-8') as file:
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

        with open(dir_path + '/ExamList.json', 'w', encoding='utf-8') as file:
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
        exam_file_path = dir_path + '/ExamList.json'
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
