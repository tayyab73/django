from django.shortcuts import render
from django.http import request,JsonResponse, request,HttpResponse
from django.views.decorators.csrf import csrf_exempt

from fyp.cronjob import CronJob
from mail_ftn import MailService
from reader import Reader
import uuid

from ipware.ip import get_real_ip

class Project:
   ##contructor of Project class
    def __init__(self,flag,db_instance):
        self.db_flag=flag
        self.db_instance=db_instance
        self.reader=Reader()
        self.for_result=True
        self.empty_result=False
        self.mailftn=MailService()
        self.cronjob=CronJob(flag,db_instance)

    def getFeature(self):
        lst = []
        result_flag=False
        try:
            sql = "select p.property_id,p.property_name,p.price,p.status,d.bed,d.living,d.kitchen,d.park" \
                  " from property p join property_detail d on(d.property_id=p.property_id and p.category='Rent' and p.status>-1) order by last_modified desc"


            if self.db_flag:
                cursor = self.db_instance.cursor()
                flag,results=self.reader.execute_query(self.for_result,cursor,sql)
                if flag:
                    if len(results) > 0:
                        count = 0
                        for row in results:
                            if count == 9:
                                break
                            dic = {}
                            dic.setdefault('id', row[0])
                            sql = "select path from property_media where property_id='" + row[0] + "' and type in ('jpg','jpeg','png','bmp','gif')"
                            img_flag,img_results =self.reader.execute_query(self.for_result,cursor,sql)
                            if img_flag:
                                if len(img_results) > 0:
                                    dic.setdefault("img", row[0] + "/" + img_results[0][0])
                                else:
                                    dic.setdefault("img", "default.jpg")
                            dic.setdefault('title', row[1])
                            dic.setdefault('price', self.reader.addComma(row[2]))
                            dic.setdefault('status', row[3])
                            dic.setdefault('bed', row[4])
                            dic.setdefault('living', row[5])
                            dic.setdefault('kitchen', row[6])
                            dic.setdefault('parking', row[7])

                            lst.append(dic)
                            count += 1
                        result_flag=True
        except Exception, e:
            lst=str(e)
        return result_flag, lst



    def getSliderData(self):
        lst = []
        result_flag=False
        try:
            sql="select property_id,property_name,address,city,description,price from property where category='Sale' and status>-1order by last_modified desc"

            if self.db_flag:
                cursor=self.db_instance.cursor()
                flag,results=self.reader.execute_query(self.for_result,cursor,sql)
                if flag:
                    if len(results)>0:

                        count=0
                        for row in results:
                            if count==5:
                                break
                            dic={}
                            dic.setdefault('id',row[0])
                            dic.setdefault('title', row[1])
                            dic.setdefault('address', row[2]+','+row[3])
                            dic.setdefault('desc', row[4][:110]+'...')
                            dic.setdefault('price', self.reader.addComma(row[5]))
                            lst.append(dic)
                            count+=1
                        result_flag=True

        except Exception,e:
            lst = str(e)
        return result_flag, lst





    #Home Page response
    def home(self,request):
        error,response_error="",{'logvalue':0,'fname':'guest' ,'status':-1}
        error_bit=0
        try:
            if self.logMonitor(request):
                flag_slider,resp=self.getSliderData()
                response_error.setdefault("slider",resp)

                if flag_slider:
                    flag_feature,feature=self.getFeature()
                    response_error.setdefault("feature", feature)
                    if flag_feature:
                        price=self.reader.getPrice()
                        response_error.setdefault("price", price)
                        if request.method=='POST':

                            if self.db_flag:
                                sql="select fullname,status from client where username='"+\
                                    request.POST['form_email']+"' and password='"+request.POST['form_password']+"' and status>-1"
                                db=self.db_instance.cursor()
                                flag,result=self.reader.execute_query(result_flag=self.for_result,cursor=db,query=sql)
                                if len(result)!=0:
                                    request.session['__auth_log']=1
                                    request.session['status']=result[0][1]
                                    request.session['fname']=result[0][0]
                                    request.session['fuser'] = request.POST['form_email']
                                    sql="update client_chat_status set status=1,last_date=(select current_date from dual) where username='"+request.session['fuser']+"'"
                                    flag,result=self.reader.execute_query(result_flag=self.empty_result,cursor=db,query=sql)
                                    if flag:
                                        self.db_instance.commit()
                                        return render(request, 'index.html', {'logvalue':request.session['__auth_log'],'fname':request.session['fname'] ,
                                                          'status':request.session['status'],'slider':resp,'feature':feature,'price':price})
                                    else:
                                        error="Sorry, your status updation processing is not completed."
                                else:
                                    error='Username or Password may be wrong'
                            else:
                                error="Sorry, your login request is not completed yet."

                            return render(request, 'login.html', {'error':error})

                        elif '__auth_log' in request.session and request.session['__auth_log']==1:
                            sql="select status from client where username='"+request.session['fuser']+"'"
                            if self.db_flag:
                                corsor=self.db_instance.cursor()
                                flag,result=self.reader.execute_query(self.for_result,corsor,sql)
                                request.session['status']=result[0][0]
                                return render(request, 'index.html',
                                        {'logvalue': request.session['__auth_log'], 'fname': request.session['fname'],
                                        'status': request.session['status'],'slider':resp,'feature':feature,'price':price})
                            else:
                                error_bit=1
                                error="Sorry, database options are not working well"


                    else:
                        error_bit=1
                        error = "Some features of property is not working yet, Please try again."
                else:
                    error_bit = 1
                    error = "Some slider feature of property is not working yet, Please try again."
            else:
                error_bit = 1
                error = "Some connection of storage is not working yet, Please try again."

        except Exception,e:
            error_bit = 1
            error="Some connection of storage is not working yet, Please try again."
        response_error.setdefault("error_bit", error_bit)
        response_error.setdefault("error",error)

        return render(request, 'index.html',response_error)



    def getprice(self,request):
        try:
            if request.method=='GET':
                reader=Reader()
                resp=reader.getData(request.GET['price'])
                data={'is_taken':resp}
            else:
                data = {'is_taken': 'Cannot be posted request for price to server'}
        except Exception,e:
            data = {'is_taken': 'Error due to '+str(e)}
        return JsonResponse(data)


    def public_page(self,request,page):
        error_bit=0
        error=""
        try:
            if self.db_flag == False:
                error_bit = 1
                error="Sorry, some database options are not working well"
            if '__auth_log' in request.session and request.session['__auth_log'] == 1:
                return render(request, page+'.html',
                              {'logvalue': request.session['__auth_log'], 'fname': request.session['fname'],
                               'status': request.session['status'],"error_bit":error_bit,"error":error})
        except Exception, e:
            error+="Sorry, Some exception occurs."
        return render(request, page+'.html', {'logvalue': 0, 'fname': 'guest', 'status': -1,"error_bit":error_bit,"error":error})



    def agents(self,request):
        return self.public_page(request,'agents')

    def contact(self,request):
        return self.public_page(request,'contact')


    def about(self, request):
        return self.public_page(request, 'about')

    def logout(self,request):
        try:
            result_flag=False
            error=""
            if self.db_flag:
                sql="update client_chat_status set status=0,last_date=(select current_date from dual) where username='"+request.session['fuser']+"'"
                cursor=self.db_instance.cursor()
                flag,results=self.reader.execute_query(self.empty_result,cursor,sql)
                if flag:
                    self.db_instance.commit()
                    for _ in request.session.keys():
                        del request.session[_]
                    result_flag=True

        except Exception,e:
            error+=str(e)
        flag_slider, resp = self.getSliderData()
        flag_feature, feature = self.getFeature()
        price = self.reader.getPrice()

        if result_flag:
            return render(request, 'index.html', {'logvalue': 0, 'fname': '', 'status': -1,"slider":resp,"feature":feature,"price":price})
        else:
            return render(request, 'index.html', {'logvalue': request.session['__auth_log'],
                                                  "slider": resp, "feature": feature, "price": price
                                                  ,'fname': request.session['fuser'], 'status':request.session['status'],'error':error})


    @csrf_exempt
    def contactRequest(self,request):
        try:
            if request.method=="POST":
                if 'name' in request.POST:
                    if 'email' in request.POST and '@' in request.POST['email']:
                        if 'phone' in request.POST:
                            if 'message' in request.POST:
                                sql="select * from contact where to_char(contact_date,'dd-MON-yyyy')=to_char((select current_date from dual),'dd-MON-yyyy')"\
                                    +" and name='"+request.POST['name']+"' and email='"+request.POST['email']+"' and phone='"+request.POST['phone']+"'"

                                if self.db_flag:
                                    cursor=self.db_instance.cursor()
                                    flag,results=self.reader.execute_query(self.for_result,cursor,sql)
                                    if flag:
                                        if len(results)==0:
                                            sql="insert into contact (name,email,phone,msg,contact_date) values ('"+\
                                            request.POST['name']+"','"+request.POST['email']+"','"+request.POST['phone']+\
                                            "','"+request.POST['message']+"',(select current_date from dual))"
                                            s_flag,s_results=self.reader.execute_query(self.empty_result,cursor,sql)
                                            if s_flag:
                                                self.db_instance.commit()
                                                self.cronjob.contactJob()
                                                data = {'type':1,'resp': 'Your request has been completed successfully.'}
                                            else:
                                                data = {'type': 1,
                                                        'resp': 'Sorry, your request has not been completed successfully.'}
                                        else:
                                            data = {'type': 1, 'resp': 'You already sent message. Please try again next day.'}
                                    else:
                                        data = {'type': 1, 'resp': 'Sorry, searching request has been completed successfully.'}
                                else:
                                    data = {'type': 0, 'resp': 'Database connection is not working due to services.'}
                            else:
                                data = {'type':0,'resp': 'Message field is missing.'}
                        else:
                            data = {'type':0,'resp': 'Mobile field is missing.'}
                    else:
                        data = {'type':0,'resp': 'Email field is missing.'}
                else:
                    data = {'type':0,'resp': 'Name field is missing.'}
            else:
                data = {'type':0,'resp': 'Error, while accessing through wrong method.'}
        except Exception,e:
            data={'type':0,'resp':'Error due to '+str(e)}
        return JsonResponse(data)


    @csrf_exempt
    def notify(self,request):
        try:
            if request.method == "POST":
                if 'email' in request.POST and '@' in request.POST['email']:
                    sql = "select * from subscribe where email='"+request.POST['email']+"'"

                    if self.db_flag:
                        cursor = self.db_instance.cursor()
                        flag,results=self.reader.execute_query(self.for_result,cursor,sql)
                        if flag:
                            if len(results) == 0:
                                sql = "insert into subscribe (email,s_date) values ('"+request.POST['email']+"',(select current_date from dual))"
                                sub_flag,sub_result=self.reader.execute_query(self.empty_result,cursor,sql)
                                if sub_flag:
                                    self.db_instance.commit()

                                    data = {'type': 1, 'resp': 'Your request has been completed successfully.'}
                                else:
                                    data = {'type': 1,
                                            'resp': 'Your request processing error.'}
                            else:
                                data = {'type': 1,
                                                'resp': 'Sorry, you already subsrcibed.'}
                        else:
                            data = {'type': 1,
                                    'resp': 'Sorry, you request has been not completed.'}
                    else:
                        data = {'type': 0, 'resp': 'Database connection is not working due to services.'}

                else:
                    data = {'type': 0, 'resp': 'Email field is missing.'}
            else:
                data = {'type': 0, 'resp': 'Error, while accessing through wrong method.'}
        except Exception, e:
            data = {'type': 0, 'resp': 'Error due to ' + str(e)}
        return JsonResponse(data)

##################################################################################################################################################################################
    def get_mac(self):
        mac_num = hex(uuid.getnode()).replace('0x', '').upper()
        mac = '-'.join(mac_num[i: i + 2] for i in range(0, 11, 2))
        return mac

    def demo(self,request,id_):
        return HttpResponse(id_)

    def logMonitor(self,request):
        check=False
        try:
            if self.db_flag:
                cursor=self.db_instance.cursor()
                sql="insert into log_record (v_date,mac_address,ip_address) values " \
                    "((select current_date from dual),'"+str(self.get_mac())+"','"+str(request.META.get('REMOTE_ADDR'))+"')"
                flag,results=self.reader.execute_query(self.empty_result,cursor,sql)
                if flag:
                    self.db_instance.commit()
                    check=True

        except Exception,e:
            check=False
        return check


