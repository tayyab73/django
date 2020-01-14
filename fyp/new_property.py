from django.shortcuts import render
from django.http import request,JsonResponse, request,HttpResponse
from dbconfig import DataBase
from random import randint

from fyp.cronjob import CronJob
from reader import Reader
import os
import shutil
import sys
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from reader import Reader
from threading import Thread

class New_Property:
    def __init__(self,flag,instance):
        self.reader=Reader()
        self.db_flag=flag
        self.db_instance=instance
        self.for_result=True
        self.empty_result=False
        self.crobjob=CronJob(flag,instance)





    def get_id(self):
        value="abcdefghijklmnopqrstuvxyz"
        value2="1234567890"
        flag_bit,gene_id=False,""
        try:
            for i in range(1,3):
                index=randint(0,len(value))
                gene_id+=value[index]
            for i in range(1,6):
                index=randint(0,len(value2))
                gene_id+=value2[index]

            sql="select * from property where property_id='"+gene_id+"'"

            if self.db_flag:
                cursor=self.db_instance.cursor()
                flag,result=self.reader.execute_query(self.for_result,cursor,sql)
                if flag:
                    if len(result)==0:
                        flag_bit=True
        except Exception,e:
            flag_bit=False
        return flag_bit,gene_id


    def newads(self, request):
        page_no,error='',''
        return self.operate_page(request,page_no,error)

    def middle_regisgration(self, request):
        page_no,error='',''
        try:
            if request.method == 'POST':
                if request.POST['p_name'] != '':
                    if request.POST['p_detail'] != '':
                        if request.POST['p_address'] != '':
                            if request.POST['p_city'] != 'City':
                                if request.POST['p_price'] != '':
                                    if request.POST['p_category'] != 'Category':
                                        if request.POST['p_type'] != 'Type':
                                            if request.POST['broom']!='Bed Rooms':
                                                if request.POST['lroom'] != 'Living Rooms':
                                                    if request.POST['parking'] != 'Parking':
                                                        if request.POST['kitchen']!='Kitchen':
                                                            if request.POST['p_area'] != '':
                                                                if request.POST['p_areacategory'] != 'Area':

                                                                    generated_id = ''
                                                                    while (True):
                                                                        flag,element = self.get_id()
                                                                        if flag:
                                                                            generated_id = element
                                                                            break
                                                                    sql = "insert into property (property_id,property_name,description,address,city,price," \
                                                                          "category,type,status,property_date,area,username)" + \
                                                                        "values ('" + generated_id + "','" + str(
                                                                        request.POST['p_name']).lower() + "','" + \
                                                                            str(request.POST['p_detail']).lower() + "','" + str(
                                                                                request.POST['p_address']).lower() + "','" + \
                                                                                request.POST['p_city'] + "'," + request.POST['p_price'] + \
                                                                                ",'" + request.POST['p_category'] + "','" + request.POST[
                                                                                'p_type'] + "',0,(select current_date from dual),'" + \
                                                                         request.POST['p_area'] \
                                                                         + " " + request.POST['p_areacategory'] + "','"+request.session['fuser']+"')"


                                                                    if self.db_flag:
                                                                        cursor = self.db_instance.cursor()
                                                                        try:
                                                                            flag,result=self.reader.execute_query(self.empty_result,cursor,query=sql)
                                                                            if flag:
                                                                                sql="insert into property_detail (property_id,bed,living,park,kitchen) values" \
                                                                                " ('"+generated_id+"',"+request.POST['broom']+","+\
                                                                                    request.POST['lroom']+","+request.POST['parking']+","+request.POST['kitchen']+")"
                                                                                flag, result = self.reader.execute_query(self.empty_result, cursor,sql)
                                                                                if flag:
                                                                                    self.db_instance.commit()
                                                                                    #self.reader.new_thread_for_subscribe(self.crobjob,generated_id)
                                                                                    page_no='2'
                                                                                else:
                                                                                    error = 'Sorry, error while processing information for storage.'
                                                                            else:
                                                                                error = 'Sorry, error while processing information for storage.'
                                                                        except Exception, e:
                                                                            error='Sorry, something is wrong during processing.'+str(e)
                                                                    else:
                                                                        error = 'Sorry, error while connecting to storage/database.'
                                                                else:
                                                                    error='Please select area category to procced further.'
                                                            else:
                                                                error='Please fill the area info.'
                                                        else:
                                                            error='Please select number of Kitchens.'
                                                    else:
                                                        error='Please select number of Parking.'
                                                else:
                                                    error = 'Please select number of Living Rooms.'
                                            else:
                                                error = 'Please select number of Bed Rooms.'
                                        else:
                                            error = 'Please select property type.'
                                    else:
                                        error = 'Please select property category like sale or rent.'
                                else:
                                    error = 'Please fill price about property.'
                            else:
                                error = 'Please select property\'s location city.'
                        else:
                            error = 'Please fill the property\'s location address.'
                    else:
                        error = 'Please fill description about property.'
                else:
                    error = 'Please fill some property name.'
            else:
                error = 'Cannot access directly this page, Please first go to login,<br> click on New ADS.'
        except Exception, e:
            error = 'Sorry, error due to something wrong working.'
        return self.operate_page(request,page_no,error)

    def newads2(self, request):
        page_no,error='2',''
        return self.operate_page(request, page_no,error)



    def operate_page(self,request,page_name,error):
        if page_name=='':
            page_name='new-ads'
        else:
            page_name='new-ads-2'
        numb=self.reader.getData('Numbering')
        try:
            if '__auth_log' in request.session:
                if request.session['__auth_log'] == 1:

                    return render(request, page_name+'.html', {'error': error, 'logvalue': request.session['__auth_log'],
                                                          'fname': request.session['fname'],
                                                          'status': request.session['status'],'number':numb})
                else:
                    return render(request, page_name+'.html',
                              {'error': 'Please login to access this page.', 'logvalue': 0, 'fname': 'guest',
                               'status': -1,'number':numb})
            else:
                return render(request, page_name+'.html',
                          {'error': 'Cannot access directly this page.', 'logvalue': 0, 'fname': 'guest', 'status': -1,'number':numb})
        except Exception, e:
            return render(request, page_name+'.html', {'error': 'Error due to ' + str(e), 'logvalue': 0,
                                                  'fname': 'guest', 'status': 0,'number':numb})


    def getPropertyID(self,request):
        p_id,flg='',False
        try:
            if '__auth_log' in request.session:
                if request.session['__auth_log']==1:
                    flg=True
                    sql="select property_id from property where username='"+request.session['fuser']+"' " \
                        "and to_char(property_date,'d-mm-yyyy')=to_char((select current_date from dual),'d-mm-yyyy')"

                    if self.db_flag:
                        cursor=self.db_instance.cursor()
                        flag,result=self.reader.execute_query(self.for_result,cursor,sql)

                        if len(result)!=0:
                            p_id=result[0][0]
                            flg=True
        except Exception,e:
            flg=False
        return flg,p_id


    def finalRegAd(self,request):
        page_no,error='2',''
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        error_flag = False
        image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp']
        video_extensions = ['mp4', '3gp', 'mkv', 'avi', 'webm']

        try:
            if '__auth_log' in request.session:
                if request.session['__auth_log']==1:
                    if request.method=='POST':
                        if self.db_flag:
                            cursor = self.db_instance.cursor()
                            err_img,err_video=False,False
                            if 'p_img' not in request.FILES:
                                err_img=True
                            if 'p_vid' not in request.FILES:
                                err_video=True

                            if err_img==False:
                                flg,p_id=self.getPropertyID(request)

                                if flg==True and p_id!='':
                                    full_path = os.path.join(BASE_DIR, "\\static\\property\\" + p_id + "\\")
                                    for _ in request.FILES.getlist('p_img'):
                                        if _.size>0:
                                            if os.path.exists(BASE_DIR+full_path)==False:
                                                os.mkdir(BASE_DIR+full_path)
                                            full_filename = os.path.join(BASE_DIR+full_path, _.name)
                                            arg=_.name
                                            arg=str(arg).split('.')
                                            if str(arg[1]).lower() not in image_extensions:
                                                error_flag=True
                                                error=_.name
                                                break
                                            try:
                                                with open(full_filename, 'wb+') as fi:
                                                    for chunk in _:
                                                        fi.write(chunk)
                                                    fi.close()
                                                sql="insert into property_media (property_id,type,path,media_date) values " \
                                                    "('"+p_id+"','"+str(arg[1]).lower()+"','"+str(_.name)+"',(select current_date from dual))"
                                                flag,result=self.reader.execute_query(self.empty_result,cursor,sql)
                                                if flag:
                                                    self.db_instance.commit()
                                                else:
                                                    error="Sorry, something is going wrong during updation storage."
                                            except Exception,e:
                                                error="Sorry, something is going wrong "+str(e)
                                else:
                                    error="Unknown property ID recognize for updation"
                            if err_video==False:
                                #############video uploading##################
                                vid=request.FILES['p_vid']
                                #20 MB video file check
                                video_dir=""
                                if vid.size<=20000000:
                                    full_path=os.path.join(BASE_DIR, "\\media\\property\\" + p_id + "\\")
                                    video_dir=BASE_DIR + full_path
                                    if os.path.exists(BASE_DIR + full_path) == False:
                                        try:
                                            os.mkdir(BASE_DIR + full_path)
                                        except Exception,e:
                                            print str(e)
                                    full_filename = os.path.join(BASE_DIR + full_path, vid.name)


                                    arg=vid.name.split('.')

                                    if str(arg[1]).lower() not in video_extensions:
                                        error_flag=True
                                        error="Video extension is reconginze, Please use only .mp4, .3gp, .mkv, .webm, .avi"
                                    else:
                                        fs = FileSystemStorage()
                                        filename = fs.save(video_dir+vid.name, vid)
                                        uploaded_file_url = fs.url(filename)

                                        sql = "insert into property_media (property_id,type,path,media_date) values " \
                                            "('" + p_id + "','" + str(arg[1]).lower() + "','" + str(
                                               vid.name) + "',(select current_date from dual))"
                                        flag,result=self.reader.execute_query(self.empty_result,cursor,sql)

                                        self.db_instance.commit()
                                    if error_flag:
                                        error='Error due to not supporting of extension, '+error
                                        # for video code
                                    elif error=='':
                                        error='Your ads has been added successfully.'
                                else:
                                    error='Error, while uploading file which has size greater than 20 MB.'
                            if err_img and err_video:
                                error='Please select some media files for property'
                        else:
                            error="Error while database connection error."

                    else:
                        error="Error while sending data to server, Please try again."
                else:
                    error='Your session has been removed, Please login again.'
            else:
                error='Please login to access this page.'
        except Exception,e:
            error="Error due to "+str(e)

        return self.operate_page(request, page_no, error)