from django.shortcuts import render
from django.http import request,JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from reader import Reader
from mail_ftn import MailService
from random import randint


class RecoveryPassword:
    def __init__(self,flag,db_instance):
        self.db_flag=flag
        self.db_instance=db_instance
        self.reader=Reader()
        self.mail=MailService()
        self.for_result=True
        self.empty_result=False


    def forgetpassword(self,request):
        try:
            return render(request,'forget-password.html',{'error':'','logvalue':0,'fname':'' ,'status':-1})
        except Exception,e:
            return render(request,'forget-password.html',{'error':str(e),'logvalue':0,'fname':'' ,'status':-1})

    def generate_code(self,username,code):
        resp_flag=False
        sql="select * from recovery_password where username='"+username+"' and scode="+str(code)
        try:

            if self.db_flag:
                cur=self.db_instance.cursor()
                flag,result=self.reader.execute_query(self.for_result,cur,sql)
                if flag:
                    if len(result)==0:
                        resp_flag=True
        except Exception,e:
            resp_flag=False
        return resp_flag



    def savepassword(self,username,scode):
        resp_flag=False
        try:
            sql="select password from client where username='"+username+"'"
            if self.db_flag:
                cursor=self.db_instance.cursor()
                flag,result=self.reader.execute_query(self.for_result,cursor,sql)
                if flag:
                    if len(result)>0:
                        sql="insert into recovery_password (username,old_password,scode) values ('"+username+"','"+result[0][0]+"',"+str(scode)+")"
                        flag,result=self.reader.execute_query(self.empty_result,cursor,sql)
                        if flag:
                            self.db_instance.commit()
                            resp_flag=True
        except Exception,e:
            resp_flag= False
        return resp_flag


    def checkdb(self,username):
        check=False
        try:
            sql="select new_password from recovery_password where username='"+username+"'"
            if self.db_flag:
                cursor=self.db_instance.cursor()
                flag,result=self.reader.execute_query(self.for_result,cursor,sql)
                if len(result)>0:
                    if result[0][0]!=None:
                        check=True
        except Exception,e:
            check=False
        return check


    def recoverypassword(self,request):
        error=""
        try:
            if request.method=='POST':
                sql="select email from client where username='"+request.POST['username']+"'"
                check=self.checkdb(request.POST['username'])
                if check==False:
                    return render(request,'recovery-password.html',{'error':'','logvalue':0,'fname':'' ,'status':-1})
                if self.db_flag:
                    db_cursor = self.db_instance.cursor()
                    flag,result=self.reader.execute_query(self.for_result,db_cursor,sql)
                    if len(result)==1:
                        email=result[0][0]
                        if email!=None:
                            argu=0
                            while(True):
                                code = randint(100000, 999999)
                                if self.generate_code(request.POST['username'],code):
                                    argu=code
                                    break
                                else:
                                    continue
                            try:
                                if self.mail.sent_mail_client(email,argu,''):
                                    if self.savepassword(request.POST['username'],argu):
                                        return render(request,'recovery-password.html',{'error':'','logvalue':0,'fname':'' ,'status':-1})
                                    else:
                                        error="Sorry, Storage/Database error while saving information."
                                else:
                                    error = "Sorry, processing error while sending verification code."
                            except Exception,e:
                                error="Sorry, something is wrong during processing."
                        else:
                            error = "Sorry, email does not found for that Username."
                    else:
                        error = "Sorry, account's username does not found for requested client."
                else:
                    error = "Sorry, storage/database connection error found."
            else:
                error = "Sorry, recovery password page cannot access directly."
        except Exception,e:
            error = "Sorry, something is wrong during processing."
        return render(request, 'forget-password.html', {'error':error,'logvalue':0,'fname':'' ,'status':-1})


    @csrf_exempt
    def securitycode(self,request):
        data={}
        try:
            if request.method == 'POST':
                sql = "select * from recovery_password where scode=" + str(request.POST['scode'])

                if self.db_flag:
                    obj_cursor=self.db_instance.cursor()
                    flag,result=self.reader.execute_query(self.for_result,obj_cursor,sql)
                    if flag:
                        if len(result)!=0:
                            data = {'is_taken': ''}
                        else:
                            data = {'is_taken': 'Sorry, no security code found'}
                    else:
                        data = {'is_taken': 'Sorry, processing error found'}
                else:
                    data={'is_taken':'Database connection error found'}
            else:
                data = {'is_taken': 'error during data sending to server'}
        except Exception, e:
            data = {'is_taken': str(e)}
        return JsonResponse(data)



    def finalrecovery(self,request):
        error=""
        try:
            if request.method=='POST':
                if request.POST['securecode']!='':
                    if request.POST['new_password']!='' and len(request.POST['new_password'])>7:
                        if request.POST['con_password'] != '' and len(request.POST['con_password'])>7:
                            if request.POST['new_password'] == request.POST['con_password']:
                                sql="select new_password,username from recovery_password where scode="+str(request.POST['securecode'])

                                if self.db_flag:
                                    cursor=self.db_instance.cursor()
                                    flag,result=self.reader.execute_query(self.for_result,cursor,sql)
                                    if flag:
                                        if len(result)==1:
                                            if result[0][0]==None:
                                                username=result[0][1]
                                                sql="update recovery_password set new_password='"+\
                                                    request.POST['new_password']+"', rdate=(select current_date from dual) where username='"+username+"'"
                                                try:
                                                    flag,result=self.reader.execute_query(self.empty_result,cursor,sql)
                                                    if flag:
                                                        self.db_instance.commit()
                                                        sql="update client set password='"+request.POST['new_password']+"' where username='"+username+"'"
                                                        flag,result=self.reader.execute_query(self.empty_result,cursor,sql)
                                                        if flag:
                                                            self.db_instance.commit()
                                                            return render(request, 'login.html',
                                                                      {'error': '','success':'Your password has been changed. Please login again.',
                                                               '        logvalue': 0, 'fname': '', 'status': -1})
                                                        else:
                                                            error = "Sorry, processing error found."
                                                    else:
                                                        error = "Sorry, processing error found."
                                                except Exception,e:
                                                    error="Sorry, something is wrong during processing."
                                            else:
                                                error = "Sorry, username is not recognize in system's storage."
                                        else:
                                            error = "Sorry, username is not exist in system's storage."
                                    else:
                                        error = "Sorry, something is wrong during processing."
                                else:
                                    error = "Sorry, something is wrong during storage connection."
                            else:
                                error = "Sorry, please use same password for new and confirm password fields."
                        else:
                            error = "Sorry, please fill confirm password at least 8 character."
                    else:
                        error = "Sorry, please fill new password at least 8 character."
                else:
                    error = "Sorry, please fill security code field."
            else:
                error = "Sorry, something is wrong during sending information."
        except Exception,e:
            error = "Sorry, something is wrong during processing."
        return render(request,'recovery-password.html',{'error':error,'logvalue':0,'fname':'' ,'status':-1})