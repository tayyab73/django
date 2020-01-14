from django.shortcuts import render
from django.http import request,JsonResponse
from dbconfig import DataBase
from random import randint
from reader import Reader
from mail_ftn import MailService
from django.views.decorators.csrf import csrf_exempt
from reader import Reader
import urllib,urllib2
from sms import SMS
from settings import MEDIA_URL



class Property_Search:
    def __init__(self,flag,instance):
        self.db_flag=flag
        self.db_instance=instance
        self.for_result=True
        self.empty_result=False

        self.reader=Reader()
        self.mail=MailService()
        self.sms=SMS()


    def addFriend(self,user,client):
        check=False
        try:
            if user==client:
                check= True
            else:
                sql="insert into client_friend (username,client) values ('"+user+"','"+client+"')"
                if self.db_flag:
                    cursor=self.db_instance.cursor()
                    flag,result=self.reader.execute_query(self.empty_result, cursor,sql)
                    if flag:
                        check=True
                        self.db_instance.commit()
        except:
            check= False
        return check

################################################################################################################################################################################
#######################################################################Helping Methods for Detail' page###################################################################################
###################################################################################################################################################################################



    def getRating(self,p_id):
        rate=''
        sql = "select avg(rating) from property_rating where property_id='"+p_id+"'"
        try:

            if self.db_flag:
                cursor = self.db_instance.cursor()
                flag,result=self.reader.execute_query(self.for_result,cursor,sql)
                if flag:
                    if len(result) == 0:
                        rate="No rating about this property not found."
                    else:
                        for row in result:
                            rate= row[0]
                else:
                    rate="Searching error in database"
            else:
                rate="Database connection error"
        except Exception, e:
            rate="Error due to "+str(e)
        return rate

    def getlatestFeedback(self,p_id):
        lst,flg=[],0
        sql="select f.feedback,f.feedback_date,c.fullname from property_feedback f join"\
            " client c on(f.property_id='"+p_id+"' and c.username=f.username) order by f.feedback_date desc"

        try:

            if self.db_flag:
                cursor = self.db_instance.cursor()
                flag,result=self.reader.execute_query(self.for_result,cursor,sql)
                if flag:
                    if len(result) == 0:
                        lst.append("No feeback about this property not found.")
                    else:
                        for row in result:
                            di={}
                            di.setdefault("user",row[2])
                            di.setdefault("feed", row[0])
                            di.setdefault("date", row[1])
                            lst.append(di)
                        flg=1
        except Exception,e:
            lst=[]
        return lst,flg

    def getLatest(self, cursor):
        latest = []
        try:
            sql = "select property_id,property_name, price from property order by property_date desc"
            flag, result = self.reader.execute_query(self.for_result, cursor, sql)
            if flag:
                counter = 0
                if len(result) > 0:
                    for _ in result:
                        if counter < 5:
                            d = {}
                            d.setdefault("id", _[0])
                            d.setdefault("name", _[1])
                            d.setdefault("price", self.reader.addComma(_[2]))

                            sql = "select path from property_media where property_id='" + _[0] + "' and type in ('jpg','jpeg','png','bmp','gif')"
                            flag, sub_result = self.reader.execute_query(self.for_result, cursor, sql)
                            if flag:
                                if len(sub_result) > 0:
                                    d.setdefault("img", _[0] + "/" + sub_result[0][0])
                                else:
                                    d.setdefault("img", "default.jpg")
                            else:
                                break

                            latest.append(d)
                        else:
                            break
                        counter += 1
        except:
            latest=[]
        return latest


