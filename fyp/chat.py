from django.shortcuts import render
from django.http import request,JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from dbconfig import DataBase
from fyp.reader import Reader
from server import Server
from client import Client
from threading import Thread
from opentok import OpenTok,MediaModes,ArchiveModes,Roles
import time
import urllib3
from stackmessage import StackMessage

class Chat:
    def __init__(self,flag,instance,stack):
        self.db_flag=flag
        self.db_instance=instance
        self.empty_result=False
        self.for_result=True
        self.reader=Reader()
        self.chat_history={}
        self.client = {}
        self.data={}
        self.stack_message=stack
        self.api_key = "46076842"
        self.api_secret = "391b655a884af796fef257bd08d96c4e85c00fc8"


    def blockUser(self,user,client):
        err_flag=False
        try:
            sql="delete from client_friend where username='"+user+"' and client='"+client+"' or username='"+client+"' and client='"+user+"'"
            if self.db_flag:
                cursor = self.db_instance.cursor()
                flag, result = self.reader.execute_query(self.empty_result, cursor, sql)
                if flag:
                    err_flag=False
                else:
                    err_flag=True
            else:
                err_flag=True
        except Exception,e:
            err_flag=True
        return err_flag



    def blockFriend(self,request):
        try:
            if '__auth_log' in request.session:
                if request.session['__auth_log']==1:
                    if request.method=="POST":
                        if 'client' in request.POST:
                            err_f=self.blockUser(request.session['fuser'],request.POST['client'])
                            if err_f==False:
                                data={'type':1,'resp':'Your friend block request completed.'}
                            else:
                                data = {'type': 0, 'resp': 'Your friend block request is not completed.'}
                        else:
                            data = {'type': 0, 'resp': 'Sorry, friend information is not specify.'}
                    else:
                        data = {'type': 0, 'resp': 'Sorry, invalid accessing method.'}
                else:
                    data = {'type': 0, 'resp': 'Sorry, your session is expired. Please login again.'}
            else:
                data = {'type': 0, 'resp': 'Please login.'}
        except Exception,e:
            data = {'type': 1, 'resp': 'Sorry, exception found '+str(e)}
        return JsonResponse(data)

    def getFriendList(self,username):
        lst = []
        try:
            sql="select fullname,username from client where username in (select client from client_friend where username='"+username+"')"

            if self.db_flag:
                cursor=self.db_instance.cursor()
                flag,result=self.reader.execute_query(self.for_result,cursor,sql)
                if flag:
                    if len(result)>0:
                        for _ in result:
                            dic={}
                            dic.setdefault("fullname",_[0])
                            dic.setdefault("user", _[1])
                            lst.append(dic)
        except Exception,e:
            lst=[]
        return lst


    def onconnect(self):
        try:
            sql="select username from client_chat_status where status=1 and username !='"+request.session['fuser']+"'"

            if self.db_flag:
                cursor=self.db_instance.cursor()
                flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                if flag:
                    data = []
                    if len(result)!=0:
                        for _ in result:
                            data.append(_[0])
                        resp={'is_taken':data}
                    else:
                        resp = {'is_taken': data}
                else:
                    resp = {'is_taken': 'No anyone not live for chat'}
            else:
                resp = {'is_taken': 'Sorry, something is going wrong with database/storage.'}
        except Exception,e:
            resp = {'is_taken': 'Sorry, some uncertain error was occur.'}
        return JsonResponse(resp)



    @csrf_exempt
    def sendUserMsg(self, request):
        try:
            if request.method == 'POST':
                if '__auth_log' in request.session:
                    if request.session['__auth_log'] == 1:

                        sql = "insert into client_chat (username,client,msg,msg_date,flag) values ('" + \
                              request.session['fuser'] + "','" + request.POST['client'] + "','" + \
                              request.POST['msg'] + "',(select current_date from dual),'clear')"

                        if self.db_flag:
                            cursor = self.db_instance.cursor()

                            flag,result=self.reader.execute_query(self.empty_result,cursor,sql)
                            if flag:
                                self.stack_message.setMessage(request.session['fuser'],request.POST['client'] ,request.POST['msg'])
                                self.db_instance.commit()
                                data = {'is_taken': ''}
                            else:
                                data = {'is_taken': 'Sorry, msg did not sent yet.'}
                        else:
                            data = {'is_taken': 'Msg saving error due to database'}
                    else:
                        data = {'is_taken': 'Auth error'}
                else:
                    data = {'is_taken': 'Please login'}
            else:
                data = {'is_taken': 'Sending error'}
        except Exception, e:
            data = {'is_taken': 'Error due to ' + str(e)}
        return JsonResponse(data)



    @csrf_exempt
    def getClientMsg(self,request):
        try:
            if request.method == 'POST':
                if '__auth_log' in request.session:
                    if request.session['__auth_log'] == 1:

                        data = {'is_taken': self.stack_message.getMessage(request.POST['client'],request.session['fuser'])}
                        '''sql = "select msg from client_chat where username='"+request.POST['client']+"' and client='"+request.session['fuser']+"' order by msg_date desc"

                        if self.db_flag:
                            cursor = self.db_instance.cursor()
                            flag,result=self.reader.execute_query(self.empty_result,cursor,sql)
                            if flag:
                                if len(result)>0:
                                    data = {'is_taken': result[0][0]}
                                else:
                                    data = {'is_taken': ''}
                            else:
                                data = {'is_taken': 'Sorry, msg did not received yet.'}
                        else:
                            data = {'is_taken': 'Msg saving error due to database'}'''
                    else:
                        data = {'is_taken': 'Auth error'}
                else:
                    data = {'is_taken': 'Please login'}
            else:
                data = {'is_taken': 'Sending error'}
        except Exception, e:
            data = {'is_taken': 'Error due to ' + str(e)}
        print data
        return JsonResponse(data)


    @csrf_exempt
    def getMsg(self,request):
        try:
            if '__auth_log' in request.session:
                if request.session['__auth_log'] == 1:
                    if request.method=='POST':
                        sql="select username,msg from client_chat where username='"+request.session['fuser']+\
                            "' and client='"+request.POST['client']+"' or username='"+request.POST['client']+\
                            "' and client='"+request.session['fuser']+"' order by msg_date asc"


                        if self.db_flag:
                            cursor=self.db_instance.cursor()
                            flag,result=self.reader.execute_query(self.for_result,cursor,sql)
                            if flag:
                                resp_result=""
                                if len(result)>0:
                                    for data in result:
                                        resp_result+=data[0]+"+"+data[1]+"%"
                                    data = {'is_taken': resp_result[:-1]}
                                else:
                                    data = {'is_taken':""}
                            else:
                                data = {'is_taken': 'Sorry, server unable to find chat history'}
                        else:
                            data = {'is_taken': 'Msg saving error due to database'}
                    else:
                        data = {'is_taken': 'Auth error'}
                else:
                    data = {'is_taken': 'Please login'}
            else:
                data={'is_taken':'Sending error'}
        except Exception,e:
            data = {'is_taken': 'Error due to '+str(e)}
        return JsonResponse(data)





    def getClientList(self,user):
        lst = []
        try:
            sql = "select distinct c.username,c.fullname,s.status from client c " \
              "join client_friend f on(c.username in (select client from client_friend " \
              "where username='" + user + "')) join client_chat_status s on(s.username=c.username)"


            if self.db_flag:
                cursor=self.db_instance.cursor()
                flag,result=self.reader.execute_query(self.for_result,cursor,sql)
                if flag:
                    if len(result)!=0:
                        for row in result:
                            di={}
                            di.setdefault("user",row[0])
                            di.setdefault("fullname", row[1])
                            di.setdefault("status", row[2])
                            lst.append(di)
        except Exception,e:
            lst=[]
        return lst

    def chat(self, request):
        return self.operation_about_page(request, 'text', 1)



