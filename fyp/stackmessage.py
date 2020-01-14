class StackMessage:
    def __init__(self):
        self.message=[]

    def getMessage(self,user,client):
        msg=""
        order=len(self.message)-1
        if order>-1:
            while order>-1:
                sub=self.message[order]
                if sub['user']==user and sub['client']==client:
                    msg=sub['msg']
                    break
                order-=1
        return msg


    def setMessage(self,user,client,msg):
        dic={}

        dic.setdefault("user",user)
        dic.setdefault("client", client)
        dic.setdefault("msg", msg)
        self.message.append(dic)


