from django.shortcuts import render
from django.http import request,JsonResponse, request,HttpResponse
from dbconfig import DataBase
from django.views.decorators.csrf import csrf_exempt
from reader import Reader

class Client_Information:
    def __init__(self,flag,instance):
        self.db_flag=flag
        self.db_instance=instance
        self.for_result=True
        self.empty_result=False
        self.reader=Reader()


    def setting(self,request):
        error,data="",{}
        try:
            if '__auth_log' in request.session:
                if request.session['__auth_log']==1:
                    sql="select fullname,username,email,address,phone,issue_date,verify_date,status from client where username='"+request.session['fuser']+"'"

                    if self.db_flag:
                        cursor=self.db_instance.cursor()
                        flag,result=self.reader.execute_query(self.for_result,cursor,sql)
                        if flag:
                            if len(result)==1:
                                data={}
                                data.setdefault('name',result[0][0])
                                data.setdefault('user', result[0][1])
                                data.setdefault('email', result[0][2])
                                data.setdefault('address', result[0][3])
                                data.setdefault('phone', result[0][4])
                                data.setdefault('issue_date',result[0][5])
                                data.setdefault('verify_date', result[0][6])
                                if result[0][7]==0:
                                    data.setdefault('status', "Unactivated")
                                elif result[0][7]==1:
                                    data.setdefault('status', "Activated")
                            else:
                                error="User's account profile error"
                        else:
                            error="Sorry, error while processing to storage."
                    else:
                        error="Sorry, error while connecting to storage/database."

                    return render(request, 'settings.html', {'error': error,
                                                                'logvalue': request.session['__auth_log'],
                                                                'fname': request.session['fname'],
                                                                'status': request.session['status'], 'data': data})
                else:
                    error="Sorry, you are using expired session. Please login again."
            else:
                error="Please login to access this page."
            return render(request, 'settings.html',  {'error': error,
                                                            'logvalue': 0,
                                                            'fname': '',
                                                            'status': -1, 'data': data})

        except Exception,e:
            return render(request, 'settings.html', {'error': 'Sorry, something is going wrong.'})

    def verify(self,request):
        try:
            return render(request,'verify-client.html',{'error':'','logvalue':request.session['__auth_log'],'fname':request.session['fname'] ,'status':request.session['status']})
        except Exception,e:
            return render(request, 'verify-client.html', {'error': str(e),'logvalue':request.session['__auth_log'],'fname':request.session['fname'] ,'status':request.session['status']})



    @csrf_exempt
    def change_password(self,request):
        try:
            if '__auth_log' in request.session:
                if request.session['__auth_log']==1:
                    if request.method=="POST":
                        if "old_pass" in request.POST and request.POST['old_pass']>7:
                            if 'new_pass' in request.POST and request.POST['new_pass']>7:
                                if 'con_pass' in request.POST and request.POST['con_pass']>7:
                                    if request.POST['con_pass']==request.POST['new_pass']:
                                        sql="select * from client where username='"+request.session['fuser']+"' and password='"+request.POST['old_pass']+"'"

                                        if self.db_flag:
                                            cursor=self.db_instance.cursor()
                                            flag,result=self.reader.execute_query(self.for_result,cursor,sql)
                                            if flag:
                                                if len(result)==1:
                                                    sql="update client set password ='"+request.POST['new_pass']+"' where username='"+request.session['fuser']+"'"
                                                    flag, result = self.reader.execute_query(self.empty_result, cursor,sql)
                                                    if flag:
                                                        self.db_instance.commit()
                                                        data={'type':1,'resp':'Your Password has been changed successfully'}
                                                    else:
                                                        data = {'type': 2,
                                                                'resp': 'Sorry, error while updating into storage/database.'}
                                                else:
                                                    data = {'type': 2,
                                                        'resp': 'Sorry, your old password is invalid'}
                                            else:
                                                data = {'type': 2,
                                                        'resp': 'Sorry, error while searching into storage/database.'}
                                        else:
                                            data = {'type': 2,
                                                    'resp': 'Sorry, storage internal error is found.'}
                                    else:
                                        data = {'type': 2,
                                                'resp': 'Sorry, your new and confirm passwords did not matched.'}
                                else:
                                    data = {'type': 0,
                                            'resp': 'Error due to while missing arguments.'}
                            else:
                                data = {'type': 0,
                                        'resp': 'Error due to while missing arguments.'}
                        else:
                            data = {'type': 0,
                                    'resp': 'Error due to while missing arguments.'}
                    else:
                        data = {'type': 0,
                                'resp': 'Error due to while accessing wrong.'}
                else:
                    data = {'type': 0,
                            'resp': 'Error due to while accessing with expired session.'}
            else:
                data = {'type': 0,
                        'resp': 'Error due to while unkown session found.'}
        except Exception,e:
            data={'type':0,'resp':'Error due to '+str(e)}
        return JsonResponse(data)

    @csrf_exempt
    def deactive_account(self,request):
        try:
            if '__auth_log' in request.session:
                if request.session['__auth_log'] == 1:
                    if request.method == "POST":
                        sql = "update client set status=-1 where username='"+request.session['fuser']+"'"

                        if self.db_flag:
                            cursor = self.db_instance.cursor()
                            flag,result=self.reader.execute_query(self.empty_result,cursor,sql)
                            if flag:
                                self.db_instance.commit()
                                data = {'type': 1,'resp': 'Your Account has been deactivited successfully. After logout, you cannot be login again.'}
                            else:
                                data = {'type': 2,
                                        'resp': 'Sorry, storage updation error found.'}
                        else:
                            data = {'type': 2,
                                            'resp': 'Sorry, storage internal error is found.'}
                    else:
                        data = {'type': 0,
                                'resp': 'Error due to while accessing wrong.'}
                else:
                    data = {'type': 0,
                            'resp': 'Error due to while accessing with expired session.'}
            else:
                data = {'type': 0,
                        'resp': 'Error due to while unkown session found.'}
        except Exception,e:
            data = {'type': 0, 'resp': 'Error due to ' + str(e)}
        return JsonResponse(data)



    @csrf_exempt
    def change_profile(self, request):
        try:
            if '__auth_log' in request.session:
                if request.session['__auth_log'] == 1:
                    if request.method == "POST":
                        sql = "update client set"
                        flag=False
                        if 'fullname' in request.POST:
                            flag=True
                            sql+=" fullname='"+request.POST['fullname']+"'"
                        if 'email' in request.POST:
                            if flag:
                                sql+=","
                            sql+=" email='"+request.POST['email']+"'"
                            flag=True
                        if 'address' in request.POST:
                            if flag:
                                sql += ","
                            sql += " address='" + request.POST['address'] + "'"
                            flag = True
                        if 'address' in request.POST:
                            if flag:
                                sql += ","
                            sql += " phone='" + request.POST['phone'] + "'"
                            flag = True
                        if flag:
                            sql+= " where username='"+request.session['fuser']+"'"

                            if self.db_flag:
                                cursor = self.db_instance.cursor()
                                flag,result=self.reader.execute_query(self.empty_result,cursor,sql)
                                if flag:
                                    self.db_instance.commit()
                                    data = {'type': 1, 'resp': 'Your Profile has been changed successfully'}
                                else:
                                    data = {'type': 2,
                                            'resp': 'Sorry, storage updation error is found.'}
                            else:
                                data = {'type': 2,
                                    'resp': 'Sorry, storage internal error is found.'}
                        else:
                            data = {'type': 2,
                                    'resp': 'Sorry, please select at least one attribute of profile to change.'}
                    else:
                        data = {'type': 0,
                                'resp': 'Error due to while accessing wrong.'}
                else:
                    data = {'type': 0,
                            'resp': 'Error due to while accessing with expired session.'}
            else:
                data = {'type': 0,
                        'resp': 'Error due to while unkown session found.'}
        except Exception,e:
            data = {'type': 0, 'resp': 'Error due to ' + str(e)}
        print data
        return JsonResponse(data)



    @csrf_exempt
    def delete_ad(self,request):
        error=False
        try:
            if '__auth_log' in request.session:
                if request.session['__auth_log']==1:
                    if request.method=="POST":
                        if 'p_id' in request.POST:

                            if self.db_flag:
                                list_query=[]

                                list_query.append("delete from property_alert where property_id='"+request.POST['p_id']+"'")
                                list_query.append("delete from property_detail where property_id='" + request.POST['p_id'] + "'")
                                list_query.append("delete from property_feedback where property_id='" + request.POST['p_id'] + "'")
                                list_query.append("delete from property_media where property_id='" + request.POST['p_id'] + "'")
                                list_query.append("delete from property_rating where property_id='" + request.POST['p_id'] + "'")
                                list_query.append("delete from property_saving where property_id='" + request.POST['p_id'] + "'")
                                list_query.append("delete from property where property_id='" + request.POST['p_id'] + "'")
                                cursor=self.db_instance.cursor()
                                for query in list_query:
                                    flag,result=self.reader.execute_query(self.empty_result,cursor,query)
                                    if flag:
                                        continue
                                    else:
                                        error=True
                                        break
                                if error==False:
                                    self.db_instance.commit()
                                    data = {'type': 1, 'resp': 'Your property ad has been deleted.'}
                                else:
                                    data = {'type': 2, 'resp': 'Your property ad has not been deleted yet due to storage updation error found.'}
                            else:
                                data = {'type': 2, 'resp': 'Sorry, while internal storage error found.'}
                        else:
                            data = {'type': 2,
                                    'resp': 'Sorry, property id is missing to procceed.'}
                    else:
                        data = {'type': 0,
                                'resp': 'Error due to while accessing wrong.'}
                else:
                    data = {'type': 0, 'resp': 'Error, while not recognize information.'}
            else:
                data = {'type':0,'resp': 'Error, while accessing expiring session.'}
        except:
            data={'type':0,'resp':'Error due to exception occurs'}
        return JsonResponse(data)




    @csrf_exempt
    def getAdsHistory(self,request):
        try:
            if '__auth_log' in request.session:
                if request.session['__auth_log']==1:
                    sql="select property_id,property_name,category,address,city,price from property" \
                        " where username='"+request.session['fuser']+"'"
                    if self.db_flag:
                        cursor=self.db_instance.cursor()

                        flag,result=self.reader.execute_query(self.for_result,cursor,sql)
                        if flag:
                            if len(result)>0:
                                lst=[]
                                for row in result:
                                    dic={}
                                    dic.setdefault("id",row[0])
                                    dic.setdefault("title", row[1])
                                    dic.setdefault("category", row[2])
                                    dic.setdefault("address", row[3])
                                    dic.setdefault("city", row[4])
                                    dic.setdefault("price", self.reader.addComma(row[5]))
                                    dic.setdefault("img",self.getImage(cursor,row[0]))
                                    lst.append(dic)
                                data={'type':1,'resp':lst}
                            else:
                                data = {'type': 0, 'resp': 'No result founds'}
                        else:
                            data = {'type': 0, 'resp': 'Sorry, error is found while searching into storage.'}
                    else:
                        data = {'type': 0, 'resp': 'Error, while connecting to database.'}
                else:
                    data = {'type': 0, 'resp': 'Error, while not recognize information.'}
            else:
                data = {'type':0,'resp': 'Error, while accessing expiring session.'}
        except:
            data={'type':0,'resp':'Error due to exception occurs'}
        return JsonResponse(data)


    @csrf_exempt
    def deleteads(self,request):
        try:
            if '__auth_log' in request.session:
                if request.session['__auth_log'] == 1:
                    if request.method=='POST':
                        if 'p_id' in request.POST:
                            sql = "delete from property_saving where username='"+request.session['fuser']+"' and property_id='"+request.POST['p_id']+"'"

                            if self.db_flag:
                                cursor = self.db_instance.cursor()
                                flag,result=self.reader.execute_query(self.empty_result,cursor,sql)
                                if flag:
                                    self.db_instance.commit()
                                    data = {'type': 1, 'resp': 'Saved property has been deleted.'}
                                else:
                                    data = {'type': 0, 'resp': 'Error, while updating to database.'}
                            else:
                                data = {'type': 0, 'resp': 'Error, while connecting to database.'}
                        else:
                            data = {'type': 0, 'resp': 'Error, while missing argument for processing.'}
                    else:
                        data = {'type': 0, 'resp': 'Error, while accessing directly.'}
                else:
                    data = {'type': 0, 'resp': 'Error, while not recognize information.'}
            else:
                data = {'type': 0, 'resp': 'Error, while accessing expiring session.'}
        except:
            data={'type':0,'resp':'Error due to exception occurs'}
        return JsonResponse(data)

    def verification(self,request):
        try:
            if request.method=='GET':
                if '__auth_log' in request.session:
                    if request.session['__auth_log']==1:
                        sql="select verify_code,status from client where username='"+request.session['fuser']+"'"

                        if self.db_flag:
                            cursor=self.db_instance.cursor()
                            flag,result=self.reader.execute_query(self.for_result,cursor,sql)
                            if flag:
                                if len(result)==1:
                                    if result[0][0]==request.GET['scode']:
                                        if result[0][1]==0:
                                            try:
                                                sql="update client set verify_date=(select current_date from dual),status=1 where username='"+request.session['fuser']+"'"
                                                flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                                                if flag:
                                                    self.db_instance.commit()
                                                    data={'is_taken':'Your account has been activited successfully.'}
                                                else:
                                                    data = {'is_taken': 'Your account has not been activited successfully yet.'}
                                            except Exception,e:
                                                data = {'is_taken': 'Error due to '+str(e)}
                                        else:
                                            data={'':'Your account already activited.'}
                                    else:
                                        data = {'is_taken': 'Your security code did not matched.'}
                                else:
                                    data = {'is_taken': 'Your record about verification bot found.'}
                            else:
                                data = {'is_taken': 'Sorry, error found while searching data.'}
                        else:
                            data = {'is_taken': 'Database connection error due to some services down.'}
                    else:
                        data = {'is_taken': 'Your auth key may be lost. Please login again.'}
                else:
                    data = {'is_taken': 'Please login.'}
            else:
                data = {'is_taken': 'Could not be accessible directly.'}
        except Exception,e:
            data = {'is_taken': 'Error due to '+str(e)+'.'}
        return JsonResponse(data)





    def getSaved(self,user):
        result,lst=0,[]
        try:
            sql="select p.property_id,p.property_name,p.price,to_char(s.saving_date,'dd-Mon-yyyy'),c.fullname"\
                " from client c join property p on(c.username='"+user+"') join property_saving s on(p.property_id=s.property_id) order by s.saving_date desc"
            if self.db_flag:
                cursor=self.db_instance.cursor()
                flag,result=self.reader.execute_query(self.for_result,cursor,sql)
                if flag:
                    if len(result)!=0:
                        for item in result:
                            di={}
                            di.setdefault("id",item[0])
                            di.setdefault("name", item[1])
                            di.setdefault("price", self.reader.addComma(str(item[2])))
                            di.setdefault("date", item[3])
                            di.setdefault("fullname",item[4])
                            di.setdefault("img",self.getImage(cursor,item[0]))
                            lst.append(di)
                        result=1

        except Exception,e:
            result, lst = 0, []
        return result,lst

    def send_information(self,request,page,arg):
        check = False
        resp=[]
        if '__auth_log' in request.session:
            if request.session['__auth_log'] == 1:
                check = True
        try:
            if check:
                if arg==1:
                    arg, resp=self.getSaved(request.session['fuser'])
                return render(request, page+'.html', {'error': '', 'logvalue': request.session['__auth_log'],
                                                             'fname': request.session['fname'],
                                                             'status': request.session['status'],'res':arg,'data':resp})
        except Exception, e:
            if (check == False):
                return render(request, page+'.html',
                              {'error': 'Error due to ' + str(e), 'logvalue': 0, 'fname': '',
                               'status': -1,'res':arg,'data':resp})
            return render(request, page+'.html',
                          {'error': 'Error due to ' + str(e), 'logvalue': request.session['__auth_log'],
                           'fname': request.session['fname'],
                           'status': request.session['status'],'res':arg,'data':resp})


    def notification(self,request):
        return self.send_information(request,'notification',0)

    def saved_properties(self, request):
        return self.send_information(request,'saved',1)