###############################################################################################################################################################################
################################################################Property Detail functions##################################################################################################
################################################################################################################################################################################

    def send_error(self,request, found, error, result_dict, latest, flg, feedback, rating,media,video):
        check = False
        if '__auth_log' in request.session and request.session['__auth_log'] == 1:
            check = True

        if check:

            return render(request, 'detail.html',
                              {'error': error, 'logvalue': request.session['__auth_log'],
                               'fname': request.session['fname'], 'status': request.session['status'],
                               'username': result_dict['p_fullname'], 'property_name': result_dict['p_name'],
                               'address': result_dict['p_address'], 'city': result_dict['p_city'],
                               'desc': result_dict['p_desc'],
                               'price': result_dict['p_price'],'phone': result_dict['p_phone'],'result':found,'latest':latest,
                                'bed':result_dict['p_bed'],'living':result_dict['p_living'],'park':result_dict['p_park'],
                               'kitchen':result_dict['p_kitchen'],
                               'flag':flg,'feedback':feedback,'rang':rating,'media':media,'video':video
                               ,"MEDIA_URL":MEDIA_URL,'p_category':result_dict['p_category'],'stat':result_dict['p_status']})

        return render(request, 'detail.html',
                          {'error': error, 'logvalue': 0,
                           'fname': 'guest', 'status': -1,
                            'username': result_dict['p_fullname'], 'property_name': result_dict['p_name'],
                               'address': result_dict['p_address'], 'city': result_dict['p_city'],
                               'desc': result_dict['p_desc'],
                               'price': result_dict['p_price'],'phone': result_dict['p_phone'],'result':found,'latest':latest,
                                'bed':result_dict['p_bed'],'living':result_dict['p_living'],'park':result_dict['p_park'],
                               'kitchen':result_dict['p_kitchen'],
                               'flag':flg,'feedback':feedback,'rang':rating,'media':media,'video':video
                               ,"MEDIA_URL":MEDIA_URL,'p_category':result_dict['p_category'],'stat':result_dict['p_status']})


    def getMediaFiles(self,cursor,p_id):
        img_list,video_path=[],"trial.mp4"
        sql = "select property_id,path from property_media where property_id ='" + p_id + "' and type in ('jpg','png','jpeg','gif','bmp')"
        flag, result = self.reader.execute_query(self.for_result, cursor, sql)
        if flag:
            if len(result) > 0:

                for row in result:
                    img_list.append(row[0] + '/' + row[1])
            else:
                img_list.append('default.jpg')
        else:
            error = "Sorry, searching error into database."
        sql = "select property_id,path from property_media where property_id= '" + p_id + "'and type in ('mp4','3gp','avi','mkv')"
        flag, result = self.reader.execute_query(self.for_result, cursor, sql)
        if flag:

            if len(result) > 0:
                for row in result:
                    video_path = row[0] + '/' + row[1]
        else:
            error = "Sorry, searching error into database."

        if len(img_list)==0:
            img_list.append("default.jpg")
        return img_list,video_path


    def detail(self, request):
        result_dict = {}
        latest=[]
        media=[]
        video="trial.mp4"
        found, error = 0, ''
        try:
            if request.method == 'GET':
                sql="select p.property_name,p.address,p.city,p.description,p.price,d.bed,d.living," \
                          "d.park,d.kitchen,c.fullname,c.phone,p.category,p.status from property p join property_detail d on" \
                    " (p.property_id='"+request.GET['id']+"' and p.property_id=d.property_id) join client c " \
                                                          "on(c.username=(select username from property where property_id='"+request.GET['id']+"'))"

                if self.db_flag:
                    feedback,flg=self.getlatestFeedback(request.GET['id'])
                    rating=self.getRating(request.GET['id'])

                    cursor = self.db_instance.cursor()
                    flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                    latest = self.getLatest(cursor)
                    if flag:
                        if len(result) != 0:
                            for row in result:
                                result_dict.setdefault("p_name",row[0])
                                result_dict.setdefault("p_address", row[1])
                                result_dict.setdefault("p_city", row[2])
                                result_dict.setdefault("p_desc",row[3])
                                result_dict.setdefault("p_price", self.reader.addComma(row[4]))
                                result_dict.setdefault("p_bed", row[5])
                                result_dict.setdefault("p_living", row[6])
                                result_dict.setdefault("p_park", row[7])
                                result_dict.setdefault("p_kitchen", row[8])
                                result_dict.setdefault("p_fullname", row[9])
                                result_dict.setdefault("p_phone", row[10])
                                result_dict.setdefault("p_category", row[11])
                                result_dict.setdefault("p_status", row[12])
                            media,video=self.getMediaFiles(cursor,request.GET['id'])


                            found=1
                        else:
                            error='No require data found according to that property id'
                    else:
                        error = "Sorry, searching error into database for specific property detail."
                else:
                    error='Error due to database connection'
            else:
                error='Cannot use this page directly.'
        except Exception, e:
            error="Error due to "+str(e)

        return self.send_error(request, found, error, result_dict, latest, flg, feedback, rating,media,video)


