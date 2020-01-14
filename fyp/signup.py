from django.shortcuts import render
from django.http import request,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dbconfig import DataBase
from reader import Reader
class SignUp:
    def __init__(self,flag,db_instance):
        self.reader=Reader()
        self.db_flag=flag
        self.db_instance=db_instance
        self.for_result=True

    @csrf_exempt
    def checknewuser(self,request):
        data={}
        try:
            if request.method=='POST':
                sql="select * from client where username='"+request.POST['user']+"'"

                if self.db_flag:
                    obj_cursor = self.db_instance.cursor()
                    flag,result=self.reader.execute_query(self.for_result,obj_cursor,sql)
                    if flag:
                        if len(result)==0:
                            data={'is_taken':'Username Ok'}
                        else:
                            data = {'is_taken': 'This username exist, choose another username'}
                    else:
                        data = {'is_taken': 'Storage/Database error during processing.'}
                else:
                    data = {'is_taken': 'Database connection error.'}
            else:
                data = {'is_taken': 'Server connection error during sending information'}
        except Exception,e:
            data={"is_taken":"Error due to "+str(e)}
        return JsonResponse(data)


    def register(self,request):
        try:
            co=self.reader.getData('Mobile Code')
            return render(request,'register.html',{'error':'','logvalue':0,'fname':'' ,'status':-1,'code':co})
        except Exception,e:
            return render(request,'register.html',{'error':'Error due to '+str(e),'logvalue':0,'fname':'' ,'status':-1,'code':co})