###########################################################################################################################################################################
###########################################################################################################################################################################
###########################################################################################################################################################################




    def getImage(self,cursor,p_id):
        val="default.jpg"
        try:
            sql = "select path from property_media where property_id='" + p_id + "' and type in ('jpg','jpeg','png','bmp','gif')"
            flag,result=self.reader.execute_query(self.for_result,cursor,sql)
            if flag:
                if len(result) > 0:
                    val=p_id+"/"+result[0][0]
        except:
            val="default.jpg"
        return val



    @csrf_exempt
    def notification_alert(self,request):
        try:
            if '__auth_log' in request.session:
                if request.method=='POST':
                    sql=""
                    if request.POST['arg']=='Email':
                        sql+="select distinct p.property_name,c.fullname,a.send_date,p.property_id " \
                             "from property p join property_alert a on(p.property_id=a.property_id and" \
                             " a.property_id in (select property_id from property where " \
                            "username='"+request.session['fuser']+"') and a.type='email') join client c on(c.username=a.username) order by a.send_date desc"

                    elif request.POST['arg'] == 'SMS':
                        sql+="select distinct p.property_name,c.fullname,a.send_date,p.property_id from" \
                             " property p join property_alert a on(p.property_id=a.property_id " \
                             "and a.property_id in (select property_id from property " \
                             "where username='"+request.session['fuser']+"') and a.type='sms') join client c on(c.username=a.username) order by a.send_date desc"

                    elif request.POST['arg'] == 'Rating':
                        sql+="select distinct p.property_name,a.rating,c.fullname,a.rating_date,p.property_id from property p "\
                             "join property_rating a on(p.property_id=a.property_id and a.property_id in (select property_id"\
                             " from property where username='"+request.session['fuser']+"'))  join client c on(c.username=a.username) order by a.rating_date desc"

                    elif request.POST['arg'] == 'Feedback':
                        sql+="select distinct p.property_name,a.feedback,c.fullname,a.feedback_date,p.property_id from " \
                             "property p join property_feedback a on(p.property_id=a.property_id and a.property_id in " \
                             "(select property_id from property where username='"+request.session['fuser']+"')) join client c "\
                                                    "on(c.username=a.username) order by a.feedback_date desc"

                    elif request.POST['arg'] == 'Payment':
                        sql="select distinct p.property_name,c.fullname,a.request_date,p.property_id from property"\
                             " p join payment_request a on(p.property_id=a.property_id and a.property_id in(select"\
                             " property_id from property where username='"+request.session['fuser']+"')) join client c on(c.username=a.username) order by a.request_date desc"

                    elif request.POST['arg'] == 'Response':
                        sql="select distinct p.property_name,p.property_id,c.fullname,pi.branch,pi.account_no from" \
                            " property p join payment_request pr on(pr.username='"+request.session['fuser']+"' and p.property_id=pr.property_id " \
                            "and acception='accepted') join payment_info pi on(pi.username=(select username from property" \
                            " where property_id=p.property_id)) join client c on(c.username=pi.username)"
                    if sql!="":

                        if self.db_flag:
                            cursor=self.db_instance.cursor()
                            flag,result=self.reader.execute_query(self.for_result,cursor,sql)
                            if flag:
                            
                                if len(result)==0:
                                    data={'type':0,'resp':'No result found for '+request.POST['arg']}
                                else:
                                    resp_result=[]

                                    if request.POST['arg']=='SMS' or request.POST['arg']=='Email' or request.POST['arg']=='Payment':
                                        
                                        for _ in result:
                                            di={}
                                            di.setdefault("name",_[0])
                                            di.setdefault("user",_[1] )
                                            di.setdefault("date", _[2])
                                            di.setdefault("id",_[3])
                                            di.setdefault("img",self.getImage(cursor,_[3]))
                                            resp_result.append(di)
                                    if request.POST['arg']=='Response':
                                        for _ in result:
                                            di={}
                                            di.setdefault("name",_[0])
                                            di.setdefault("user",_[2] )
                                            di.setdefault("branch", _[3])
                                            di.setdefault("account", _[4])
                                            di.setdefault("id",_[1])
                                            di.setdefault("img",self.getImage(cursor,_[1]))
                                            resp_result.append(di)


                                    elif request.POST['arg']=='Feedback' or request.POST['arg']=='Rating':
                                        for _ in result:
                                            di={}
                                            di.setdefault("name",_[0])
                                            di.setdefault("resp", _[1])
                                            di.setdefault("user",_[2] )
                                            di.setdefault("date", _[3])
                                            di.setdefault("id", _[4])
                                            di.setdefault("img", self.getImage(cursor, _[3]))
                                            resp_result.append(di)
                                    data = {'type':1,'resp': resp_result}
                            else:
                                data = {'type': 0, 'resp': 'Error while searching to database.'}
                        else:
                            data = {'type':0,'resp': 'Error while connecting to database'}
                    else:
                        data = {'type':0,'resp': 'Error while request not fully recoginize for server'}
                else:
                    data = {'type':0,'resp': 'Error while sending data to server'}
            else:
                data = {'type':0,'resp': 'Error while accessing directly without login.'}
        except Exception,e:
            data={'type':0,'resp':'Error due to '+str(e)}
        return JsonResponse(data)


