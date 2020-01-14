from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse,request
from itsdangerous import base64_decode
from django.views.decorators.csrf import csrf_exempt
from random import randint
from cronjob import CronJob
from mail_ftn import MailService
from client_info import Client_Information
from reader import Reader
from chat import Chat
from sms import SMS
import os



class WebServices:
    def __init__(self,flag,instance,stack):
        self.db_flag=flag
        self.db_instance=instance
        self.for_result=True
        self.empty_result=False
        self.client=Client_Information(flag,instance)
        self.mail=MailService()
        self.reader=Reader()
        self.chat_obj=Chat(flag,instance,stack)
        self.sms=SMS()
        self.stack_message=stack
        self.client={}
        self.cronjob=CronJob(flag,instance)

###################################################################################################################################################################
############################################################CLIENT LOGIN & LOGOUT REQUEST#######################################################################################
########################################################################################################################################################################

    def create_code(self,user):
        c_code=''
        arg='abcdefghijklmnopqrstuvwxyz0123456789'
        counter,handle=0,0
        while(handle<5):
            while(counter<7):
                c_code+=arg[randint(0,len(arg))]
                counter+=1
            counter=0
            flag,g_code=self.check_code(c_code,user)
            if flag==True:
                break
            handle+=1
        return c_code

    def addFriend(self, user, client):
        check=False
        try:
            if user == client:
                return True
            sql = "insert into client_friend (username,client) values ('" + user + "','" + client + "')"

            if self.db_flag:
                cursor = self.db_instance.cursor()
                flag,result=self.reader.execute_query(self.empty_result,cursor,sql)
                if flag:
                    check = True
                    self.db_instance.commit()

        except:
            check=False
        return check

    def check_code(self,code,user):
        flag,g_code=False,code
        try:
            sql="select * from client_mobile where mob_code='"+g_code+"' and username='"+user+"'"

            if self.db_flag:
                cursor=self.db_instance.cursor()
                flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                if flag:
                    if len(result)==0:
                        flag=True
                    else:
                        g_code='Error, required code not found.'
                else:
                    g_code='Error, while searching to database.'
            else:
                g_code='Error while connecting to database.'
        except Exception,e:
            g_code='Error due to '+str(e)
        return flag,g_code


#################################################################################################################################################################################

    def login(self,request):
        try:
            if request.method=='POST':
                http_arg=request.POST
                sql="select * from client where username='"+http_arg['user']+"' and password='"+http_arg['pass']+"'"

                if self.db_flag:
                    cursor=self.db_instance.cursor()
                    flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                    if flag:
                        if len(result)==1:
                            g_code=self.create_code(http_arg['user'])
                            if g_code!='':
                                sql="insert into client_mobile (username,mob_code,mobile_date) values ('"+http_arg['user']+"','"+g_code+"',(select current_date from dual))"
                                flag, result = self.reader.execute_query(self.empty_result, cursor, sql)
                                if flag:
                                    self.db_instance.commit()
                                    data={'type':1,'resp':g_code}
                                else:
                                    data={'type':0,'resp':'Error, during updation processing.'}
                            else:
                                data = {'type': 2, 'resp': 'Sorry, do not create any authorize information of client.'}
                        else:
                            data = {'type':0,'resp': 'Sorry, required user not found.'}
                    else:
                        data = {'type': 0, 'resp': 'Sorry, searching error found.'}
                else:
                    data = {'type':0,'resp': 'Error, while connecting to database.'}
            else:
                data = {'type':0,'resp': 'Sorry, cannot access this web webservices.'}

        except Exception,e:
            data={'type':0,'resp':'Error due to '+str(e)}
        return JsonResponse(data)


    def logout(self,request):
        try:
            if request.method=='POST':
                http_arg=request.POST
                sql="delete from client_mobile where mob_code='"+http_arg['m_code']+"'"

                if self.db_flag:
                    cursor = self.db_instance.cursor()
                    flag, result = self.reader.execute_query(self.empty_result, cursor, sql)
                    if flag:
                        self.db_instance.commit()
                        data = {'type':1,'resp': 'You are successfully logout'}
                    else:
                        data={'type':2,'resp':'you are not logout successfully while error found.'}
                else:
                    data = {'type':2,'resp': 'Sorry, while internal storage error found.'}
            else:
                data={'type':0,'resp':'Error, while cannot access directly.'}
        except Exception,e:
            data={'type':0,'resp':'Error due to '+str(e)}
        return JsonResponse(data)



####################################################################################################################################################################################
###################################################################################CLIENT PASSWORD RECOVERY REQUEST##########################################################################
##################################################################################################################################################################################



    def forget_password(self,request):
        try:

            if request.method == 'POST':
                http_arg=request.POST
                if 'user' in http_arg:
                    sql = "select * from recovery_password where username='" + http_arg['user'] + "'"

                    if self.db_flag:
                        cursor = self.db_instance.cursor()
                        flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                        if flag:
                            if len(result)==0:

                                sql = "select email,phone from client where username='" + http_arg['user'] + "'"

                                flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                                if flag:
                                    if len(result)!=0:
                                        email,phone="",""
                                        if http_arg['req']=="email":
                                            code = randint(1000000, 9999999)
                                            if result[0][0]!=None and '@' in result[0][0]:
                                                email=result[0][0]
                                        elif http_arg['req']=="sms":
                                            phone=result[0][1]
                                            if '+' in phone:
                                                phone=phone[1:]
                                            elif '00' in phone:
                                                phone=phone[2:]

                                        if http_arg['req']=="email":
                                            flag=self.mail.sent_mail_client(email,code,'')
                                        elif http_arg['req']=="sms":
                                            flag=self.sms.send_code(phone,code)
                                        if flag:
                                            sql = "insert into recovery_password (username,scode,rdate) values ('" + http_arg['user'] + "'," + code + ",(select current_date from dual))"
                                            flag, sub_result = self.reader.execute_query(self.empty_result, cursor,sql)
                                            if flag:
                                                self.db_instance.commit()
                                                data = {'type':1,'resp': "Your current request for password recovery procceed. "
                                                                 "Email sent at this address:"+result[0][0]+"Please wait..."}
                                            else:
                                                data = {'type': 2, 'resp':"Sorry, updation error found"}
                                        else:
                                            data = {'type': 2,
                                                    'resp': 'Sorry, while sending code to client. Please try again.'}

                                    else:
                                        data = {'type': 0, 'resp': 'Error, while searching client that is not found.'}
                                else:
                                    data = {'type': 0, 'resp':'Sorry, while searching client email address during error found'}
                            else:
                                sql="select old_password,new_password from recovery_password where username='"+http_arg['user']+"'"
                                flag, sub_result = self.reader.execute_query(self.for_result, cursor, sql)
                                if flag:
                                    if len(result)==1:
                                        if result[0][0]==None and result[0][1]==None:
                                            sql="select r.scode,c.email from recovery_password r join client c on(c.username='"+http_arg['user']+"')"
                                            flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                                            if flag:
                                                if len(result)!=0:
                                                    if result[0][1]!=None and '@' in result[0][1]:
                                                        flag=self.mail.sent_mail_client(result[0][1],result[0][0],'')
                                                        if flag:
                                                            data = {'type': 1, 'resp': "Your request procceed. Email sent at this address:"+result[0][1]+" Please check your security code."}
                                                        else:
                                                            data = {'type': 2, 'resp': 'Sorry, while sending email request to client, Please try again.'}
                                                    else:
                                                        data = {'type': 0, 'resp': 'Error, while searching for client email address.'}
                                                else:
                                                    data = {'type': 0, 'resp': 'Error, while not found record about security.'}
                                            else:
                                                data = {'type': 0, 'resp': 'Error, while searchin error is found.'}
                                        else:
                                            data = {'type': 0, 'resp': 'Error, while requested duplicate request.'}
                                    else:
                                        data = {'type': 0, 'resp': 'Error, while record is not found.'}
                                else:
                                    data = {'type': 0, 'resp': 'Error, while searching database.'}
                        else:
                            data = {'type': 0, 'resp': 'Error, while searching database.'}
                    else:
                        data = {'type':0,'resp': 'Error, while connecting to database.'}
                else:
                    data = {'type': 0, 'resp': 'Error, while missing argument for proccessing.'}
            else:
                data = {'type':0,'resp': 'Error, while cannot access directly.'}
        except Exception,e:
            data = {'type':0,'resp': 'Error due to '+str(e)}
        return JsonResponse(data)



    def recovery_password(self,request):
        try:
            if request.method=='POST':
                http_arg=request.POST
                if 'user' in http_arg:
                    if 'scode' in http_arg:
                        if 'pass' in http_arg:
                            if 'con_pass' in http_arg:
                                sql="select * from recovery_password where username='"+http_arg['user']+"' and scode='"+http_arg['scode']+"'"

                                if self.db_flag:
                                    cursor=self.db_instance.cursor()
                                    flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                                    if flag:
                                        if len(result)==1:
                                            if http_arg['pass']==http_arg['con_pass']:
                                                sql="select password from client where username='"+http_arg['user']+"'"
                                                flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                                                if flag:
                                                    if len(result)==1:
                                                        old_password=result[0][0]
                                                        sql = "update recovery_password set old_password='"+old_password+"', new_password='" + \
                                                                http_arg['pass'] + "' where username='" + http_arg[
                                                            'user'] + "'"
                                                        flag, result = self.reader.execute_query(self.empty_result,cursor, sql)
                                                        if flag:
                                                            sql="update client set password='"+http_arg['pass']+"' where username='"+http_arg['user']+"'"
                                                            flag, result = self.reader.execute_query(self.empty_result,cursor, sql)
                                                            if flag:
                                                                self.db_instance.commit()
                                                                data={'type':1,'resp':"Congrates, Your recovery password succeeded."}
                                                            else:
                                                                data = {'type': 2,'resp': 'Sorry, while error found during updating record.'}
                                                        else:
                                                            data = {'type': 2,'resp': 'Sorry, while error found during updating record.'}
                                                    else:
                                                        data = {'type': 2, 'resp': 'Sorry, while searching pervious information of client.'}
                                                else:
                                                    data = {'type': 0,'resp': 'Sorry, while error found during searching record.'}
                                            else:
                                                data = {'type': 0, 'resp': 'Error, while new password and confirm password does not matched.'}
                                        else:
                                            data = {'type': 0, 'resp': 'Error, while searching perivous record.'}
                                    else:
                                        data = {'type': 0, 'resp': 'Error, while searching perivous record.'}
                                else:
                                    data = {'type': 0, 'resp': 'Error , while connecting to database.'}
                            else:
                                data = {'type': 0, 'resp': 'Error, while missing argument (confirm password).'}
                        else:
                            data = {'type': 0, 'resp': 'Error, while missing argument (password).'}
                    else:
                        data = {'type': 0, 'resp': 'Error, while missing argument (security code).'}
                else:
                    data = {'type': 0, 'resp': 'Error, while missing argument (username).'}
            else:
                data = {'type': 0, 'resp': 'Error, while accessing directly '}
        except Exception,e:
            data = {'type':0,'resp': 'Error due to '+str(e)}
        return JsonResponse(data)



