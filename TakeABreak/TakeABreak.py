import time
import webbrowser
import os

# 时间间隔 & 提醒次数
t = 20*60           # 20min 20-20-20原则
total = 30          # 30次 共10小时

# html内容
html_content = r'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport"content="width=device-width, initial-scale=1.0"><meta http-equiv="X-UA-Compatible"content="ie=edge"><title>Take A Break</title><style>body{margin:0;position:relative}img{height:auto;width:auto\9;width:100%}.center{position:absolute;margin:auto;padding:auto;width:100%;text-align:center}.text{font-size:60px;color:rgb(255,255,255);width:100%;font-family:PMingLiu,MingLiU,Microsoft YaHei}.time{font-size:200px;color:rgb(255,255,255);width:100%;height:400px;line-height:400px}</style></head><body onload="time()"><div class="center"><div class="text time">20</div><div class="text">远眺</div></div><img src="https://uploadbeta.com/api/pictures/random/?key=BingEverydayWallpaperPicture"/></body><script type="text/javascript">var wait=20;function time(){document.getElementsByClassName("time")[0].innerHTML=wait.toString();if(wait==0){texts=document.getElementsByClassName("text");for(const index in texts){if(texts.hasOwnProperty(index)){const text=texts[index];text.innerHTML=""}}}else{wait--;setTimeout(function(){time()},1000)}}</script></html>'''

# 获取文件绝对路径
Dir_Path = os.path.dirname(os.path.abspath(__file__))
html_file_path = os.path.join(Dir_Path, 'TakeABreak.html')

# 创建html文件（如果不存在的话）
if not os.path.isfile(html_file_path):
    print('正在创建html文件...')
    with open(html_file_path, 'w', encoding='utf-8') as file:
        file.write(html_content)
        print('创建完成：',html_file_path)

# 浏览器打开本地html需要的地址
html_file = 'file:///'+html_file_path

# 计时 & 计数
flag = 0
while (flag < total):
    time.sleep(t)
    flag += 1
    webbrowser.open(html_file_path, new=0, autoraise=True)
    print('第', str(flag), "次休息")
print("程序结束")