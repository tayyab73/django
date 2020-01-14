import urllib,urllib2

class SMS:
    def __init__(self):
        
        self.username='tayyab103'
        self.password='40914'
        self.from_='BookIt.pk'

    def send(self,user,user_no,client_no,p_name):
        flag=False
        try:
            message = self.from_+"\n" + user + ":" + user_no + " \nis interesting to your property named \n" + \
                  p_name
            ms = {'message': message}
            url = "http://lifetimesms.com/plain?username=" + self.username + "&" \
                                                                    "password=" + self.password + "&to=" + client_no + "&from=" + self.from_ + "&" + urllib.urlencode(
                ms)

            req = urllib2.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/5.6.12860.7 Safari/537.36'})
            resp = urllib2.urlopen(req)
            if resp.getcode() == 200:
                flag=True
        except:
            flag=False
        return flag

    def send_code(self,phone,code):
        flag=False
        try:
            message = "Your security code is: "+code
            ms = {'message': message}
            url = "http://lifetimesms.com/plain?username=" + self.username + "&" \
                                                                    "password=" + self.password + "&to=" + phone + "&from=" + self.from_ + "&" + urllib.urlencode(
                ms)

            req = urllib2.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/5.6.12860.7 Safari/537.36'})
            resp = urllib2.urlopen(req)
            if resp.getcode() == 200:
                flag=True
        except:
            flag=False
        return flag