#################################################################################################################################################################################
########################################################################NEW CLIENT ACCOUNT REQUEST###################################################################################
##################################################################################################################################################################################



    def signup(self,request):
        try:
            if request.method=='POST':
                http_arg=request.POST
                if 'name' in http_arg:
                    if 'user' in http_arg:
                        if 'email' in http_arg:
                            if 'address' in http_arg:
                                if 'pass' in http_arg:
                                    if 'con_pass' in http_arg:
                                        if http_arg['pass'] == http_arg['con_pass']:
                                            if 'phone' in http_arg:
                                                code = randint(1000000, 9999999)
                                                sql="insert into client (fullname,username,password,email,address,phone,issue_date,status,verify_code)" \
                                                            " values ('" + str(http_arg['name']) + "','" + \
                                                                str(http_arg['user']) + "','" \
                                                                + str(http_arg['pass']) + "','" + \
                                                                str(http_arg['email']) + "','"+str(http_arg['address'])+"','" +\
                                                                str(http_arg['phone'])+  "',(select current_date from dual),0,"+str(code)+")"

                                                if self.db_flag:
                                                    cursor=self.db_instance.cursor()
                                                    flag,result=self.reader.execute_query(self.empty_result,cursor,sql)
                                                    if flag:
                                                        self.db_instance.commit()
                                                        data = {'type': 1, 'resp': 'Congrates, your account is successfully created.'}
                                                    else:
                                                        data = {'type': 2, 'resp': 'Sorry, database updation error is found.'}
                                                else:
                                                    data = {'type': 2, 'resp': 'Sorry, while operation cannot be completed successfully.'}
                                            else:
                                                data = {'type': 0, 'resp': 'Error, while not found phone no.'}
                                        else:
                                            data = {'type': 0,
                                                        'resp': 'Error, while not matched password and confirm password.'}
                                    else:
                                        data = {'type': 0, 'resp': 'Error, while not found confirm password.'}
                                else:
                                    data = {'type': 0, 'resp': 'Error, while not found password.'}
                            else:
                                data = {'type': 0, 'resp': 'Error, while not found address.'}
                        else:
                            data = {'type': 0, 'resp': 'Error, while not found email.'}
                    else:
                        data = {'type': 0, 'resp': 'Error, while not found username.'}
                else:
                    data = {'type': 0, 'resp': 'Error, while not found fullname.'}
            else:
                data = {'type': 0, 'resp': 'Error, while accessing directly.'}
        except Exception,e:
            data = {'type':0,'resp': 'Error due to '+str(e)}
        return JsonResponse(data)



###############################################################################################################################################################################
############################################################CLIENT ACOOUNT'S SETTING OPTIONS####################################################################################
#################################################################################################################################################################################




    def profile(self,request):
        try:
            flag=False
            flag_ = False
            if request.method=='POST':
                http_arg=request.POST
                if 'status' in http_arg and 'm_code' in http_arg:
                    if http_arg['status']=='false':
                        sql = "select fullname,username,email,address,phone,issue_date," \
                              "verify_date from client where username=(select username from client_mobile where mob_code='" + \
                              http_arg['m_code'] + "')"
                    elif http_arg['status']=='true':
                        sql="update client set"

                        if 'fullname' in http_arg:
                            sql+=" fullname='"+http_arg['fullname']+"'"
                            flag_=True
                        if 'email' in http_arg:
                            if flag_:
                                sql+=","
                            sql+=" email='"+http_arg['email']+"'"
                            flag_=True
                        if 'phone' in http_arg:
                            if flag_:
                                sql+=","
                            sql+=" phone='"+http_arg['phone']+"'"
                        if 'address' in http_arg:
                            if flag_:
                                sql+=","
                            sql+=" address='"+http_arg['address']+"'"
                    else:
                        flag=True


                    if self.db_flag:
                        cursor=self.db_instance.cursor()
                        if flag==False:

                            if http_arg['status']=='false':
                                sub_flag,result=self.reader.execute_query(self.for_result,cursor,sql)
                                if sub_flag:
                                    if len(result)>0:
                                        lst=[]
                                        for row in result:
                                            dit={}
                                            dit.setdefault('fullname',row[0])
                                            dit.setdefault('user', row[1])
                                            dit.setdefault('email', row[2])
                                            dit.setdefault('address',row[3])
                                            dit.setdefault('phone', row[4])
                                            dit.setdefault('is_date', str(row[5]))
                                            dit.setdefault('ve_date', str(row[6]))
                                            lst.append(dit)
                                        data = {'type': 1, 'resp': lst}
                                    else:
                                        data = {'type': 2, 'resp': 'Sorry, required user not found'}
                                else:
                                    data = {'type': 2, 'resp': 'Sorry, server storage is not working well.'}

                            elif http_arg['status']=='true':
                                if flag_:
                                    sql+=" where username=(select username from client_mobile where mob_code='" + http_arg['m_code'] + "')"
                                    sub_flag, result = self.reader.execute_query(self.empty_result, cursor, sql)
                                    if sub_flag:
                                        self.db_instance.commit()

                                        data = {'type': 1,
                                            'resp': 'Congrate, your profile has been changed successfully.'}
                                    else:
                                        data = {'type': 2, 'resp': 'Sorry, server storage is not working well.'}
                                else:
                                    data = {'type': 2, 'resp': 'Sorry, while updating profile due to missing attributes.'}
                        else:
                            data = {'type': 0, 'resp': 'Error, required request not procceed due to improper arguments.'}
                    else:
                        data = {'type': 0, 'resp': 'Error, while connecting to database.'}
                else:
                    data = {'type': 0, 'resp': 'Error, required key is not found.'}
            else:
                data={'type':0,'resp':'Error, while accessing directly.'}
        except Exception,e:
            data={'type':0,'resp':'Error due to '+str(e)}
        return JsonResponse(data)



    def change_password(self,request):
        try:
            if request.method=='POST':
                http_arg=request.POST
                if 'm_code' in http_arg:
                    if 'old_pass' in http_arg:
                        if 'new_pass' in http_arg:
                            if 'con_pass' in http_arg:
                                if http_arg['new_pass']==http_arg['con_pass']:
                                    sql="select username from client_mobile where mob_code='"+http_arg['m_code']+"'"

                                    if self.db_flag:
                                        cursor=self.db_instance.cursor()
                                        sub_flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                                        if sub_flag:
                                            if len(result)!=0:
                                                sql="update client set password='"+http_arg['new_pass']+"' where username='"+result[0][0]+"'"

                                                sub_flag, result = self.reader.execute_query(self.empty_result, cursor,sql)
                                                if sub_flag:
                                                    self.db_instance.commit()
                                                    data = {'type': 1, 'resp': 'Your password has been changed successfully.'}
                                                else:
                                                    data={'type': 2, 'resp': 'Sorry, server storage is not working well.'}
                                            else:
                                                data = {'type': 2, 'resp': 'Sorry, while invalid recognize user.'}
                                        else:
                                            data={'type': 2, 'resp': 'Sorry, server storage is not working well.'}
                                    else:
                                        data = {'type': 0, 'resp': 'Error, while connecting to database.'}
                                else:
                                    data = {'type': 0, 'resp': 'Error, while does not match passwords.'}
                            else:
                                data = {'type': 0, 'resp': 'Error, while searching confirm password.'}
                        else:
                            data = {'type': 0, 'resp': 'Error, while searching new password.'}
                    else:
                        data = {'type': 0, 'resp': 'Error, while searching old password.'}
                else:
                    data = {'type': 0, 'resp': 'Error, while fully recoginize the user info.'}
            else:
                data = {'type': 0, 'resp': 'Error, while sending data to server.'}
        except Exception,e:
            data={'type':0,'resp':'Error due to '+str(e)}
        return JsonResponse(data)



    def ads_history(self,request):
        try:
            if request.method=='POST':
                http_arg=request.POST
                if 'm_code' in http_arg:
                    sql="select property_name,address,city,price,category,property_id from property " \
                        "where username=(select username from client_mobile where mob_code='"+http_arg['m_code']+"')"

                    if self.db_flag:
                        cursor = self.db_instance.cursor()
                        flag,result=self.reader.execute_query(self.for_result,cursor,sql)
                        if flag:
                            if len(result)!=0:
                                lst=[]
                                for row in result:
                                    dic={}
                                    dic.setdefault("title",row[0])
                                    dic.setdefault("address", row[1])
                                    dic.setdefault("city", row[2])
                                    dic.setdefault("price", row[3])
                                    dic.setdefault("category", row[4])
                                    dic.setdefault("id", row[5])
                                    lst.append(dic)
                                data={'type':1,'resp':lst}
                            else:
                                data = {'type': 2, 'resp': 'Sorry, not found such records for property ads.'}
                        else:
                            data={'type':2,'resp':'Sorry, server storage is not working well.'}
                    else:
                        data = {'type': 0, 'resp': 'Error, while connecting to database.'}
                else:
                    data = {'type': 0, 'resp': 'Error, while not found arguments.'}
            else:
                data = {'type': 0, 'resp': 'Error, while access directly service.'}
        except Exception, e:
            data = {'type': 0, 'resp': 'Error due to ' + str(e)}
        return JsonResponse(data)


