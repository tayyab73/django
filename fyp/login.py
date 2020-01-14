from django.shortcuts import render
from django.http import request,JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from dbconfig import DataBase
from reader import Reader
from mail_ftn import MailService
from random import randint


class Login:
    def __init__(self,flag,db_instance):
        self.mail=MailService()
        self.db_flag=flag
        self.db_instance=db_instance
        self.reader=Reader()
        self.for_result=True
        self.empty_result=False

    def checkusername(self,user):
        check=False
        try:
            sql="select * from client where username='"+user+"'"
            if self.db_flag:
                cursor=self.db_instance.cursor()
                flag,results=self.reader.execute_query()
                if flag:
                    if len(results)!=0:
                        check=True
        except Exception,e:
            check=True
        return check




    def login(self, request):
        resp_data={}
        error=""
        try:
            if request.method=='POST':
                if 'form_name' in request.POST:
                    if request.POST['form_name']!='':
                        resp_data.setdefault('name',request.POST['form_name'])
                        if request.POST['form_user']!='':
                            if self.checkusername(request.POST['form_user'])!=True:
                                resp_data.setdefault('user',request.POST['form_user'])

                                if request.POST['form_email']!='' and '@' in request.POST['form_email']:
                                    resp_data.setdefault('email',request.POST['form_email'])

                                    if request.POST['form_password']!='' and len(request.POST['form_password'])>7:
                                        if request.POST['form_con_password']!='' and len(request.POST['form_con_password'])>7:

                                            if request.POST['form_password']==request.POST['form_con_password']:
                                                if request.POST['cc']!='Country Code':
                                                    resp_data.setdefault('cc',request.POST['cc'])

                                                    if request.POST['mc']!='Mobile Code':
                                                        resp_data.setdefault('mc', request.POST['mc'])

                                                        if request.POST['form_phone']!='' and len(request.POST['form_phone'])==7:
                                                            resp_data.setdefault('nber',request.POST['form_phone'])

                                                            if request.POST['form_address']!='':
                                                                code = randint(1000000, 9999999)
                                                                response=self.mail.sent_mail_client(request.POST['form_email'],code,'')
                                                                if response:
                                                                    sql = "insert into client (fullname,username,password,email,address,phone,issue_date,status,verify_code)" \
                                                                        " values ('" + request.POST['form_name'] + "','" + \
                                                                          request.POST['form_user'] + "','" \
                                                                        + request.POST['form_password'] + "','" + \
                                                                        request.POST['form_email'] + "','"+request.POST['form_address']+"','" +\
                                                                        request.POST['cc']+request.POST['mc']+ \
                                                                        request.POST['form_phone']+  "',(select current_date from dual),0,"+code+")"


                                                                    if self.db_flag:
                                                                        try:
                                                                            cursor=self.db_instance.cursor()
                                                                            flag,results=self.reader.execute_query(self.empty_result,cursor,sql)
                                                                            if flag:
                                                                                self.db_instance.commit()
                                                                                return render(request, 'login.html', {
                                                                                    'success': 'Registration account is successfully done.'
                                                                                    ' Please login with Username and Password','error':'','logvalue':0,'fname':'' ,'status':-1})
                                                                        except Exception,e:
                                                                            error="Sorry, something is wrong during saving your information."
                                                                    else:
                                                                        error = "Sorry, something is wrong during storage connection."
                                                                else:
                                                                    error = "Sorry, something is wrong during sending email of verification."
                                                            else:
                                                                error = "Sorry, processing error. Please fill address field."
                                                        else:
                                                            error = "Sorry, processing error. Please fill correct phone number without any country and mobile code like 3217654321."
                                                    else:
                                                        error = "Sorry, processing error. Please select mobile code field."
                                                else:
                                                    error = "Sorry, processing error. Please select country code field."
                                            else:
                                                error = "Sorry, processing error. Please use same password for new and confirm password field."
                                        else:
                                            error = "Sorry, processing error. Please fill confirm password field at least 8 character."
                                    else:
                                        error = "Sorry, processing error. Please fill password field at least 8 character."
                                else:
                                    error = "Sorry, processing error. Please fill email field correctly."
                            else:
                                error = "Sorry, processing error. Please choose another username, because this username already exist."
                        else:
                            error = "Sorry, processing error. Please fill username field."
                    else:
                        error = "Sorry, processing error. Please fill fullname field."
                else:
                    error = "Sorry, processing error during sending information."
                return render(request,'register.html',{'error':error,'success':'','logvalue':0,'fname':'' ,'status':-1,'data':resp_data})
            else:
                return render(request, 'login.html',{'error':'','success':'','logvalue':0,'fname':'' ,'status':-1})
        except Exception,e:
            return render(request, 'login.html',{'error':'Error due to '+str(e),'success':'','logvalue':0,'fname':'' ,'status':-1})

    @csrf_exempt
    def checkLoginUsername(self, request):
        try:
            if request.method == 'POST':
                sql = "select * from client where username ='" + request.POST['user'] + "'"

                if self.db_flag:
                    obj=self.db_instance.cursor()
                    flag,result=self.reader.execute_query(self.for_result,obj,sql)
                    if flag:
                        if len(result)!=0:
                            data = {'is_taken': ''}
                        else:
                            data = {'is_taken': 'No username found'}
                    else:
                        data = {'is_taken': 'Sorry, your username processing fails'}
                else:
                    data={'is_taken':'Sorry, database connection error due to internal issues'}
            else:
                data = {'is_taken': 'error during data sending to server'}
        except Exception, e:
            data = {'is_taken': str(e)}
        return JsonResponse(data)


    @csrf_exempt
    def checkVerifyScode(self,request):
        try:
            if request.method=='POST':
                if '__auth_log' in request.session:
                    if request.session['__auth_log']==1:
                        sql="select verify_code from client where username='"+request.session['fuser']+"'"

                        if self.db_flag:
                            cursor=self.db_instance.cursor()
                            flag,results=self.reader.execute_query(self.for_result,cursor,sql)
                            if flag:
                                if len(results)==1:
                                    if results[0][0]==request.POST['scode']:
                                        data={'is_taken':'Security code match.'}
                                    else:
                                        data = {'is_taken': 'Security code not match.'}
                                else:
                                    data = {'is_taken': 'Security code is not found for matching.'}
                            else:
                                data = {'is_taken': 'Sorry, processing error of verify code.'}
                        else:
                            data = {'is_taken': 'Sorry, storage connection error.'}
                    else:
                        data = {'is_taken': 'Sorry, your session may be expired. Please login again.'}
                else:
                    data = {'is_taken': 'Please login.'}
            else:
                data = {'is_taken': 'Server connection problem during sending data to server.'}
        except Exception,e:
            data = {'is_taken': 'Error due to '+str(e)}
        return JsonResponse(data)