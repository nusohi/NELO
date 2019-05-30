import re
import json
import requests


class ElecQuery():
    url = 'http://ecardwx.ujs.edu.cn/wechat/callinterface/queryElecRoomInfo.html'
    data = {
        'sno': '3170602082',
        'xxbh': 'synjones',
        'aid': '0030000000005401',
        'account': '137555',
        'area': r'{"area": "F区","areaname": ""}',
        'building': r'{"building": "5","buildingid": "5"}',
        'floor': r'{"floor": "","floorid": "5"}',
        'room': r'{"room": "","roomid": "516"}'
    }

    @classmethod
    def get(self):
        res = requests.post(self.url, data=self.data)
        return self.clean_data(self, res)
    
    def clean_data(self, res):
        data = json.loads(res.text)
        text = data['errmsg']
        digits = re.findall("\d+", text)
        format_text = str(digits[-2]) + ' 剩余电量: ' + str(digits[-1])
        return digits[-1], format_text


if __name__ == '__main__':
    elec, text = Html.get()
    print(text)