############################################################################################################################################################################
###########################################################################End of Detail 's Page##############################################################################
#############################################################################Query Search Method############################################################################
##########################################################################################################################################################################



    def property_search(self, request):
        latest,bigdata = [],[]
        error,bit="",0
        bed,park=False,False
        numb=self.reader.getData("Numbering")
        try:
            sql = "select property_id,property_name,price,status from property"
            if request.method=='GET':

                if 'req' in request.GET:
                    if request.GET['req']=='Rent' or request.GET['req']=='rent':
                        sql+=" where category='Rent'"
                    elif request.GET['req']=='Sale' or request.GET['req']=='sale' or request.GET['req']=='Buy' or request.GET['req']=='buy':
                        sql+=" where category='Sale'"
                    elif str(request.GET['req'])!='all':
                        print request.GET['req']
                        return self.send_error_msg(request, 'buysalerent', 'missing argument to procceed.', 0, [],
                                                   latest,numb)
            elif request.method == 'POST':
                sql = "select property_id,property_name,price,status from property"
                property_flag, cat, price, tp = False, False, False, False
                bed,park=False,False
                sql2="select property_id from property_detail where"

                if request.POST['property_name'] != '':
                    sql += " where (property_name like '%" + str(
                        request.POST['property_name']).lower() + \
                      "%' or address like '%" + str(request.POST['property_name']).lower() + "%' or city like '%" + \
                      str(request.POST['property_name']).lower() + "%' or description like '%"+request.POST['property_name']+"%' " \
                                            "or area like '%"+request.POST['property_name']+"%')"

                    property_flag = True
                if request.POST['category'] != 'Category':
                    if property_flag:
                        sql += " and category='" + request.POST['category']+ "'"
                    else:
                        sql += " where category='" + request.POST['category'] + "'"
                    cat = True

                if request.POST['price'] != 'Price':
                    operation = "<="
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
                            no=int(str(request.POST['price'][0]))
                            price*=no

                        elif 'Crore' in request.POST['price']:
                            price=10000000
                            no=int(str(request.POST['price'][0]))
                            price*=no

                        else:
                            price=request.POST['price']
                            operation="<="


                    except Exception,e:
                        return self.send_error_msg(request,'buysalerent','Error due to '+str(e),0,[])

                    if property_flag or cat:
                        sql += " and price"+operation +str(price)
                    else:
                        sql += " where price"+operation + str(price)

                    price = True

                if request.POST['type'] != 'Property':
                    if price or property_flag or cat:
                        sql += " and type='" + request.POST['type'] + "'"
                    else:
                        sql += " where type='" + request.POST['type'] + "'"
                    tp = True
                if 'bed' in request.POST and request.POST['bed']!="Bed Rooms":
                    sql2+=" bed="+request.POST['bed']
                    bed=True
                if 'parking' in request.POST and request.POST['parking']!="Parking Place":
                    if bed:
                        sql2+=" and"
                    sql2+=" park="+request.POST['parking']
                    park=True

                if property_flag==False and cat==False and price==False and tp==False:
                    sql="select property_id,property_name,price,status from property"

            sql += " order by price desc"



            if self.db_flag:
                cursor =self.db_instance.cursor()
                latest = self.getLatest(cursor)
                flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                #flag_sub,result_sub=self.reader.execute_query(self.for_result, cursor, sql2)


                sql_detail = "select bed,living,park,KITCHEN from property_detail where"
                if bed:
                    sql_detail+=" bed="+request.POST['bed']
                if park and 'bed=' in sql_detail:
                    sql_detail += " and park=" + request.POST['parking']
                elif park:
                    sql_detail += " park=" + request.POST['parking']
                if bed or park:
                    sql_detail+=" and"

                if flag:
                    if len(result) != 0:
                        bigdata = []

                        for row in result:
                            data_ = {}
                            sql = sql_detail+" property_id='" + row[0] + "'"
                            flag, sub_result = self.reader.execute_query(self.for_result, cursor, sql)

                            if flag:
                                if len(sub_result)>0:
                                    data_.setdefault("bed", sub_result[0][0])
                                    data_.setdefault("living", sub_result[0][1])
                                    data_.setdefault("park", sub_result[0][2])
                                    data_.setdefault("kitchen", sub_result[0][3])

                                    data_.setdefault('name', row[1])
                                    data_.setdefault('price', self.reader.addComma(row[2]))
                                    data_.setdefault('id', row[0])
                                    data_.setdefault('status', row[3])

                                    sql = "select path from property_media where property_id='" + row[
                                        0] + "' and type in ('jpg','jpeg','png','bmp','gif')"
                                    flag, sub_result = self.reader.execute_query(self.for_result, cursor, sql)
                                    if flag:
                                        p_id = row[0]
                                        if len(sub_result) > 0:
                                            data_.setdefault("img", p_id + "/" + sub_result[0][0])
                                        else:
                                            data_.setdefault("img", "default.jpg")
                                    else:
                                        error = "Error found during while searching."
                                        break

                            else:
                                error = "Error found during while searching."
                                break
                            if len(data_)>0:
                                bigdata.append(data_)
                        bit=1
                    else:
                        error='Records are not found according to your requirements.'
                else:
                    error="Error found during searching."
            else:
                error='DB connection is not made successfully'

        except Exception, e:
            error="Something is going wrong due to "+str(e)
        return self.send_error_msg(request,'buysalerent',error,bit,bigdata,latest,numb)



    def send_error_msg(self,request,page,msg,result,lst,latest,numb):
        check = False
        price = self.reader.getPrice()
        if '__auth_log' in request.session:
            if request.session['__auth_log'] == 1:
                check = True
        if check:
            return render(request, page+'.html', {'result': result, 'bigdata': lst, 'error': msg,
                                                        'logvalue': request.session['__auth_log'],
                                                        'fname': request.session['fname'], 'status':
                                                        request.session['status'],'latest':latest,'price':price,'numbers':numb})
        return render(request, page+'.html', {'result': result, 'bigdata': lst, 'error': msg,
                                                    'logvalue': 0,
                                                    'fname': 'guest', 'status':
                                                        -1,'latest':latest,'price':price,'numbers':numb
                                                    })