############################################################################################################################################################################
#############################################################################PROPERTY OPERATION & REQUESTS############################################################################
###############################################################################################################################################################################

    def get_property_images_by_id(self,request):
        try:
            if request.method == 'POST':
                http_arg=request.POST
                if 'id' in http_arg:

                    if self.db_flag:
                        sql="select path from property_media where property_id='"+http_arg['id']+"' and type in ('jpg','jpeg','png','bmp','gif')"
                        cursor=self.db_instance.cursor()
                        flag,result=self.reader.execute_query(self.for_result,cursor,sql)
                        if flag:
                            lst=[]
                            if len(result)>0:
                                for row in result:
                                    lst.append("/static/property/"+http_arg['id']+"/"+row[0])
                            else:
                                lst.append("/static/property/default.jpg")
                            data = {'type': 1, 'resp':lst}
                        else:
                            data = {'type': 2, 'resp': 'Sorry, while internal storage error found.'}
                    else:
                        data = {'type': 2, 'resp': 'Sorry, while internal storage error found.'}
                else:
                    data = {'type': 0, 'resp': 'Error, while not found arguments.'}
            else:
                data = {'type': 0, 'resp': 'Error, while access directly service.'}
        except Exception, e:
            data = {'type': 0, 'resp': 'Error due to ' + str(e)}
        return JsonResponse(data)

    def getMediaImage(self,p_id):
        path="/static/property/default.jpg"
        if self.db_flag:
            sql = "select path from property_media where property_id='" + p_id + "' and type in ('jpg','jpeg','png','bmp','gif')"
            cursor = self.db_instance.cursor()
            flag, result = self.reader.execute_query(self.for_result, cursor, sql)
            if flag:
                if len(result) > 0:
                    for row in result:
                        path="/static/property/" + p_id + "/" + row[0]
                        break
        return path

    def getMediaVideo(self,p_id):
        path="/media/property/trial.mp4"
        if self.db_flag:
            sql = "select path from property_media where property_id='" + p_id + "' and type in ('mp4','3gp','avi','mkv')"
            cursor = self.db_instance.cursor()
            flag, result = self.reader.execute_query(self.for_result, cursor, sql)
            if flag:
                if len(result) > 0:
                    for row in result:
                        path="/media/property/" + p_id + "/" + row[0]
                        break
        return path

    def get_property_by_id(self,request):
        try:
            if request.method=='POST':
                http_arg=request.POST

                if 'id' in http_arg:
                    
                    sql="select p.property_name,p.address,p.city,p.price,p.category,p.type,p.DESCRIPTION,p.area,p.status," \
                    "p.property_date,c.fullname,pd.bed,pd.living,pd.park,pd.kitchen from property p join client c" \
                    " on(p.property_id='"+http_arg['id']+"' and c.username=(select username from property where property_id='"+http_arg['id']+"')) " \
                    "join property_detail pd on(pd.property_id='"+http_arg['id']+"')"
                    
                    if self.db_flag:
                        cursor=self.db_instance.cursor()
                        flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                        if flag:
                            if len(result)==1:
                                lst = []
                                for row in result:
                                    dic={}

                                    dic.setdefault("title",row[0])
                                    dic.setdefault("address", row[1])
                                    dic.setdefault("city", row[2])
                                    dic.setdefault("price", self.reader.addComma(str(row[3])))
                                    dic.setdefault("category", row[4])
                                    dic.setdefault("type", row[5])
                                    dic.setdefault("desc", row[6])
                                    dic.setdefault("area", row[7])
                                    dic.setdefault("status", row[8])
                                    dic.setdefault("date", row[9])
                                    dic.setdefault("fullname", row[10])
                                    dic.setdefault("bed", row[11])
                                    dic.setdefault("living", row[12])
                                    dic.setdefault("park", row[13])
                                    dic.setdefault("kitchen", row[14])
                                    dic.setdefault("img",self.getMediaImage(http_arg['id']))
                                    dic.setdefault("video", self.getMediaVideo(http_arg['id']))
                                    lst.append(dic)

                                data = {'type': 1, 'resp': lst}
                            else:
                                data = {'type': 2, 'resp': 'Sorry, no result found according to requirement'}
                        else:
                            data={'type':2,'resp':'Sorry, server storage is not working well.'}
                    else:
                        data = {'type': 0, 'resp': 'Error while connecting to database'}
                else:
                    data = {'type': 0, 'resp': 'Error, while missing info'}
            else:
                data = {'type': 0, 'resp': 'Error, while accessing directly.'}
        except Exception,e:
            data = {'type': 0, 'resp': 'Error due to ' + str(e)}
        
        return JsonResponse(data)



    def get_property(self,request):
        try:
            bed,park=False,False
            sql = "select property_name,address,city,price,category,type,status,property_id from property"
            if request.method=='POST':
                http_arg=request.POST
                flag=False

                if 'price' in http_arg:
                    if flag==False:
                        flag=True
                        sql+=" where"
                    else:
                        sql+=" and"
                    price=''
                    try:
                        if '+' in request.POST['price']:
                            price = request.POST['price']
                            operation = ">="
                            if 'Lac' in request.POST['price']:
                                price = 100000
                                no = int(str(request.POST['price'][0]))
                                price *= no
                            elif 'Crore' in request.POST['price']:
                                price = 10000000
                                no = int(str(request.POST['price'][0]))
                                price *= no
                            else:
                                price = price[:-1]

                        elif 'Lac' in request.POST['price']:
                            price = 100000
                            no = int(str(request.POST['price'][0]))
                            price *= no

                        elif 'Crore' in request.POST['price']:
                            price = 10000000
                            no = int(str(request.POST['price'][0]))
                            price *= no

                        else:
                            price = request.POST['price']
                            operation = "<="
                    except:
                        price='10000'
                    sql+=" price<="+price
                if 'category' in request.GET:
                    if flag==False:
                        flag=True
                        sql += " where"
                    else:
                        sql+=" and"
                    sql+=" category='" + http_arg['category']+"'"

                if 'type' in http_arg:
                    if flag==False:
                        flag = True
                        sql += " where"
                    else:
                        sql+=" and"

                    sql += " type='" + http_arg['type']+"'"

                if 'query' in http_arg:
                    if flag==False:
                        flag = True
                        sql += " where"
                    else:
                        sql+=" and"
                    arg= str(http_arg['query']).lower()
                    sql += " (property_name like '%" +arg+"%' or city like '%"+arg+"%' or " \
                                "address like '%"+arg+"%' or property_id like '%"+arg+"%' or area like '%"+arg+"%')"
                if 'bed' in http_arg and http_arg['bed']!="Bed Rooms":
                    bed=True
                if 'parking' in http_arg and http_arg['parking']!="Parking Place":
                    park=True

                if flag:
                    sql+=" and status>-1 order by price desc"



            if self.db_flag:

                cursor = self.db_instance.cursor()

                sql_detail = "select bed,living,park,KITCHEN from property_detail where"
                if bed:
                    sql_detail += " bed=" + http_arg['bed']
                if park and 'bed=' in sql_detail:
                    sql_detail += " and park=" + http_arg['parking']
                elif park:
                    sql_detail += " park=" + http_arg['parking']
                if bed or park:
                    sql_detail += " and"

                flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                if flag:
                    if len(result)>0:
                        result_list=[]
                        count=0
                        for row in result:
                            if count > 29:
                                break
                            sql=sql_detail+" property_id='"+row[7]+"'"

                            sub_flag,sub_result=self.reader.execute_query(self.for_result,cursor,sql)
                            if sub_flag:
                                if len(sub_result)>0:
                                    di={}
                                    di.setdefault("name",row[0])
                                    di.setdefault("address",row[1] )
                                    di.setdefault("city", row[2])
                                    di.setdefault("price", self.reader.addComma(str(row[3])))
                                    di.setdefault("category", row[4])
                                    di.setdefault("type", row[5])
                                    di.setdefault("status", row[6])
                                    di.setdefault("p_id", row[7])
                                    di.setdefault("img", self.getMediaImage(row[7]))
                                    result_list.append(di)
                                    count+=1


                        data = {'type': 1, 'resp': result_list}
                    else:
                        data = {'type': 2, 'resp': 'Sorry, while not found required results.'}
                else:
                    data = {'type': 2, 'resp': 'Sorry, server storage is not working well.'}
            else:
                data = {'type': 0, 'resp': 'Error, while connecting to database.'}
        except Exception, e:
            data = {'type': 0, 'resp': 'Error due to ' + str(e)}
        return JsonResponse(data)


    def operation_property(self,request):
        delete_flag=False
        try:
            sql="property"
            if request.method=='POST':
                http_arg=request.POST
                if 'update' in http_arg:
                    sql="update "+sql +" set"

                    flag=False
                    if 'address' in http_arg:
                        flag=True
                        sql+=" address='"+http_arg['address']+"'"
                    if 'city' in http_arg:
                        if flag:
                            sql+=","
                        else:
                            flag=True
                        sql+=" city='"+http_arg['city']+"'"

                    if 'name' in http_arg:
                        if flag:
                            sql+=","
                        else:
                            flag=True
                        sql+=" property_name='"+http_arg['name']+"'"

                    if 'price' in http_arg:
                        if flag:
                            sql+=","
                        else:
                            flag=True
                        tmp=http_arg['price']
                        tmp=tmp.split(',')
                        newtmp=""
                        for _ in tmp:
                            newtmp+=_
                        sql+=" price="+newtmp

                    if 'category' in http_arg:
                        if flag:
                            sql+=","
                        else:
                            flag=True
                        sql+=" category='"+http_arg['category']+"'"

                    if 'type' in http_arg:
                        if flag:
                            sql+=","
                        else:
                            flag=True
                        sql+=" type='"+http_arg['type']+"'"

                    if 'status' in http_arg:
                        if flag:
                            sql+=","
                        else:
                            flag=True
                        sql+=" status="+http_arg['status']

                    if 'desc' in http_arg:
                        if flag:
                            sql+=","
                        else:
                            flag=True
                        sql+=" description='"+http_arg['desc']+"'"

                    if 'area' in http_arg:
                        if flag:
                            sql+=","
                        else:
                            flag=True
                        sql+=" area='"+http_arg['area']+"'"
                    sql+=" ,last_modified=(select current_date from dual)"
                elif 'delete' in http_arg:
                    sql="update "+sql+" set status=-1"
                    delete_flag=True
                if 'p_id' in http_arg:
                    sql+=" where property_id='"+http_arg['p_id']+"'"

                    if self.db_flag:
                        cursor = self.db_instance.cursor()
                        if delete_flag:
                            error=False
                            list_query = []

                            list_query.append(
                                "delete from property_alert where property_id='" + http_arg['p_id'] + "'")
                            list_query.append(
                                "delete from property_detail where property_id='" + http_arg['p_id'] + "'")
                            list_query.append(
                                "delete from property_feedback where property_id='" + http_arg['p_id'] + "'")
                            list_query.append(
                                "delete from property_media where property_id='" + http_arg['p_id'] + "'")
                            list_query.append(
                                "delete from property_rating where property_id='" +http_arg['p_id'] + "'")
                            list_query.append(
                                "delete from property_saving where property_id='" + http_arg['p_id'] + "'")
                            list_query.append("delete from property where property_id='" + http_arg['p_id'] + "'")

                            for query in list_query:
                                flag, result = self.reader.execute_query(self.empty_result, cursor, query)
                                if flag:
                                    continue
                                else:
                                    error = True
                                    break
                            if error == False:
                                self.db_instance.commit()
                                data = {'type': 1, 'resp': 'Your property ad has been deleted.'}
                            else:
                                data = {'type': 2,
                                        'resp': 'Your property ad has not been deleted yet due to storage updation error found.'}
                        else:
                            
                            flag,result=self.reader.execute_query(self.empty_result,cursor,sql)
                            if flag:
                                self.db_instance.commit()
                                data = {'type': 1, 'resp': 'Your required operation procceed successfully.'}
                            else:
                                data = {'type': 2, 'resp': 'Sorry, while internal storage working error found.'}
                    else:
                        data = {'type': 2, 'resp': 'Sorry, while internal storage error found.'}
                else:
                    data = {'type': 0, 'resp': 'Error, while selection id missing of record that you to change.'}
            else:
                data = {'type': 0, 'resp': 'Error, while sending data to server.'}
        except Exception, e:
            data = {'type': 0, 'resp': 'Error due to ' + str(e)}
        print data
        return JsonResponse(data)



