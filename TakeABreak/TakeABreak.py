import time
import webbrowser
import os


class Break:
    def __init__(self, _interval=20*60, _total=30):
        # 时间间隔 & 提醒次数
        self.interval = _interval   # 20*60 20min 20-20-20原则
        self.total = _total         # 30次 -> 10小时

        # html内容
        self.html_content = r'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport"content="width=device-width, initial-scale=1.0"><meta http-equiv="X-UA-Compatible"content="ie=edge"><title>Take A Break</title><style>body{margin:0;position:relative}img{height:auto;width:auto\9;width:100%}.center{position:absolute;margin:auto;padding:auto;width:100%;text-align:center}.text{font-size:60px;color:rgb(255,255,255);width:100%;font-family:PMingLiu,MingLiU,Microsoft YaHei}.time{font-size:200px;color:rgb(255,255,255);width:100%;height:400px;line-height:400px}</style></head><body onload="time()"><div class="center"><div class="text time">20</div><div class="text">远眺</div></div><img src="https://uploadbeta.com/api/pictures/random/?key=BingEverydayWallpaperPicture"/></body><script type="text/javascript">var wait=20;function time(){document.getElementsByClassName("time")[0].innerHTML=wait.toString();if(wait==0){texts=document.getElementsByClassName("text");for(const index in texts){if(texts.hasOwnProperty(index)){const text=texts[index];text.innerHTML=""}}}else{wait--;setTimeout(function(){time()},1000)}}</script></html>'''

        # 获取文件绝对路径
        self.Dir_Path = os.path.dirname(os.path.abspath(__file__))
        self.html_file_path = os.path.join(self.Dir_Path, 'TakeABreak.html')

        # 创建html文件（如果不存在的话）
        if not os.path.isfile(self.html_file_path):
            print('正在创建html文件...')
            with open(self.html_file_path, 'w', encoding='utf-8') as file:
                file.write(self.html_content)
                print('创建完成：', self.html_file_path)

    def run(self):
        print('时间间隔:', self.interval, 's  提醒次数:', self.total)
        print('程序开始...')

        # 浏览器打开本地html需要的地址
        html_file = 'file:///' + self.html_file_path

        # 计时 & 计数
        flag = 0
        while (flag < self.total):
            time.sleep(self.interval)
            flag += 1
            webbrowser.open(self.html_file_path, new=0, autoraise=True)
            print('第', str(flag), "次休息")
        print("程序结束")


if __name__ == '__main__':
    TakeABreak = Break(_total=100)
    TakeABreak.run()