#####################################################################################################################################################################################
###########################################################################Endding of Searching property################################################################################
#############################################################################Starting of Property relateed function#############################################################################
################################################################################################################################################################################



    def check_alert(self,cursor,user,property,type):
        ch=False
        try:
            sql="select * from property_alert where username='"+user+"' and property_id='"+property+"' and type='"+type+"' and send_date=(select current_date from dual)"
            flag,result=self.reader.execute_query(self.for_result,cursor,sql)
            if flag:
                if len(result)==0:
                    ch=True
        except Exception,e:
            ch=False
        return ch


    def insert_alert(self,db,user,property_id,type):
        try:
            sql="insert into property_alert (username,property_id,type,send_date) values ('"+user\
                +"','"+property_id+"','"+type+"',(select current_date from dual))"
            cursor=db.cursor()
            try:
                flag, result = self.reader.execute_query(self.empty_result, cursor, sql)
                if flag:
                    db.commit()
                    data={'resp':type.upper()+' is sent successfully'}
                else:
                    data = {'resp': type.upper() + ' is not sent successfully'}
            except Exception ,e:
                data = {'resp': 'Error due to '+str(e)}
        except Exception,e:
            data = {'resp': ''}
        return data





    @csrf_exempt
    def send_email(self,request):
        try:
            if '__auth_log' in request.session:
                if request.session['__auth_log']==1:
                    if request.method=='POST':
                        if 'id' in request.POST:
                            if self.db_flag:
                                cursor=self.db_instance.cursor()
                                sql = "select c.email,p.property_name,c.username from client c join property p on " \
                                      "(p.property_id='"+request.POST['id']+"' and c.username=(select username from property where property_id='"+request.POST['id']+"'))"
                                flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                                if flag:
                                    if len(result)==1:
                                        email=result[0][0]
                                        if email!=None and len(email)>0:

                                            sql = "select fullname,email from client where username='"+request.session['fuser']+"'"

                                            flag, sub_result = self.reader.execute_query(self.for_result, cursor, sql)
                                            if flag:

                                                if len(sub_result)>0:
                                                    context="<style>/* Shrink Wrap Layout Pattern CSS */@media only screen and (max-width: 599px) " \
                                                    "{td[class='hero'] img {  width: 100%; height: auto !important;}" \
	                                                " td[class='pattern'] td{  width: 100%;}}</style>" \
                                                    "<table cellpadding='0' cellspacing='0'><tr><td class='pattern' width='600'>" \
                                                    "<table cellpadding='0' cellspacing='0'><tr><td class='hero'>" \
                                                    "<img style='width:600px;height:460px;' src='https://images.pexels.com/photos/106399/pexels-photo-106399.jpeg?cs=srgb&dl=architecture-family-house-front-yard-106399.jpg&fm=jpg' alt='' style='display: block; border: 0;' /></td></tr><tr>" \
                                                    "<td style='font-family: arial,sans-serif; color: #333;margin-left:200px;'><h1>BookIt</h1></td></tr>" \
                                                    "<tr><td align='left' style='font-family: arial,sans-serif; font-size: 14px; line-height: 20px !important;"\
                                                    " color: #666; padding-bottom: 20px;'>" \
                                                    "Alert Message from BookIt<br> "+sub_result[0][0]+":"+sub_result[0][1]+"	is interested to your property<br>"\
                                                            "Property Name:"+result[0][1]

                                                    context+= "</td></tr><tr>" \
                                                    "<td align='left'><a href='192.168.137.1:8000/property-detail?id="+request.POST['id']+"'><img src='http://placehold.it/200x50/333&text=Check+it' alt='Click here' style='display: block; border: 0;' /></a>" \
                                                    "</td></tr></table></td></tr></table>"
                                                    context= str(context.encode('ascii','ignore'))
                                                    try:
                                                        t_flag=self.mail.sent_mail_client(email,'',unicode(context))
                                                        if t_flag:
                                                            sql="insert into property_alert (username,property_id,type,send_date) values" \
                                                            " ('"+request.session['fuser']+"','"+request.POST['id']+"','email',(select current_date from dual))"
                                                            flag,t_result=self.reader.execute_query(self.empty_result,cursor,sql)
                                                            if flag:
                                                                self.db_instance.commit()

                                                                self.addFriend(request.session['fuser'],result[0][2])
                                                                self.addFriend( result[0][2],request.session['fuser'])
                                                                data = {'resp': 'Email is successfully sent!'}
                                                            else:
                                                                data = {'resp': 'Error while saving information.'}
                                                        else:
                                                            data = {'resp': 'Email is not sent successfully.'}
                                                    except:
                                                        data = {'resp': 'Error, while sending email to client.'}
                                                else:
                                                    data = {'resp': 'Invalid user request for sending email'}
                                            else:
                                                data = {'resp': 'Error while searching into database.'}
                                        else:
                                            data = {'resp': 'Email is not valid for processing.'}
                                    else:
                                        data = {'resp': 'Error, email address is not found for client.'}
                                else:
                                    data = {'resp': 'Error while searching into database.'}
                            else:
                                data = {'resp': 'Error, while connecting to database for infomation parsing.'}
                        else:
                            data = {'resp': 'Error, while not found argument.'}
                    else:
                        data = {'resp': 'Error, while accessing directly'}
                else:
                    data = {'resp': 'Error, while user client is invalid for logging'}
            else:
                data = {'resp': 'Error, while not found session of user.'}
        except Exception,e:
            data={'resp':'Error due to '+str(e)}
        return JsonResponse(data)


    @csrf_exempt
    def send_mobile(self, request):

        try:
            if '__auth_log' in request.session:
                if request.session['__auth_log']==1:
                    if request.method == 'POST':
                        if 'id' in request.POST:

                            if self.db_flag:
                                cursor = self.db_instance.cursor()
                                sql =  "select c.phone,p.property_name,c.username from client c join property p on " \
                                      "(p.property_id='"+request.POST['id']+"' and c.username=(select username from property where property_id='"+request.POST['id']+"'))"
                                flag,result=self.reader.execute_query(self.for_result,cursor,sql)
                                if flag:
                                    if len(result) == 1:
                                        phone = result[0][0]
                                        if phone != None and len(phone) > 0:
                                            if '+' in phone:
                                                phone=phone[1:]
                                            if '00'==phone[0:2]:
                                                phone=phone[2:]
                                            sql = "select fullname,phone from client where username='" + request.session['fuser'] + "'"
                                            flag, sub_result = self.reader.execute_query(self.for_result, cursor, sql)
                                            if flag:
                                                if len(sub_result) == 1:
                                                    if self.sms.send(sub_result[0][0],sub_result[0][1],phone,result[0][1]):
                                                        sql = "insert into property_alert (username,property_id,type,send_date) values" \
                                                        " ('" + request.session['fuser'] + "','" + request.POST[
                                                        'id'] + "','sms',(select current_date from dual))"
                                                        flag, result = self.reader.execute_query(self.empty_result, cursor, sql)
                                                        if flag:
                                                            self.db_instance.commit()

                                                            self.addFriend(request.session['fuser'], result[0][2])
                                                            self.addFriend(result[0][2],request.session['fuser'])
                                                            data = {'resp': 'SMS is successfully sent!'}
                                                        else:
                                                            data = {'resp': 'Sorry, sms updation error found.'}
                                                    else:
                                                        data = {'resp': 'SMS is not successfully sent yet!'}
                                                else:
                                                    data = {'resp': 'Sorry, your information is recoginze!'}
                                            else:
                                                data = {'resp': "Sorry, database searching error found."}
                                        else:
                                            data = {'resp': 'Sorry, client phone number is not recognize!'}
                                    else:
                                        data = {'resp': 'Sorry, database searching result not found.'}
                                else:
                                    data = {'resp': 'Sorry, database searching error found..'}
                            else:
                                data = {'resp': 'Error, during database connection...'}
                        else:
                            data={'resp':'Error, while not found argument.'}
                    else:
                        data = {'resp': 'Failed while sending data to server.'}
                else:
                    data = {'resp': 'Failed while not found user infomation of logging.'}
            else:
                data = {'resp': 'Failed while access of session, which might be expire.'}
        except Exception, e:
            data = {'resp': 'Error due to ' + str(e)}

        return JsonResponse(data)