#####################################################################################################################################################################
########################################################Saved Property Option########################################################################################
######################################################################################################################################################################


    def checkSavedProperty(self,cursor,user,p_id):
        flag=False
        try:
            sql="select * from property_saving where username='"+user+"' and property_id='"+p_id+"'"
            flag, result = self.reader.execute_query(self.for_result, cursor, sql)
            if flag:
                if len(result)==0:
                    flag=True
        except:
            flag=False
        return flag


    @csrf_exempt
    def saved_property_to_acc(self,request):
        try:
            if request.method=="POST":
                if 'id' in request.POST:
                    if '__auth_log' in request.session:
                        if request.session['__auth_log'] == 1:

                            if self.db_flag:
                                cursor=self.db_instance.cursor()
                                if self.checkSavedProperty(cursor,request.session['fuser'],request.POST['id']):
                                    sql="insert into property_saving (property_id,username,saving_date) values ('"+request.POST['id']+\
                                        "','"+request.session['fuser']+"',(select current_date from dual))"
                                    flag, result = self.reader.execute_query(self.empty_result, cursor, sql)
                                    if flag:
                                        data = {'type': 1, 'resp': 'Property has been saved into account.'}
                                    else:
                                        data = {'type': 0, 'resp': 'Sorry, error is found during saving property information into account.'}
                                else:
                                    data = {'type': 1, 'resp': 'You already saved this property to your account.'}
                            else:
                                data = {'type': 0, 'resp': 'Error while connecting to database.'}

                        else:
                            data = {'type': 0, 'resp': 'Error while request not fully recoginize for server'}
                    else:
                        data = {'type': 0, 'resp': 'Error while accessing directly without login.'}
                else:
                    data = {'type': 0, 'resp': 'Error while due to missing property id.'}
            else:
                data = {'type': 0, 'resp': 'Error while accessing directly.'}
        except Exception, e:
            data = {'type': 0, 'resp': 'Error due to ' + str(e)}
        return JsonResponse(data)



    def editads(self,request):
        data,resp={},0
        error=""
        try:
            if '__auth_log' in request.session:
                if request.session['__auth_log']==1:
                    if request.method=="GET":
                        if 'id' in request.GET:
                            data={}
                            sql="select property_name,description,address,city,price,category,type,area from property where property_id='"+request.GET['id']+"'"

                            if self.db_flag:
                                cursor=self.db_instance.cursor()
                                flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                                if flag:
                                    if len(result)==1:
                                        data.setdefault("name",result[0][0])
                                        data.setdefault("desc",result[0][1] )
                                        data.setdefault("address",result[0][2] )
                                        data.setdefault("city", result[0][3])
                                        data.setdefault("price", result[0][4])

                                        data.setdefault("category", self.getNumberfromString("category",result[0][5]))
                                        data.setdefault("type",  self.getNumberfromString("type",result[0][6]))
                                        area=result[0][7].split(' ')
                                        try:
                                            data.setdefault("area", int(area[0]))
                                            data.setdefault("area2",  self.getNumberfromString("category",area[1]))
                                        except:
                                            data.setdefault("area", area[0][:2])
                                            data.setdefault("area2", self.getNumberfromString("category", "Area"))
                                        resp=1
                                        sql="select bed,living,park,kitchen from property_detail where property_id='"+request.GET['id']+"'"
                                        flag, result = self.reader.execute_query(self.for_result, cursor, sql)

                                        if flag:
                                            if len(result)>0:
                                                data.setdefault("bed",result[0][0])
                                                data.setdefault("living", result[0][1])
                                                data.setdefault("parking",result[0][2] )
                                                data.setdefault("kitchen",result[0][3] )
                                                resp = 1

                                    else:
                                        error= "empty result found"
                                else:
                                    error="query error found"

        except Exception,e:

            resp=0
        numb=self.reader.getData('Numbering')
        return render(request, "editads.html", {'logvalue': request.session['__auth_log'],
                                                             'fname': request.session['fname'],
                                                             'status': request.session['status'],'res': resp,'resp':data,'number':numb})

    def getNumberfromString(self,handle,args):
        count=0
        if handle=='category':
            if args=="Buy":
                count=0
            elif args=="Rent":
                count=1
            elif args=="Sale":
                count=2
        elif handle=='type':
            if args=="Appartment":
                count=0
            elif args=="Flat":
                count=1
            elif args=="House":
                count=2
            elif args=="Office":
                count=3
        elif handle == 'area':
            if args=="Marla":
                count=0
            elif args=="Canal":
                count=1
            elif args=="Acre":
                count=2
            elif args=="Square feet":
                count=3
        return count


    @csrf_exempt
    def submitEditAds(self,request):
        try:
            if '__auth_log' in request.session and request.session['__auth_log']==1:
                if request.method=="POST":
                    if 'title' in request.POST:
                        if 'desc' in request.POST:
                            if 'address' in request.POST:
                                if 'city' in request.POST:
                                    if 'price' in request.POST:
                                        if 'category' in request.POST:
                                            if 'type' in request.POST:
                                                if 'bed' in request.POST:
                                                    if 'living' in request.POST:
                                                        if 'parking' in request.POST:
                                                            if 'kitchen' in request.POST:
                                                                if 'area' in request.POST:
                                                                    if 'p_id' in request.POST:
                                                                        sql="update property set property_name='"+request.POST['title']+\
                                                                            "',description='"+request.POST['desc']+"',address='"+request.POST['address']+\
                                                                            "',city='"+request.POST['city']+"',price="+request.POST['price']+",category='"+request.POST['category']+\
                                                                            "',type='"+request.POST['type']+"',area='"+request.POST['area']+\
                                                                            "' where property_id='"+request.POST['p_id']+"'"
                                                                        if self.db_flag:
                                                                            cursor=self.db_instance.cursor()
                                                                            try:
                                                                                flag,result=self.reader.execute_query(self.empty_result,cursor,sql)
                                                                                if flag:
                                                                                    sql = "update property_detail set bed="+request.POST['bed']+",living="+request.POST['living']+\
                                                                                        ",park="+request.POST['parking']+",kitchen="+request.POST['kitchen']+\
                                                                                        " where property_id='"+request.POST['p_id']+"'"
                                                                                    flag,result=self.reader.execute_query(self.empty_result,cursor,sql)
                                                                                    if flag:
                                                                                        self.db_instance.commit()
                                                                                        data = {'type': 1,
                                                                                                'resp': "Congrates, Your request is executed successfully."}
                                                                                    else:
                                                                                        data = {'type': 0,
                                                                                                'resp': "Sorry, Your request is not executed successfully."}
                                                                                else:

                                                                                    data = {'type': 0,
                                                                                            'resp': "Sorry, Your request is not executed successfully."}
                                                                            except Exception,e:
                                                                                data = {'type': 0,
                                                                                        'resp': "Sorry, something is wrong during updation."}
                                                                        else:
                                                                            data = {'type': 0,
                                                                                    'resp': "Sorry, property ID is missing to procceed."}
                                                                    else:
                                                                        data = {'type': 0,'resp': "Sorry, property ID is missing to procceed."}
                                                                else:
                                                                    data = {'type': 0,'resp': "Sorry, property area field is missing."}
                                                            else:
                                                                data = {'type': 0,
                                                                        'resp': "Sorry, property kitchen field is missing. "}
                                                        else:
                                                            data = {'type': 0,
                                                                    'resp': "Sorry, property parking field is missing."}
                                                    else:
                                                        data = {'type': 0,
                                                                'resp': "Sorry, property living rooms field is missing."}
                                                else:
                                                    data = {'type': 0,
                                                            'resp': "Sorry, property bed rooms field is missing."}
                                            else:
                                                data = {'type': 0, 'resp': "Sorry, property type field is missing."}
                                        else:
                                            data = {'type': 0, 'resp': "Sorry, property category field is missing."}
                                    else:
                                        data = {'type': 0, 'resp': "Sorry, property price field is missing."}
                                else:
                                    data = {'type': 0, 'resp': "Sorry, property city field is missing."}
                            else:
                                data = {'type': 0, 'resp': "Sorry, property address field is missing."}
                        else:
                            data = {'type': 0, 'resp': "Sorry, property description field is missing."}
                    else:
                        data = {'type': 0, 'resp': "Sorry, property title field is missing."}
                else:
                    data = {'type': 0, 'resp': "Sorry, something is goning wrong due to accessing wrong."}
            else:
                data = {'type': 0, 'resp': "Sorry, Please login to procceed request."}

        except Exception,e:
            data={'type':0,'resp':"Sorry, something is goning wrong due to "+str(e)}
        return JsonResponse(data)



    def check_request(self,cursor,user,p_id):
        flag=False
        try:
            sql="select acception from payment_request where username='"+user+"' and property_id='"+p_id+"' order by request_date desc"
            flg,result=self.reader.execute_query(self.for_result,cursor,sql)
            if flg:
                if len(result)>0:
                    if result[0][0] is not None:
                        flag=True
                else:
                    flag=True
        except:
            flag=False
        return flag


    @csrf_exempt
    def payment_request(self,request):
        try:
            if '__auth_log' in request.session and request.session['__auth_log']==1:
                if request.method=="POST":
                    if 'id' in request.POST:
                        sql="insert into payment_request (username, property_id,request_date) values ('"+\
                            request.session['fuser']+"','"+request.POST['id']+"',(select current_date from dual))"
                        if self.db_flag:
                            cursor=self.db_instance.cursor()
                            fl=self.check_request(cursor,request.session['fuser'],request.POST['id'])
                            
                            if fl:
                                flag,result=self.reader.execute_query(self.empty_result,cursor,sql)
                                if flag:
                                    data = {'type': 1, 'resp': "Your payment request is completed."}
                                else:
                                    data = {'type': 0, 'resp': "Sorry, payment request is not completed."}
                            else:
                                data = {'type': 0, 'resp': "Sorry, you already sent payment request to client."}
                        else:
                            data = {'type': 0, 'resp': "Sorry, record updation error found."}
                    else:
                        data = {'type': 0, 'resp': "Sorry, property field is missing."}
                else:
                    data = {'type': 0, 'resp': "Sorry, something is goning wrong due to accessing wrong."}
            else:
                data = {'type': 0, 'resp': "Sorry, Please login to procceed request."}

        except Exception, e:
            data = {'type': 0, 'resp': "Sorry, something is goning wrong due to " + str(e)}
        return JsonResponse(data)

    @csrf_exempt
    def accept_payment_request(self, request):
        try:
            if '__auth_log' in request.session and request.session['__auth_log'] == 1:
                if request.method == "POST":
                    if 'id' in request.POST:
                        sql = "update payment_request set acception ='accepted' where property_id='"+request.POST['id']+"' and "\
                                "username=(select c.username from client c join payment_request pr on(pr.property_id"\
                                "='"+request.POST['id']+"' and pr.username=(select username from client where fullname="\
                                "'"+request.POST['name']+"') and c.username=pr.username)) "
                        
                        if self.db_flag:
                            cursor = self.db_instance.cursor()

                            flag, result = self.reader.execute_query(self.empty_result, cursor, sql)
                            
                            if flag:
                                
                                data = {'type': 1, 'resp': "Your payment request updation is completed."}
                            else:
                                data = {'type': 0, 'resp': "Sorry, payment request updation is not completed."}

                        else:
                            data = {'type': 0, 'resp': "Sorry, record updation error found."}
                    else:
                        data = {'type': 0, 'resp': "Sorry, property field is missing."}
                else:
                    data = {'type': 0, 'resp': "Sorry, something is goning wrong due to accessing wrong."}
            else:
                data = {'type': 0, 'resp': "Sorry, Please login to procceed request."}

        except Exception, e:
            data = {'type': 0, 'resp': "Sorry, something is goning wrong due to " + str(e)}
        return JsonResponse(data)

    @csrf_exempt
    def del_payment_request(self, request):
        try:
            if '__auth_log' in request.session and request.session['__auth_log'] == 1:
                if request.method == "POST":
                    if 'id' in request.POST:
                        sql = "update payment_request set acception ='rejected' where property_id='"+request.POST['id']+"' " \
                                "and username=(select c.username from client c join payment_request pr on(pr.property_id='"+request.POST['id']+"' " \
                                "and pr.username=(select username from client where fullname='"+request.POST['name']+"') and c.username=pr.username)) "

                        if self.db_flag:
                            cursor = self.db_instance.cursor()

                            flag, result = self.reader.execute_query(self.empty_result, cursor, sql)
                            if flag:
                                data = {'type': 1, 'resp': "Your payment request rejection is completed."}
                            else:
                                data = {'type': 0, 'resp': "Sorry, payment request rejection is not completed."}
                        else:
                            data = {'type': 0, 'resp': "Sorry, record updation error found."}
                    else:
                        data = {'type': 0, 'resp': "Sorry, property field is missing."}
                else:
                    data = {'type': 0, 'resp': "Sorry, something is goning wrong due to accessing wrong."}
            else:
                data = {'type': 0, 'resp': "Sorry, Please login to procceed request."}

        except Exception, e:
            data = {'type': 0, 'resp': "Sorry, something is goning wrong due to " + str(e)}
        return JsonResponse(data)


    def payment_method(self,request):
        error=""
        try:
            if '__auth_log' in request.session and request.session['__auth_log'] == 1:
                return render(request, "payment.html", {'logvalue': request.session['__auth_log'],
                                                'fname': request.session['fname'],
                                                'status': request.session['status']})
            else:
                error="Please login before use this page"
        except Exception,e:
            error="Some features are not working well. Please try again"
        return render(request, "payment.html", {'logvalue': 0,'fname': "",'status': -1,"error":error})


    def check_payinfo(self,cursor,user):
        flag=False
        try:
            sql="select * from payment_info where username='"+user+"'"
            flg,result=self.reader.execute_query(self.for_result,cursor,sql)
            if flg:
                if len(result)==0:
                    flag=True
        except Exception,e:
            flag=False
        return flag




    @csrf_exempt
    def send_payment_info(self,request):
        try:
            if '__auth_log' in request.session and request.session['__auth_log'] == 1:
                if request.method == "POST":
                    if 'branch' in request.POST:
                        if 'account' in request.POST:
                            if 'pin' in request.POST:
                                sql = "insert into payment_info (username,pin_code,branch,account_no) values ('"+request.session['fuser']+"',"+request.POST['pin']+"," \
                                                    "'"+request.POST['branch']+"','"+request.POST['account']+"')"
                                
                                if self.db_flag:
                                    cursor = self.db_instance.cursor()
                                    f=self.check_payinfo(cursor,request.session['fuser'])
                                    if f:
                                        flag, result = self.reader.execute_query(self.empty_result, cursor, sql)
                                        if flag:
                                            data = {'type': 1, 'resp': "Your payment information is saved successfully."}
                                        else:
                                            data = {'type': 0, 'resp': "Your payment information is not saved successfully."}
                                    else:
                                        data = {'type': 1,
                                                'resp': "Your payment information already saved."}
                                else:
                                    data = {'type': 0, 'resp': "Sorry, connection error found to storage."}
                            else:
                                data = {'type': 0, 'resp': "Sorry, account pin field is missing."}
                        else:
                            data = {'type': 0, 'resp': "Sorry, account number field is missing."}
                    else:
                        data = {'type': 0, 'resp': "Sorry, branch field is missing."}
                else:
                    data = {'type': 0, 'resp': "Sorry, something is goning wrong due to accessing wrong."}
            else:
                data = {'type': 0, 'resp': "Sorry, Please login to procceed request."}

        except Exception, e:
            data = {'type': 0, 'resp': "Sorry, something is goning wrong due to " + str(e)}
        return JsonResponse(data)

    @csrf_exempt
    def get_profile(self,request):
        try:
            if '__auth_log' in request.session and request.session['__auth_log'] == 1:
                if request.method == "POST":
                    if 'id' in request.POST:
                        if 'name' in request.POST:
                            sql = "select fullname,address,email,phone from client where username " \
                                  "in (select username from payment_request where property_id='"+request.POST['id']+"') and fullname='"+request.POST['name']+"'"
                            if self.db_flag:
                                cursor = self.db_instance.cursor()
                                flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                                if flag:
                                    if len(result)>0:
                                        resp={}
                                        resp.setdefault("name",result[0][0])
                                        resp.setdefault("address", result[0][1])
                                        resp.setdefault("email", result[0][2])
                                        resp.setdefault("phone", result[0][3])
                                        data = {'type': 1, 'resp': resp}
                                    else:
                                        data = {'type': 0,
                                                'resp': "Sorry, no record found."}
                                else:
                                    data = {'type': 0, 'resp': "Sorry, operational error found."}
                            else:
                                data = {'type': 0, 'resp': "Sorry, connection error found to storage."}
                        else:
                            data = {'type': 0, 'resp': "Sorry, account number field is missing."}
                    else:
                        data = {'type': 0, 'resp': "Sorry, branch field is missing."}
                else:
                    data = {'type': 0, 'resp': "Sorry, something is goning wrong due to accessing wrong."}
            else:
                data = {'type': 0, 'resp': "Sorry, Please login to procceed request."}

        except Exception, e:
            data = {'type': 0, 'resp': "Sorry, something is goning wrong due to " + str(e)}
        return JsonResponse(data)



    
    def getInfo(self,cursor,p_id):
        flag=False
        bal,user='',''
        try:
            sql="select price,username from property where property_id='"+p_id+"'"
            flag, result = self.reader.execute_query(self.for_result, cursor, sql)
            if flag:
                if len(result)>0:
                    bal=result[0][0]
                    user=result[0][1]
                    flag=True
        except:
            flag=False
        return flag,bal,user

    def checkBalance(self,cursor,user,p_id):
        flag=False
        remain=''
        try:
            sql="select pi.balance-p.price from property p join payment_info pi on(pi.balance>=p.price and p.property_id='"+p_id+"' and pi.username='"+user+"')"
            flag, result = self.reader.execute_query(self.for_result, cursor, sql)
            if flag:
                if len(result)>0:
                    remain=result[0][0]
                    flag=True
        except:
            flag=False
        return flag,remain

    
    @csrf_exempt
    def transfer_property(self,request):
        try:
            if '__auth_log' in request.session and request.session['__auth_log'] == 1:
                if request.method == "POST":
                    if 'id' in request.POST:
                        if 'name' in request.POST:
                            if self.db_flag:
                                cursor = self.db_instance.cursor()
                                
                                client_user=request.session['fuser']
                                flag,remain=self.checkBalance(cursor,client_user,request.POST['id'])
                                fl,bal,user_owner=self.getInfo(cursor,request.POST['id'])
                                if flag:
                                    if fl:
                                        sql_list=[]
                                        sql_list.append("update payment_info set balance=balance+"+str(bal)+" where username='"+user_owner+"'")
                                        sql_list.append("update payment_info set balance="+str(remain)+" where username='"+client_user+"'")
                                        sql_list.append("update property set status=1 where property_id='"+request.POST['id']+"'")
                                        sql_list.append("insert into TRANSACTION_PROPERTY (username,property_id,t_date) values "+\
                                                            "('"+client_user+"','"+request.POST['id']+"',(select current_date from dual))")
                                        err=False
                                        for each_query in sql_list:
                                            
                                            flag, result = self.reader.execute_query(self.empty_result, cursor, each_query)
                                            if flag==False:
                                                err=True
                                                self.db_instance.rollback()
                                                break
                                            
                                        if err:
                                            data = {'type': 0, 'resp': 'Congrates, your property transaction is not completed yet.'}

                                        else:    
                                            data = {'type': 1, 'resp': 'Congrates, your property transaction is completed.'}
                                    else:
                                        data = {'type': 0,
                                                'resp': "Sorry, property's owner info is not found."}
                                else:
                                    data = {'type': 0,
                                                'resp': "Sorry, you have insufficient balance."}
                            else:
                                data = {'type': 0, 'resp': "Sorry, connection error found to storage."}
                        else:
                            data = {'type': 0, 'resp': "Sorry, account number field is missing."}
                    else:
                        data = {'type': 0, 'resp': "Sorry, branch field is missing."}
                else:
                    data = {'type': 0, 'resp': "Sorry, something is goning wrong due to accessing wrong."}
            else:
                data = {'type': 0, 'resp': "Sorry, Please login to procceed request."}

        except Exception, e:
            data = {'type': 0, 'resp': "Sorry, something is goning wrong due to " + str(e)}
        return JsonResponse(data)
