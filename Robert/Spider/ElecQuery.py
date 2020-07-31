'''
@Description: 
@Author: nuso
@LastEditors: nuso
@Date: 2019-05-30 13:14:15
@LastEditTime: 2020-07-31 08:42:20
'''
import re
import json
import requests


class ElecQuery():
    url = 'http://ecardwx.ujs.edu.cn/wechat/callinterface/queryElecRoomInfo.html'
    data = {
        'sno': '3170305000',
        'xxbh': 'synjones',
        'aid': '0030000000005401',
        'account': '137333',
        'area': r'{"area": "F区","areaname": ""}',
        'building': r'{"building": "5","buildingid": "5"}',
        'floor': r'{"floor": "","floorid": "5"}',
        'room': r'{"room": "","roomid": "516"}'
    }

    @classmethod
    def Run(cls):
        try:
            res = requests.post(cls.url, data=cls.data)
            return cls.clean_data(res)
        except:
            print("电费查询错误，POST请求失败!")
            return 0, "电费查询错误，POST请求失败!"

    def clean_data(self, res):
        data = json.loads(res.text)
        text = data['errmsg']
        digits = re.findall("\d+", text)
        format_text = str(digits[-2]) + ' 剩余电量: ' + str(digits[-1])
        return digits[-1], format_text


if __name__ == '__main__':
    elec, text = ElecQuery.Run()
    print(text)