###############################################################################################################################################################################
###########################################################################Property Feedback option###############################################################################
################################################################################################################################################################################


    def check_feedback(self,cursor,typ,property_id,user):
        ch=False
        try:
            sql="select * from property_feedback where username='"+user+"' and property_id='"+property_id+"' " \
                                                "and to_char("+typ+"_date,'d-mm-yyyy')=to_char((select current_date from dual),'d-mm-yyyy')"

            flag, result = self.reader.execute_query(self.for_result, cursor, sql)
            if flag:
                if len(result)==0:
                    ch=True

        except Exception,e:
            ch=False
        return ch


    def insert_feedback(self,db,typ,msg,property_id,user):
        try:
            sql = "insert into property_"+typ+" (property_id,username,"+typ+"_date,"+typ+") values ('" + property_id + \
                  "','" + user + "',(select current_date from dual),'" +msg + "')"
            try:
                cursor=db.cursor()
                flag, result = self.reader.execute_query(self.empty_result, cursor, sql)
                if flag:
                    db.commit()
                    data = {'resp': "Your preciesly "+typ+" about property submitted"}
                else:
                    data={'resp':'Sorry, '+typ+' is not submitted yet.'}
            except Exception, e:
                data = {'resp': 'Error due to ' + str(e)}
        except Exception,e:
            data = {'resp': 'Error due to '+str(e)}
        return data


    @csrf_exempt
    def feedback(self,request):
        try:
            if '__auth_log' in request.session:
                if request.method=='POST':


                    if 'rating' in request.POST:

                        if self.db_flag:
                            cursor=self.db_instance.cursor()
                            if self.check_feedback(cursor,'rating',request.POST['property_id'],request.session['fuser']):
                                self.addFriend(request.session['fuser'], result[0][2])
                                self.addFriend(result[0][2], request.session['fuser'])
                                data=self.insert_feedback(self.db_instance,'rating',request.POST['rating'],request.POST['property_id'],request.session['fuser'])
                            else:
                                data = {'resp': 'Sorry, one request perform per day.'}
                        else:
                            data = {'resp': 'Error while connecting to database.'}

                    elif 'feedback' in request.POST:
                        if self.db_flag:
                            cursor = self.db_instance.cursor()
                            if self.check_feedback(cursor,'feedback', request.POST['property_id'],request.session['fuser']):
                                data = self.insert_feedback(self.db_instance, 'feedback',request.POST['feedback'], request.POST['property_id'],request.session['fuser'])
                            else:
                                data = {'resp': 'Sorry, one request perform per day.'}
                        else:
                            data = {'resp': 'Error while connecting to database.'}
                    else:
                        data = {'resp': 'Error while not desire request found.'}
                else:
                    data={'resp':'Error while sending data to server.'}
            else:
                data = {'resp': 'Error while directly accessing.'}
        except Exception,e:
            data = {'resp': 'Error due to '+str(e)}
        return JsonResponse(data)



