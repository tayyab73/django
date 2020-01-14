from mail_ftn import MailService
from reader import Reader
import thread
from django_cron import CronJobBase,Schedule

class CronJob:


    def __init__(self,flag,db_instance):
        self.db_flag = flag
        self.db_instance = db_instance
        self.reader = Reader()
        self.for_result = True
        self.empty_result = False
        self.mailftn = MailService()
        self.contact_email="muhammadtayyab73@gmail.com"




    def subscriberJob(self,p_id):
        error_flag = False
        try:
            if self.db_flag:
                cursor = self.db_instance.cursor()
                #sql = "select ((select count(*) from property)-(select count(*) from subcribe_record where send_date=(select current_date from dual))) as counter from dual"
                property_sql = "select property_id,property_name,address,city,category,price from property where property_id='"+p_id+"' order by property_date desc"
                email_sql = "select email from subscribe"
                flag, result = self.reader.execute_query(self.for_result, cursor, property_sql)
                if flag:
                    flag, email_result = self.reader.execute_query(self.for_result, cursor, email_sql)
                    if flag:
                        if len(email_result)>0:
                            for user_email in email_result:
                                self.mailftn.sent_mail_client(user_email, '',"<h2>BookIt</h2><br><br>"\
                                                              +"<h3><a href='http://192.168.137.1:8000/property_detail?id="+result[0][0]+"'>"\
                                                              + result[0][1] + "</a></h3><br><h4>Address:"+result[0][2]+" , "+result[0][3]+"</h4>"\
                                                            +"<br><h4>Category:"+result[0][4]+"</h4><br><h4>Price:"+result[0][5]+"</h4>")
        except:
            error_flag = True
        return error_flag

    def videoJob(self):
        error_flag=False
        try:
            if self.db_flag:
                sql="delete from video_session where v_time<=(select ((to_char(current_date,'hh')+5)"\
                    "*60+to_char(current_date,'mi'))*60+to_char(current_date,'ss') from dual) and v_date=(select current_date from dual)"
                cursor=self.db_instance.cursor()
                while True:
                    flag, result = self.reader.execute_query(self.empty_result, cursor, sql)
                    if flag==False:
                        error_flag=True
                        break
            else:
                error_flag=True
        except:
            error_flag = True
        return error_flag


    def contactJob(self):
        error_flag = False
        try:
            if self.db_flag:
                cursor = self.db_instance.cursor()
                sql = "select name,email,phone,msg from contact order by contact_date desc"

                flag, result = self.reader.execute_query(self.for_result, cursor, sql)
                if flag:
                    if len(result) > 0:
                        for row in result:
                            self.mailftn.sent_mail_client(self.contact_email, '',"<h2>Contact Notification</h2><br>"+\
                                                                                     "<h4>Name:"+row[0] +"</h4><br><h4>Email:"+ row[1] + "</h4>"+\
                                                              "<h5>Phone:"+row[2]+"</h5><h5>Message:"+row[3]+"</h5>")
                            break


                else:
                    error_flag=False
        except:
            error_flag = True
        return error_flag


