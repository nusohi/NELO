import hashlib, time, random


class YouDaoUrl:
    def __init__(self):
        self.appKey = "ff889495-4b45-46d9-8f48-946554334f2a";
        self.appID = '6126c7938be5da5d'
        self._from = "en";
        self.to = "zh_CHS";
        self.query = "";
        self.sign = hashlib.md5()
        # sign = hashlib.md5()

        self.params = {};
        self.params['from'] = self._from;
        self.params['to'] = self.to;
        self.params['appKey'] = self.appKey;


    def GetUrl(self, query):
        self.query = query
        # self.salt = str(round(time.time()*1000))
        self.salt = str(random.randint(0,9))
        self.sign.update((self.appID + self.query + self.salt +self.appKey).encode())

        self.params['q'] = self.query
        self.params['salt'] = self.salt
        self.params['sign'] = self.sign;

        return self.getUrlWithQueryString(self.params)

    def getUrlWithQueryString(self, params) :
        url = 'https://openapi.youdao.com/api'
        url += '?q={}'.format(params['q'])
        url += '&from={}'.format(params['from'])
        url += '&to={}'.format(params['to'])
        url += '&appKey={}'.format(params['appKey'])
        url += '&salt={}'.format(params['salt'])
        url += '&sign={}'.format(params['sign'].hexdigest())
        return str(url);