#################################################################################################################################################################
##############################################################video Chat########################################################################################
###############################################################################################################################################################
    def video(self, request):
        return self.operation_about_page(request, 'video', 0)

    def generate_video_session(self,request):
        try:
            if request.method=="POST":
                client=request.POST['client']
                if '__auth_log' in request.session:
                    if request.session['__auth_log']==1:
                        username=request.session['fuser']
                        return self.get_session_token(username,client)
                    else:
                        data={'type':0,'resp':'Error, while missing comparison auth. Please login again.'}
                else:
                    data = {'type': 0, 'resp': 'Error, while expired of login session. Please login again.'}
            else:
                data = {'type': 0, 'resp': 'Error, while accessing using wrong appoach.'}
        except Exception,e:
            data = {'type': 0, 'resp': 'Error, while due to '+str(e)}
        return JsonResponse(data)

    def get_session_token(self,username,client):
        try:
            t=int(time.time())
            sql="select session_id,token from video_session where to_char(v_date,'dd-Mon-yyyy')="+\
                "(select to_char(current_date,'dd-Mon-yyyy') from dual) and username ='"+username+"' and  client='"+client+\
                "' or username='"+client+"' and client='"+username+"' and v_time>"+str(t)+" order by v_date desc"

            if self.db_flag:
                cursor=self.db_instance.cursor()
                flag,result=self.reader.execute_query(self.for_result,cursor,sql)
                if flag:
                    if len(result)>0:
                        lst=[]
                        lst.append(self.api_key)
                        for _ in result:
                            lst.append(str(_[0]))
                            lst.append(str(_[1]))
                            break
                        data = {'type': 1, "resp": lst}
                    else:
                        return self.generate_session_token(username,client)
                else:
                    data = {'type': 0, "resp": "Sorry, while processing error found."}
            else:
                data = {'type': 0, "resp": "Error, while connecting to database."}
        except Exception,e:
            data = {'type': 0, "resp": "Error, while due to "+str(e)}
        return JsonResponse(data,safe=False)

    def generate_session_token(self,username,client):
        try:
            lst=[]

            try:            
                opentok_obj=OpenTok(self.api_key,self.api_secret)

                session = opentok_obj.create_session(media_mode=MediaModes.routed, archive_mode=ArchiveModes.always)
                session_id = session.session_id
                #token = opentok_obj.generate_token(session_id)
                t=int(time.time()) + 7200
                token = session.generate_token(role=Roles.moderator,
                                           expire_time=t,
                                          data=u'name='+username,
                                  initial_layout_class_list = [u'focus'])
            
                if token!="" and session_id!="":
                    sql="insert into video_session (username,client,session_id,token,v_date,v_time) values ('"+\
                       str(username)+"','"+str(client)+"','"+str(session_id)+"','"+str(token)+"',(select current_date from dual),"+str(t)+")"

                    if self.db_flag:
                        cursor=self.db_instance.cursor()
                        flag,result=self.reader.execute_query(self.empty_result,cursor,sql)
                        if flag:
                            self.db_instance.commit()
                            lst.append(self.api_key)
                            lst.append(session_id)
                            lst.append(token)
                            data={'type':1,"resp":lst}
                        else:
                            data = {'type': 0, "resp": "Sorry, while processing to storage error found."}
                    else:
                        data = {'type': 0, "resp": "Error, while connecting to database."}
                else:
                    data = {'type': 0, "resp": "Error, while creating your session."}
            except Exception,e:
                print str(e)
                data = {'type': 0, "resp": "Error, while creating your session initials."}
        except Exception,e:
            data = {'type': 0, "resp": "Error, while due to "+str(e)}
        
        return JsonResponse(data,safe=False)

    def operation_about_page(self,request,page,typ):
        check = False
        if '__auth_log' in request.session:
            if request.session['__auth_log'] == 1:
               check = True
        lst = []
        if typ == 1:
            username= request.session['fuser']
            lst = self.getFriendList(username)


        try:
            if check:
                return render(request, page+'.html', {'error': '',
                                                     'logvalue': request.session['__auth_log'],
                                                     'fname': request.session['fname'],
                                                     'status': request.session['status'],'chat_client':lst})
            else:
                return render(request, page+'.html', {'error': 'Your session may be finish. Please login again',
                                                     'logvalue': 0, 'fname': 'guest', 'status': -1})

        except Exception, e:
            if check:
                return render(request, page+'.html', {'error': 'Error due to ' + str(e),
                                                     'logvalue': request.session['__auth_log'],
                                                     'fname': request.session['fname'],
                                                     'status': request.session['status'],'chat_client':lst})
            else:
                return render(request, page+'.html', {'error': 'Error due to ' + str(e),
                                                     'logvalue': 0, 'fname': 'guest', 'status': -1})