##########################################################New Property AD Request###################################################################################




    def get_ID(self):
        value = "abcdefghijklmnopqrstuvxyz"
        value2 = "1234567890"
        gene_id = ""
        try:
            for i in range(1, 3):
                index = randint(0, len(value))
                gene_id += value[index]
            for i in range(1, 6):
                index = randint(0, len(value2))
                gene_id += value2[index]

            sql = "select * from property where property_id='" + gene_id + "'"

            if self.db_flag:
                cursor = self.db_instance.cursor()
                flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                if flag:
                    if len(result) == 0:
                        return gene_id
                else:
                    return False
            else:
                return False
        except Exception, e:
            return False




    def save_data_to_db(self,query):
        check=False
        try:

            if self.db_flag:
                cursor=self.db_instance.cursor()
                flag, result = self.reader.execute_query(self.empty_result, cursor, query)
                if flag:
                    self.db_instance.commit()
                    check=True
        except Exception,e:
            check= False
        return check


    def save_media(self,request):
        data=None
        err_img,err_video=False,False
        error_flag=False
        image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp']
        video_extensions = ['mp4', '3gp', 'mkv', 'avi', 'webm']
        try:
            if request.method=='POST':
                
                if 'mob_code' in request.POST:
                    if 'p_id' in request.POST:
                        p_id=request.POST['p_id']
                        
                        if 'img' not in request.POST:
                            err_img=True
                        if 'video' not in request.FILES:
                            err_video=True
                        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                        if err_img==False:
                            
                            full_path = os.path.join(BASE_DIR, "\\static\\property\\" + p_id + "\\")
                            if os.path.exists(BASE_DIR + full_path) == False:
                                os.mkdir(BASE_DIR + full_path)
                            full_imgPath = os.path.join(BASE_DIR + full_path, request.POST['mob_code']+'.jpg')
                            flag=False


                            img_src = base64_decode(request.POST['img'])
                            with open(full_imgPath,'wb+') as file:
                                for chunk in img_src:
                                    file.write(chunk)
                                file.flush()
                                file.close()
                            sql="insert into property_media (property_id,type,path,media_date) values ('"+\
                                request.POST['p_id'] +"','jpg','"+\
                                request.POST['p_code']+"/"+request.POST['mob_code']+".jpg'"+",(select current_date from dual))"
                            if self.save_data_to_db(sql):
                                data={'type':1,'resp':'Your property image has been saved successfully.'}
                            else:
                                data = {'type': 0, 'resp': 'Your property image has not been saved successfully.'}

                        if err_video==False:
                            vid = request.FILES['video']
                            # 20 MB video file check
                            video_dir = ""
                            if vid.size <= 20000000:
                                full_path = os.path.join(BASE_DIR, "\\media\\property\\" + p_id + "\\")
                                video_dir = BASE_DIR + full_path
                                if os.path.exists(BASE_DIR + full_path) == False:
                                    try:
                                        os.mkdir(BASE_DIR + full_path)
                                    except Exception, e:
                                        print str(e)
                                full_filename = os.path.join(BASE_DIR + full_path, vid.name)

                                arg = vid.name.split('.')

                                if str(arg[1]).lower() not in video_extensions:
                                    error_flag = True
                                    data = {'type': 2, 'resp':"Video extension is reconginze, Please use only .mp4, .3gp, .mkv, .webm, .avi"}
                                else:
                                    fs = FileSystemStorage()
                                    filename = fs.save(video_dir + vid.name, vid)
                                    uploaded_file_url = fs.url(filename)

                                    sql = "insert into property_media (property_id,type,path,media_date) values " \
                                          "('" + p_id + "','" + str(arg[1]).lower() + "','" + str(
                                        vid.name) + "',(select current_date from dual))"
                                    if self.save_data_to_db(sql):
                                        self.db_instance.commit()
                                        data = {'type': 1,
                                                'resp': 'Your property media file(s) has been saved successfully.'}
                                if error_flag:
                                    data = {'type': 2, 'resp':'Error due to not supporting of extension, '}
                                    # for video code

                            else:
                                data = {'type': 2, 'resp':'Error, while uploading file which has size greater than 20 MB.'}


                        if err_img and err_video:
                            data = {'type': 0, 'resp': 'Please select some media files for property.'}

                    else:
                        data = {'type': 0, 'resp': 'Error, while missing property identity arguments.'}
                else:
                    data = {'type': 0, 'resp': 'Error, while missing arguments'}
            else:
                data = {'type': 0, 'resp': 'Error, while accessing wrong approach'}
        except Exception,e:
            data = {'type': 0, 'resp': 'Error due to '+str(e)}
        
        return JsonResponse(data,safe=False)


    def new_property(self,request):
        try:
            if request.method=='POST':
                http_arg=request.POST
                if 'mob_code' in http_arg:
                    if 'title' in http_arg:
                        if 'desc' in http_arg:
                            if 'address' in http_arg:
                                if 'city' in http_arg:
                                    if 'price' in http_arg:
                                        if 'type' in http_arg:
                                            if 'category' in http_arg:
                                                if 'bed' in http_arg:
                                                    if 'living' in http_arg:
                                                        if 'kitchen' in http_arg:
                                                            if 'parking' in http_arg:
                                                                if 'area' in http_arg:
                                                                    generate_code,username='',''
                                                                    counter=0
                                                                    while counter<3:
                                                                        generate_code=self.get_ID()
                                                                        if type(generate_code)==str:
                                                                            break
                                                                        counter+=1
                                                                    if type(generate_code)==str:
                                                                        sql="select username from client_mobile where mob_code='"+http_arg['mob_code']+"'"

                                                                        if self.db_flag:
                                                                            cursor=self.db_instance.cursor()
                                                                            flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                                                                            if flag:
                                                                                if len(result)==1:
                                                                                    username=result[0][0]
                                                                                    if len(username)>0 and username!=None:
                                                                                        sql="insert into property (property_id,property_name,description," \
                                                                                        "address,city,price,type,category,area,status,property_date,last_modified,username) values" \
                                                                                        " ('"+generate_code+"','"+http_arg['title']+"','"+http_arg['desc']+\
                                                                                        "','"+str(http_arg['address']).lower()+"','"+str(http_arg['city']).lower()+"',"+http_arg['price']+\
                                                                                        ",'"+http_arg['type']+"','"+http_arg['category']+\
                                                                                        "','"+http_arg['area']+"',0,(select current_date from dual),(select current_date from dual)," \
                                                                                              "'"+username+"')"
                                                                                        try:
                                                                                            flag, result = self.reader.execute_query(self.empty_result,cursor, sql)
                                                                                            if flag:
                                                                                                self.db_instance.commit()

                                                                                                sql = "insert into property_detail " \
                                                                                                        "(property_id,bed,living,kitchen,park) values" \
                                                                                                            " ('"+generate_code+"',"+ \
                                                                                                        http_arg['bed']+","+http_arg['living']+","+http_arg['kitchen']+","+http_arg['parking']+")"
                                                                                                flag, result = self.reader.execute_query(self.empty_result, cursor,sql)
                                                                                                if flag:
                                                                                                    self.db_instance.commit()
                                                                                                    #self.reader.new_thread_for_subscribe(self.cronjob,generate_code)
                                                                                                    data = {'type': 1, 'resp': generate_code}
                                                                                                else:
                                                                                                    {'type': 2,
                                                                                                     'resp': 'Sorry, while server database is not working well.'}
                                                                                            else:

                                                                                                {'type': 2,
                                                                                                 'resp': 'Sorry, while server database is not working well.'}
                                                                                        except Exception,e:
                                                                                            data = {'type': 0, 'resp': 'Error due to, '+str(e)}
                                                                                    else:
                                                                                        data = {'type': 2, 'resp': 'Sorry, while not recognize the client information.'}
                                                                                else:
                                                                                    data = {'type': 0, 'resp': 'Error, while not found that username.'}
                                                                            else:
                                                                                {'type':2,
                                                                                 'resp': 'Sorry, while server database is not working well.'}
                                                                        else:
                                                                            data = {'type': 0, 'resp': 'Error, while connecting to database.'}
                                                                    else:
                                                                        data={'type':0,'resp':'Error, while unable to create property code. Please try again.'}
                                                                else:
                                                                    data = {'type': 0, 'resp': 'Error, while missing area info.'}
                                                            else:
                                                                data = {'type': 0, 'resp': 'Error, while missing parking info.'}
                                                        else:
                                                            data = {'type': 0, 'resp': 'Error, while missing kitchen info.'}
                                                    else:
                                                        data = {'type': 0, 'resp': 'Error, while missing living info.'}
                                                else:
                                                    data = {'type': 0, 'resp': 'Error, while missing bed info.'}
                                            else:
                                                data = {'type': 0, 'resp': 'Error, while missing category info.'}
                                        else:
                                            data = {'type': 0, 'resp': 'Error, while missing type info.'}
                                    else:
                                        data={'type':0,'resp':'Error, while missing price info.'}
                                else:
                                    data = {'type': 0, 'resp': 'Error, while missing city info.'}
                            else:
                                data = {'type': 0, 'resp': 'Error, while missing address info.'}
                        else:
                            data = {'type': 0, 'resp': 'Error, while missing description info.'}
                    else:
                        data = {'type': 0, 'resp': 'Error, while missing title info.'}
                else:
                    data = {'type': 0, 'resp': 'Error, while missing mobile code info.'}
            else:
                data = {'type': 0, 'resp': 'Error, while accessing directly'}

        except Exception,e:
            data = {'type': 0, 'resp': 'Error due to '+str(e)}

        return JsonResponse(data)