#####################################################################################################################################################################################
##############################################################################Property Saving Option#######################################################################################
#################################################################################################################################################################################



    def check_property_save(self,cursor,user,p_id):
        ch=False
        try:
            sql="select * from property_saving where username='"+user+"' and property_id='"+p_id+"'"
            flag, result = self.reader.execute_query(self.for_result, cursor, sql)
            if flag:
                if len(result)==0:
                    ch=True
        except Exception,e:
            ch=False
        return ch




    def property_save(self,request):
        try:
            if '__auth_log' in request.session:
                if request.method=='POST':
                    if self.db_flag:
                        cursor=self.db_instance.cursor()
                        sql="insert into property_saving (property_id,username) values ('"+request.POST['property_id']+"','"+request.session['fuser']+"')"
                        if self.check_property_save(cursor,request.session['fuser'],request.POST['property_id']):
                            try:
                                flag, result = self.reader.execute_query(self.empty_result, cursor, sql)
                                if flag:
                                    self.db_instance.commit()
                                    data={'resp':'Selected property saved successfully.'}
                                else:
                                    data = {'resp': 'Selected property was not saved successfully.'}
                            except Exception,e:
                                data = {'resp': 'Error due to '+str(e)+'.'}
                        else:
                            data = {'resp': 'Sorry, you already save this property to your account'}
                    else:
                        data = {'resp': 'Error while database connectivity operation.'}
                else:
                    data = {'resp': 'Error while sending data to server.'}
            else:
                data = {'resp': 'Error while directly accessing.'}
        except Exception, e:
            data = {'resp': 'Error due to ' + str(e)}
        return JsonResponse(data)