###############################################################################################################################################################################
############################################################################PROPERTY' S Alert notifications Operations##########################################################
################################################################################################################################################################################


    def feedback_rating(self,request):
        try:
            if request.method=='POST':
                database=request.POST
                if 'mob_code' in database:
                    if 'id' in database:

                        if self.db_flag:
                            cursor=self.db_instance.cursor()
                            sql="select username from client_mobile where mob_code ='"+database['mob_code']+"'"
                            flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                            if flag:
                                if len(result) > 0:
                                    if 'feedback' in database and 'rating' in database:
                                        sql="insert into property_feedback (username,feedback,feedback_date,property_id) values ('"+result[0][0]+"'," \
                                        "'"+database['feedback']+"',(select current_date from dual),'"+database['id']+"')"
                                        flag, sub_result = self.reader.execute_query(self.empty_result, cursor, sql)
                                        if flag:
                                            sql = "insert into property_rating (username,rating,rating_date,property_id) values ('" + \
                                            result[0][0] + "'," \
                                                  "'" + database['rating'] + "',(select current_date from dual),'"+database['id']+"')"
                                            flag, sub_result = self.reader.execute_query(self.empty_result, cursor, sql)
                                            if flag:
                                                self.db_instance.commit()
                                                data = {'type': 1, 'resp': 'Your feedback and rating has been saved successfully'}
                                            else:
                                                data = {'type': 2,
                                                        'resp': 'Sorry, server storage is not working.'}
                                        else:
                                            data = {'type': 2,
                                                    'resp': 'Sorry, server storage is not working.'}
                                    elif 'feedback' in database:
                                        sql="insert into property_feedback (username,feedback,feedback_date,property_id) values ('"+result[0][0]+"'," \
                                        "'"+database['feedback']+"',(select current_date from dual),'"+database['id']+"')"
                                        flag, sub_result = self.reader.execute_query(self.empty_result, cursor, sql)
                                        if flag:
                                            self.db_instance.commit()
                                            data = {'type': 1, 'resp': 'Your feedback has been saved successfully'}
                                        else:
                                            data = {'type': 2,
                                                    'resp': 'Sorry, server storage is not working.'}
                                    elif 'rating' in database:
                                        sql = "insert into property_rating (username,rating,rating_date,property_id) values ('" + \
                                             result[0][0] + "'," \
                                                  "'" + database['rating'] + "',(select current_date from dual),'"+database['id']+"')"
                                        flag, sub_result = self.reader.execute_query(self.empty_result, cursor, sql)
                                        if flag:
                                            self.db_instance.commit()
                                            data = {'type': 1, 'resp': 'Your rating has been saved successfully'}
                                        else:
                                            data = {'type': 2,
                                                    'resp': 'Sorry, server storage is not working.'}
                                    else:
                                        data = {'type': 2, 'resp': 'Sorry, while due to not provided any information.'}
                                else:
                                    data = {'type': 0, 'resp': 'Error, while due to wrong username infomation.'}
                            else:
                                data = {'type': 2,
                                        'resp': 'Sorry, server storage is not working.'}
                        else:
                            data = {'type': 0, 'resp': 'Error, while due to connecting to server database.'}
                    else:
                        data = {'type': 0, 'resp': 'Error, while due to not provided property information.'}
                else:
                    data = {'type': 0, 'resp': 'Error, while due to not provided user information'}
            else:
                data = {'type': 0, 'resp': 'Error, while due to accessing approach'}
        except Exception,e:
            data={'type':0,'resp':'Error, while due to '+str(e)}
        return JsonResponse(data)

    def ope_save_property(self,request):
        try:
            if request.method=='POST':
                arguments=request.POST
                if 'mob_code' in arguments:
                    if 'status' in arguments:
                        sql,flag,err="",False,False
                        if arguments['status']=='clr':
                            flag=True
                            sql+="select property_id,property_name,category,price,address,city from property " \
                                 "where property_id in (select property_id from property_saving where" \
                                 " username=(select username from client_mobile where mob_code='"+arguments['mob_code']+"'))"
                        elif arguments['status']=='del':
                            if 'id' in arguments:
                                sql+="delete from property_saving where property_id='"+arguments['id']+"' and username=(select username from client_mobile where mob_code='"+arguments['mob_code']+"')"
                            else:
                                err=True
                        

                        if self.db_flag:
                            cursor=self.db_instance.cursor()
                            if err==False:
                                if flag:
                                    sub_flag, sub_result = self.reader.execute_query(self.for_result, cursor, sql)
                                else:
                                    sub_flag, sub_result = self.reader.execute_query(self.empty_result, cursor, sql)
                                if sub_flag:
                                    if flag==True:
                                        lst=[]
                                        for row in sub_result:
                                            dit={}
                                            dit.setdefault("id",row[0])
                                            dit.setdefault("title", row[1])
                                            dit.setdefault("category", row[2])
                                            dit.setdefault("price", self.reader.addComma(str(row[3])))
                                            dit.setdefault("address", row[4]+','+row[5])
                                            lst.append(dit)
                                        data = {'type': 1, 'resp': lst}
                                    else:
                                        self.db_instance.commit()
                                        data = {'type': 1, 'resp': 'Your request for delete saved property has been completed successfully.'}
                                else:
                                    data = {'type': 2, 'resp': 'Sorry, internal storage processing error found during updation.'}
                            else:
                                data = {'type': 2, 'resp': 'Sorry, internal storage processing error found.'}
                        else:
                            data = {'type': 2, 'resp': 'Sorry, internal storage error found during connecting.'}
                    else:
                        data = {'type': 0, 'resp': 'Error, while not found any request.'}
                else:
                    data = {'type': 0, 'resp': 'Error, while not user information.'}
            else:
                data = {'type': 0, 'resp': 'Error, while due to accessing wrong approach.'}
        except Exception,e:
            data={'type':0,'resp':'Error, while due to '+str(e)}
        return JsonResponse(data)


    def save_property(self,request):
        try:
            if 'POST'== request.method:
                http_arg=request.POST
                if 'mob_code' in http_arg:
                    if 'id' in http_arg:

                        if self.db_flag:
                            cursor = self.db_instance.cursor()
                            sql="select username from client_mobile where mob_code='"+http_arg['mob_code']+"'"
                            sub_flag, sub_result = self.reader.execute_query(self.for_result, cursor, sql)
                            if sub_flag:
                                if len(sub_result)>0:
                                    sql="insert into property_saving (property_id,username,saving_date)" \
                                    " values ('"+http_arg['id']+"','"+sub_result[0][0]+"',(select current_date from dual))"
                                    sub_flag, sub_result = self.reader.execute_query(self.empty_result, cursor, sql)
                                    if sub_flag:
                                        self.db_instance.commit()
                                        data = {'type': 1, 'resp': 'Property has been saved into your account.'}
                                    else:
                                        data = {'type': 2, 'resp': 'Sorry, while internal storage error found during updation.'}
                                else:
                                    data = {'type': 2, 'resp': 'Sorry, while not found authorize information of client.'}
                            else:
                                data = {'type': 2, 'resp': 'Sorry, while internal storage error found during searching.'}
                        else:
                            data = {'type': 2, 'resp': 'Sorry, while internal storage error found.'}
                    else:
                        data = {'type': 0, 'resp': 'Error, while due to missing information about property'}
                else:
                    data = {'type': 0, 'resp': 'Error, while missing client infomation'}
            else:
                data = {'type': 0, 'resp': 'Error, while accessing directly approach '}
        except Exception,e:
            data={'type':0,'resp':'Error, while due to '+str(e)}
        return JsonResponse(data)

    @csrf_exempt
    def send_email(self, request):
        try:
            if 'POST'== request.method:
                http_arg=request.POST
                if 'mob_code' in http_arg:
                    if 'id' in http_arg:

                        if self.db_flag:
                            cursor = self.db_instance.cursor()
                            sql = "select c.username,c.email,p.property_name from client c join property p on" \
                                  " (p.property_id='"+http_arg['id']+"' and c.username=(select username from property where property_id='"+http_arg['id']+"'))"
                            flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                            if flag:
                                if len(result) == 1:
                                    email = result[0][1]
                                    if email != None and len(email) > 0:
                                        sql = "select fullname,email,username from client where username=(select username"+\
                                          " from client_mobile where mob_code='"+http_arg['mob_code']+"')"
                                        sub_flag, sub_result = self.reader.execute_query(self.for_result, cursor, sql)
                                        if sub_flag:
                                            if len(sub_result) == 1:
                                                context = "<style>/* Shrink Wrap Layout Pattern CSS */@media only screen and (max-width: 599px) " \
                                                      "{td[class='hero'] img {  width: 100%; height: auto !important;}" \
                                                      " td[class='pattern'] td{  width: 100%;}}</style>" \
                                                      "<table cellpadding='0' cellspacing='0'><tr><td class='pattern' width='600'>" \
                                                      "<table cellpadding='0' cellspacing='0'><tr><td class='hero'>" \
                                                      "<img style='width:600px;height:460px;' src='https://images.pexels.com/photos/106399/pexels-photo-106399.jpeg?cs=srgb&dl=architecture-family-house-front-yard-106399.jpg&fm=jpg' alt='' style='display: block; border: 0;' /></td></tr><tr>" \
                                                      "<td style='font-family: arial,sans-serif; color: #333;margin-left:200px;'><h1>BookIt</h1></td></tr>" \
                                                      "<tr><td align='left' style='font-family: arial,sans-serif; font-size: 14px; line-height: 20px !important; color: #666; padding-bottom: 20px;'>" \
                                                      "Alert Message from BookIt<br> " + sub_result[0][0] + " : " + sub_result[0][1]+ \
                                                      "	is interested to your property<br>Property Name:" + \
                                                      result[0][2]

                                                context += "</td></tr><tr>" \
                                                       "<td align='left'><a href='192.168.137.1:8000/property-detail?id="+http_arg['id']+"'><img src='http://placehold.it/200x50/333&text=Check+it' alt='CTA' style='display: block; border: 0;' /></a>" \
                                                       "</td></tr></table></td></tr></table>"
                                                context = str(context.encode('ascii', 'ignore'))
                                                try:
                                                    t_flag = self.mail.sent_mail_client(email, '', unicode(context))
                                                    if t_flag:
                                                        sql = "insert into property_alert (username,property_id,type,send_date) values" \
                                                          " ('" + result[0][2]+ "','" + http_arg['id'] + "','email',(select current_date from dual))"
                                                        sub_flag, sub_rresult = self.reader.execute_query(self.empty_result, cursor, sql)
                                                        if sub_flag:
                                                            self.db_instance.commit()

                                                            self.addFriend(sub_result[0][2], result[0][0])
                                                            self.addFriend(result[0][0],sub_result[0][2])
                                                            data = {'type':1,'resp': 'Email is successfully sent!'}
                                                        else:
                                                            data = {'type': 2,
                                                                    'resp': 'Sorry,database is not working well during updation.'}
                                                    else:
                                                        data = {'type':2,'resp': 'Sorry,Email is not sent successfully.'}
                                                except Exception,e:
                                                    data = {'type':0,'resp': 'Error, while sending email to client.'+str(e)}

                                            else:
                                                data = {'type':0,'resp': 'Invalid user request for sending email'}
                                        else:
                                            data = {'type': 2, 'resp': 'Sorry, Sorry,database is not working well during searching.'}
                                    else:
                                        data = {'type':0,'resp': 'Email is not valid for processing.'}

                                else:
                                    data = {'type':0,'resp': 'Error, email address is not found for client.'}
                            else:
                                data = {'type': 2, 'resp': 'Sorry, Sorry,database is not working well during searching.'}
                        else:
                            data = {'type':0,'resp': 'Error, while connecting to database for infomation parsing.'}
                    else:
                        data = {'type':0,'resp': 'Error, while not found argument about property.'}
                else:
                    data = {'type':0,'resp': 'Error, while not found argument about client.'}
            else:
                data = {'type':0,'resp': 'Error, while accessing wrong approach.'}

        except Exception, e:
            data = {'resp': 'Error due to ' + str(e)}
        return JsonResponse(data)



    def send_sms(self,request):
        try:
            if request.method=='POST':
                http_arg=request.POST
                if 'mob_code' in http_arg:
                    if 'id' in http_arg:
                        sql="select m.username,m.fullname,m.phone,p.phone,c.property_name,p.username from client m join client p on(m.username=(select username from client_mobile " \
                            "where mob_code='"+http_arg['mob_code']+"') and p.username=(select username from property where property_id='"+http_arg['id']+"')) join property c" \
                                    " on(c.property_id='"+http_arg['id']+"')"

                        if self.db_flag:
                            cursor=self.db_instance.cursor()
                            flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                            if  flag:
                                if len(result)==1:
                                    fullname,c_phone,phone,title=result[0][1],result[0][2],result[0][3],result[0][4]
                                    if phone!=None and len(phone)>0:
                                        if '+' in phone:
                                            to=phone[1:]
                                        elif '00' in phone[0:2]:
                                            to = phone[2:]
                                        if self.sms.send(fullname,c_phone,to,title):
                                            sql = "insert into property_alert (username,property_id,type,send_date) values" \
                                                 " ('" + result[0][0] + "','" + http_arg[
                                                    'id'] + "','email',(select current_date from dual))"
                                            flag, sub_result = self.reader.execute_query(self.empty_result, cursor, sql)
                                            if flag:
                                                self.db_instance.commit()

                                                self.addFriend(result[0][0], result[0][5])
                                                self.addFriend(result[0][5], result[0][0])
                                                data = {'type': 1, 'resp': 'Sms has been sent successfully.'}
                                            else:
                                                data = {'type': 2,
                                                                    'resp': 'Sorry, server database is not working during updation'}
                                        else:
                                            data = {'type': 2,'resp': 'Sorry, sms is not sent yet.'}
                                    else:
                                        data = {'type': 2,'resp': 'Sorry, error found due to invalid phone number'}
                                else:
                                    data = {'type': 2, 'resp': 'Sms has not sent yet due to not found phone number'}
                            else:
                                data = {'type': 0, 'resp': 'Sms has not sent yet due to not found info.'}
                        else:
                            data = {'type': 0, 'resp': 'Sms has not sent yet due to searching info.'}
                    else:
                        data = {'type': 0, 'resp': 'Error, while missing property id.'}
                else:
                    data={'type':0,'resp':'Error, while missing authorize code.'}
            else:
                data={'type':0,'resp':'Error, while accessing directly'}
        except Exception,e:
            data={'type':0,'resp':'Error due to exception occurs.'+str(e)}
        return JsonResponse(data)

####################################################################################################################################################################################
###########################################################################Notification alerts#####################################################################################
###############################################################################################################################################################################

    def get_feedback_rating(self,request):
        try:
            if 'POST' == request.method:
                database_list=request.POST
                if 'id' in database_list:
                    sql="select avg(rating) from property_rating where property_id='"+database_list['id']+"'"

                    if self.db_flag:
                        dit={}
                        cursor=self.db_instance.cursor()
                        flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                        if flag:
                            if len(result)>0:
                                dit.setdefault("rating",str(result[0][0]))
                                sql="select c.fullname,f.feedback,f.feedback_date from client c join property_feedback f on " \
                                    "(f.property_id='"+database_list['id']+"' and c.username =(select username from " \
                                                              "property_feedback where property_id='"+database_list['id']+"')) order by feedback_date asc"
                                flag, sub_result = self.reader.execute_query(self.for_result, cursor, sql)
                                sub=[]
                                if flag:
                                    
                                    if len(sub_result)>0:
                                        for row in sub_result:
                                            dic={}
                                            dic.setdefault("fullname",row[0])
                                            dic.setdefault("feedback", row[1])
                                            sub.append(dic)
                                        dit.setdefault("feedback",sub)
                                        data={'type':1,"resp":dit}
                                    else:
                                        if len(dit)==0:
                                            data = {'type': 2, "resp": "Sorry, no record is found."}
                                        else:
                                            dit.setdefault("feedback",sub)
                                            data={'type':1,"resp":dit}
                                else:
                                    data = {'type': 2, "resp": "Sorry, while internal storage error found."}
                            else:
                                data = {'type': 2, "resp": "Sorry, no record is found."}
                        else:
                            data = {'type': 2, "resp": "Sorry, while internal storage error found."}
                    else:
                        data = {'type': 2, "resp": "Sorry, while internal storage error found." }
                else:
                    data = {'type': 0, "resp": "Error, while due to not providing info."}
            else:
                data = {'type': 0, "resp": "Error, while due to wrong approach."}
        except Exception,e:
            data = {'type': 0, "resp": "Error, while due to "+str(e)}
        return JsonResponse(data)

    def notification_alert(self,request):
        try:
            if request.method == 'POST':
                http_arg=request.POST
                sql,flag = "",False
                if 'm_code' in http_arg:
                    
                    if http_arg['arg'] == 'email':
                        sql += "select distinct p.property_name,a.username,a.send_date " \
                               "from property p join property_alert a on(p.property_id=a.property_id and" \
                            " a.property_id in (select property_id from property where " \
                             "username= (select username from client_mobile where mob_code='"+http_arg['m_code']+"')) " \
                                                        "and a.type='email') order by a.send_date desc"

                    elif http_arg['arg'] == 'sms':
                        sql += "select distinct p.property_name,a.username,a.send_date from" \
                           " property p join property_alert a on(p.property_id=a.property_id " \
                           "and a.property_id in (select property_id from property " \
                           "where username=(select username from client_mobile where mob_code='"+http_arg['m_code']+"'))" \
                                                                " and a.type='sms') order by a.send_date desc"

                    elif http_arg['arg'] == 'rating':
                        sql += "select distinct p.property_name,a.rating,a.username,a.rating_date from " \
                           "property p join property_rating a on(p.property_id=a.property_id and a.property_id in " \
                           "(select property_id from property where username=(select username from client_mobile where " \
                               "mob_code='"+http_arg['m_code']+"'))) order by a.rating_date desc"

                    elif http_arg['arg'] == 'feedback':
                        sql += "select distinct p.property_name,a.feedback,a.username,a.feedback_date from " \
                           "property p join property_feedback a on(p.property_id=a.property_id and a.property_id in " \
                           "(select property_id from property where username=(select username " \
                               "from client_mobile where mob_code='"+http_arg['m_code']+"'))) order by a.feedback_date desc"
                    else:
                        flag=True

                    if sql != "":
                        if flag==False:

                            if self.db_flag:
                                try:
                                    cursor = self.db_instance.cursor()
                                except Exception,e:
                                    print str(e)
                                    
                                sub_flag, sub_result = self.reader.execute_query(self.for_result, cursor, sql)
                                if sub_flag:

                                    if len(sub_result) == 0:
                                        data = {'type': 2, 'resp': 'Sorry, no result found for ' + str(http_arg['arg'])}
                                    else:
                                        result = []
                                        if http_arg['arg'] == 'sms' or http_arg == 'email':

                                            for _ in sub_flag:
                                                di = {}
                                                di.setdefault("id", _[0])
                                                di.setdefault("user", _[1])
                                                di.setdefault("date", _[2])
                                                result.append(di)
                                        elif http_arg['arg'] == 'feedback' or http_arg['arg'] == 'rating':

                                            for _ in sub_flag:
                                                di = {}
                                                di.setdefault("id", _[0])
                                                di.setdefault("resp", _[1])
                                                di.setdefault("user", _[2])
                                                di.setdefault("date", _[3])
                                                result.append(di)
                                        data = {'type': 1, 'resp': result}
                                else:
                                    data = {'type': 2, 'resp': 'Sorry, while internal storage error found during searching'}
                            else:
                                data = {'type': 2, 'resp': 'Sorry, while internal storage error found'}
                        else:
                            data = {'type': 0, 'resp': 'Error while request not fully recoginize for server'}
                    else:
                        data = {'type': 0, 'resp': 'Error while request not fully recoginize for server'}
                else:
                    data = {'type': 0, 'resp': 'Error while missing key for checking.'}
            else:
                data = {'type': 0, 'resp': 'Error while sending data to server.'}

        except Exception, e:
            data = {'type': 0, 'resp': 'Error due to ' + str(e)}


        return JsonResponse(data)