###########################################################################################################################################################################
###########################################################Property rating option##########################################################################################
##########################################################################################################################################################################

    def checkrating(self,cursor,username,p_id):
        flag=False
        try:
            sql="select * from property_rating where username='"+username+"' and property_id='"+p_id+"'"
            flag, result = self.reader.execute_query(self.for_result, cursor, sql)
            if flag:
                if len(result)==0:
                    flag=True
        except:
            flag=False
        return flag

    def save_rating(self,request):
        try:
            if '__auth_log' in request.session:
                if request.session['__auth_log']==1:
                    if request.method=="POST":
                        if 'rating' in request.POST:
                            if 'p_id' in request.POST:

                                if self.db_flag:
                                    cursor=self.db_instance.cursor()
                                    if self.checkrating(cursor,request.session['fuser'],request.POST['p_id']):
                                        sql="insert into property_rating (username,property_id,rating,rating_date) values ('"+\
                                            request.session['fuser']+"','"+request.POST['p_id']+"',"+request.POST['rating']+",(select current_date from dual))"
                                        flag, result = self.reader.execute_query(self.empty_result, cursor, sql)
                                        if flag:
                                            self.db_instance.commit()
                                            data = {'resp': 'Your rating about property has been saved successfully.'}
                                        else:
                                            data = {'resp': 'Your rating about property has not been saved successfully.'}
                                    else:
                                        data = {'resp': 'Sorry, you already save this property to your account'}
                                else:
                                    data = {'resp': 'Error while database connectivity operation.'}
                            else:
                                data = {'resp': 'Error while due to missing property info.'}
                        else:
                            data = {'resp': 'Error while due to missing rating.'}
                    else:
                        data = {'resp': 'Error while directly accessing.'}
                else:
                    data = {'resp': 'Please login.'}
            else:
                data = {'resp': 'Please login first for rating.'}
        except Exception, e:
            data = {'resp': 'Error due to ' + str(e)}
        print data
        return JsonResponse(data)



###################################################################################################################################################################################
####################################################################################################################################################################################
##################################################################################################################################################################################