#############################################################################################################################################################################
###############################################################################################################################################################################
#########################################################################Contact with us#######################################################################################
#############################################################################################################################################################################

    def contact(self,request):
        try:
            database={}
            flag=False
            if request.method=='GET':
                database=request.GET
                flag=True
            elif request.method=='POST':
                database=request.POST
                flag=True
            if flag:
                if 'name' in database:
                    if 'email' in database:
                        if 'phone' in database:
                            if 'msg' in database:
                                sql="insert into contact " \
                                    "(name,email,phone,msg,contact_date) values ('"+database['name']+"'," \
                                            "'"+database['email']+"','"+database['phone']+"','"+database['msg']+"',(select current_date from dual))"

                                if self.db_flag:
                                    cursor=self.db_instance.cursor()
                                    sub_flag,result=self.reader.execute_query(self.empty_result,cursor,sql)
                                    if sub_flag:
                                        self.db_instance.commit()
                                        self.cronjob.contactJob()
                                        data = {'type': 1, 'resp': 'Your request has been completed.'}
                                    else:
                                        data = {'type': 2, 'resp': 'Sorry, your request is not completed.'}
                                else:
                                    data = {'type': 0, 'resp': 'Error, while connecting to database.'}
                            else:
                                data = {'type': 0, 'resp': 'Error, while missing message field.'}
                        else:
                            data = {'type': 0, 'resp': 'Error, while missing phone field.'}
                    else:
                        data = {'type': 0, 'resp': 'Error, while missing email field.'}
                else:
                    data = {'type': 0, 'resp': 'Error, while missing name field.'}
            else:
                data={'type':0,'resp':'Error, while could not recognize request.'}
        except Exception,e:
            data = {'type': 0, 'resp': 'Error due to exception occurs'}
        return JsonResponse(data)

    def subscribe(self,request):
        try:
            database = {}
            flag = False
            if request.method == 'GET':
                database = request.GET
                flag = True
            elif request.method == 'POST':
                database = request.POST
                flag = True
            if flag:
                if 'email' in database:
                    sql="select * from subscribe where email='"+database['email']+"'"

                    if self.db_flag:
                        cursor = self.db_instance.cursor()
                        sub_flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                        if sub_flag:
                            if len(result)==0:
                                sql = "insert into subscribe " \
                                "(email,s_date) values ('"+database['email'] + "',(select current_date from dual))"

                                sub_flag, result = self.reader.execute_query(self.empty_result, cursor, sql)
                                if sub_flag:
                                    self.db_instance.commit()
                                    data = {'type': 1, 'resp': 'Your request has been completed.'}
                                else:
                                    data = {'type': 2, 'resp': 'Sorry, Your request has not subscribed.'}
                            else:
                                data = {'type': 2, 'resp': 'Sorry, You already subscribed.'}
                        else:
                            data = {'type': 2, 'resp': 'Sorry, Your request is not subscribed due to database error found.'}
                    else:
                        data = {'type': 0, 'resp': 'Error, while connecting to database.'}
                else:
                    data = {'type': 0, 'resp': 'Error, while missing email field.'}
            else:
                data = {'type': 0, 'resp': 'Error, while could not reconginze request.'}

        except Exception, e:
            data = {'type': 0, 'resp': 'Error due to exception occurs'}
        return JsonResponse(data)


    ######################################################################################################################################################################
    #####################################################################Operation of Text Chat####################################################################################
    ########################################################################################################################################################################

    def getFriendlist(self,request):
        try:
            if request.method=='POST':
                arguments=request.POST
                if 'mob_code' in arguments:
                    sql="select fullname,username from client where username in " \
                        "(select client from client_friend where username=(select username from client_mobile where mob_code='"+arguments['mob_code']+"'))"

                    if self.db_flag:
                        cursor=self.db_instance.cursor()
                        sub_flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                        if sub_flag:
                            lst=[]
                            if len(result)>0:
                                for _ in result:
                                    lst.append({"name":_[0],"user":_[1]})
                            data = {'type': 1, 'resp': lst}
                        else:
                            data = {'type': 2, 'resp': 'Sorry, while internal storage error found.'}
                    else:
                        data = {'type': 2, 'resp': 'Sorry, while internal storage error found.'}
                else:
                    data = {'type': 0, 'resp': 'Error, while due to missing argument.'}
            else:
                data={'type':0,'resp':'Error, while due to accessing wrong approach.'}
        except Exception,e:
            data={'type':0,'resp':'Error due to '+str(e)}
        return JsonResponse(data)

    def sendMsg(self,request):
        try:
            if request.method=='POST':
                arguments=request.POST
                if 'mob_code' in arguments:
                    if 'client' in arguments:
                        if 'msg' in arguments:
                            username,f="",False
                            if self.db_flag:
                                cursor = self.db_instance.cursor()
                                if arguments['mob_code'] in self.client:
                                    username=self.client[arguments['mob_code']]
                                    f=True
                                else:
                                    sql="select username from client_mobile where mob_code='"+arguments['mob_code']+"'"
                                    sub_flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                                    if sub_flag:
                                        if len(result)>0:
                                            username=result[0][0]
                                            self.client.setdefault(arguments['mob_code'],username)
                                            f=True
                                    else:
                                        data = {'type': 2, 'resp': 'Sorry, error while due to database searching.'}        
                                if f:
                                    sql="insert into client_chat (username,client,msg,msg_date,flag)" \
                                                " values ('"+username+"','"+arguments['client']+"','"+arguments['msg']+"',(select current_date from dual),'clear')"
                                    sub_flag, result = self.reader.execute_query(self.empty_result, cursor, sql)
                                    if sub_flag:
                                        self.stack_message.setMessage(username,
                                                                          arguments['client'], arguments['msg'])
                                        self.db_instance.commit()
                                        data = {'type': 1, 'resp': 'Message sent successfully.'}
                                    else:
                                        data = {'type': 2, 'resp': 'Sorry, error while due to database updation.'}
                                else:
                                    data = {'type': 2, 'resp': 'Sorry, while found unauthorize information of client.'}
                                
                            else:
                                data = {'type': 0, 'resp': 'Error, while due to database connection.'}
                        else:
                            data={'type': 0, 'resp': 'Error, while due to missing message.'}
                    else:
                        data={'type': 0, 'resp': 'Error, while due to missing client info.'}
                else:
                    data = {'type': 0, 'resp': 'Error, while due to missing argument mobile ID.'}
            else:
                data={'type':0,'resp':'Error, while due to accessing wrong approach.'}
        except Exception,e:
            data={'type':0,'resp':'Error due to '+str(e)}
        print data
        return JsonResponse(data)



    def getChatHistory(self,request):
        try:
            if request.method == 'POST':
                arguments = request.POST
                if 'mob_code' in arguments:
                    if 'client' in arguments:
                        sql = "select username from client_mobile where mob_code='" + arguments['mob_code'] + "'"

                        if self.db_flag:
                            cursor = self.db_instance.cursor()
                            sub_flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                            if sub_flag:
                                if len(result) > 0:
                                    username = result[0][0]
                                    self.client.setdefault(arguments['mob_code'],username)
                                    sql = "select username,msg,msg_date from client_chat where username='" + username + \
                                        "' and client='" + arguments['client'] + "' or username='" +arguments['client'] + \
                                        "' and client='" + username + "' order by msg_date asc"

                                    sub_flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                                    if sub_flag:
                                        lst=[]
                                        if len(result)>0:
                                            for row in result:
                                                lst.append({"from":row[0],'msg':row[1],'date':str(row[2])})
                                        data = {'type': 1, 'resp': lst}
                                    else:
                                        data = {'type': 2, 'resp': 'Sorry, error while due to database searching.'}
                                else:
                                    data = {'type': 2, 'resp': 'Sorry, while found unauthorize information of client.'}
                            else:
                                data = {'type': 2, 'resp': 'Sorry, error while due to database searching.'}
                        else:
                            data = {'type': 0, 'resp': 'Error, while due to database connection.'}
                    else:
                        data = {'type': 0, 'resp': 'Error, while due to missing client info.'}
                else:
                    data = {'type': 0, 'resp': 'Error, while due to missing argument mobile ID.'}
            else:
                data = {'type': 0, 'resp': 'Error, while due to accessing wrong approach.'}
        except Exception, e:
            data = {'type': 0, 'resp': 'Error due to ' + str(e)}
        
        return JsonResponse(data)


    def getReceiveMsg(self,request):
        try:
            if request.method == 'POST':
                arguments = request.POST
                if 'mob_code' in arguments:
                    if 'client' in arguments:
                        if self.db_flag:
                            cursor = self.db_instance.cursor()
                            username,f="",False
                            if arguments['mob_code'] in self.client:
                                username=self.client[arguments['mob_code']]
                                f=True
                            else:    
                                sql = "select username from client_mobile where mob_code='" + arguments['mob_code'] + "'"
                                sub_flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                                if sub_flag:
                                    if len(result) > 0:
                                        username = result[0][0]
                                        self.client.setdefault(arguments['mob_code'],username)
                                
                                else:
                                    data = {'type': 2, 'resp': 'Sorry, error while due to database searching.'}    
                            if f:
                                print username
                                print arguments['client']
                                data = {'type':1,
                                            'resp': [{'msg':self.stack_message.getMessage(arguments['client'], username)}]}
                            else:
                                data = {'type': 2, 'resp': 'Sorry, while found unauthorize information of client.'}
                            
                                
                        else:
                            data = {'type': 0, 'resp': 'Error, while due to database connection.'}
                    else:
                        data = {'type': 0, 'resp': 'Error, while due to missing client info.'}
                else:
                    data = {'type': 0, 'resp': 'Error, while due to missing argument mobile ID.'}
            else:
                data = {'type': 0, 'resp': 'Error, while due to accessing wrong approach.'}
        except Exception, e:
            data = {'type': 0, 'resp': 'Error due to ' + str(e)}
        print data

        return JsonResponse(data)



    def generate_video_session(self,request):
        try:
            if request.method=="POST":
                http_arg=request.POST
                if 'mob_code' in http_arg:
                    if 'client' in http_arg:
                        print http_arg['mob_code']
                        flag,user=self.getUsername(http_arg['mob_code'])
                        if flag:
                            if len(user)>0:
                                print user
                                return self.chat_obj.get_session_token(user,http_arg['client'])
                            else:
                                data={'type':2,'resp':'Sorry, User is not recoginize.'}
                        else:
                            data={'type':2,'resp':'Sorry, while found unauthorize information of client.'}
                    else:
                        data = {'type': 0, 'resp': 'Error, while missing client info.'}
                else:
                    data = {'type': 0, 'resp': 'Error, while missing user info.'}
            else:
                data = {'type': 0, 'resp': 'Error, while accessing wrongly.'}
        except Exception,e:
            data = {'type': 0, 'resp': 'Error, while due to '+str(e)}
        return JsonResponse(data,safe=False)


    def getUsername(self,m_code):
        check,name=False,""
        try:
            sql = "select username from client_mobile where mob_code ='" + m_code + "'"

            if self.db_flag:
                cursor = self.db_instance.cursor()
                sub_flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                if sub_flag:
                    if len(result) > 0:
                        name = result[0][0]
                        check=True

        except Exception,e:
            check= False
        return check,name






################# ############################################################################################################################################################
############################################################################################################################################################################
#############################################################################################################################################################################
