"""fyp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url
from django.contrib import admin

from stackmessage import StackMessage
from views import Project
from login import Login
from signup import SignUp
from recoverypassword import RecoveryPassword
from chat import Chat
from property_search import Property_Search
from new_property import New_Property
from client_info import Client_Information
from webservices import WebServices
from django.conf import settings

from django.conf.urls.static import static
from dbconfig import DataBase
from cronjob import CronJob



db_instance=DataBase()
flag,db_inst=db_instance.get_connection()
cronjob=CronJob(flag,db_inst)
print db_inst
###################################################################################################################
##########################################################Objects#################################################
#####################################################################################################################
stack=StackMessage()
project=Project(flag,db_inst)
login_=Login(flag,db_inst)
sign=SignUp(flag,db_inst)
recovery_password=RecoveryPassword(flag,db_inst)
chat=Chat(flag,db_inst,stack)
np=New_Property(flag,db_inst)
ps=Property_Search(flag,db_inst)
info=Client_Information(flag,db_inst)
service=WebServices(flag,db_inst,stack)



urlpatterns = [
url(r'^admin/', admin.site.urls),
######################################################################################################



###########################################################################################################
############################Login Auth#####################################################################
#############################################################################################################
url(r'^login',login_.login, name='login' ),
url(r'^checkLoginUsername',login_.checkLoginUsername, name='checkLoginUsername' ),
url(r'^logout',project.logout, name='logout' ),
url(r'^checkVerifyScode',login_.checkVerifyScode, name='checkVerifyScode' ),
######################################################################################################################
####################################################################################################################








################################################################################################################
####################################SignUp Auth ##################################################################
###################################################################################################################
url(r'^register',sign.register, name='register' ),
url(r'^r_newuser',sign.checknewuser, name='r_newuser' ),
############################################################################################################
#############################################################################################################






##################################################################################################################
####################################Recovery Password Auth #######################################################
###################################################################################################################
url(r'^securitycode',recovery_password.securitycode, name='securitycode' ),
url(r'^recovery-account',recovery_password.recoverypassword, name='recovery-account' ),
url(r'^forget-password',recovery_password.forgetpassword, name='forget-password' ),
url(r'^save-recovery-account',recovery_password.finalrecovery, name='save-recovery-account' ),
##########################################################################################################
############################################################################################################
##############################################################################################################




###############################################################################################################
##################################Client Information############################################################
#################################################################################################################
url(r'^settings',info.setting, name='settings' ),
url(r'^verify',info.verify, name='verify' ),
url(r'^updateVerification',info.verification, name='updateVerification' ),
url(r'^notification', info.notification, name='notification'),
url(r'^alert_notify', info.notification_alert, name='alert_notify'),
url(r'^saved', info.saved_properties, name='saved'),
url(r'^adshistory', info.getAdsHistory, name='adshistory'),
url(r'^p_saved', info.saved_property_to_acc, name='p_saved'),
url(r'^delete_p', info.deleteads, name='delete_p'),

url(r'^change_password', info.change_password, name='change_password'),
url(r'^chg_profile', info.change_profile, name='chg_profile'),
url(r'^ac_deactive', info.deactive_account, name='ac_deactive'),
url(r'^delads', info.delete_ad, name='delads'),
url(r'^editads', info.editads, name='editads'),
url(r'^submit_editads', info.submitEditAds, name='submit_editads'),
url(r'^upd_request', info.accept_payment_request, name='upd_request'),
url(r'^delete_re', info.del_payment_request, name='delete_re'),
url(r'^pay_req', info.payment_request, name='pay_req'),
url(r'^new_payinfo', info.send_payment_info, name='new_payinfo'),
url(r'^profile_pay', info.get_profile, name='profile_pay'),
url(r'^trans_pay', info.transfer_property, name='trans_pay'),
url(r'^payment', info.payment_method, name='payment'),

#############################################################################################################
#############################################################################################################









##################################################################################################################
########################################Client Chat###############################################################
###################################################################################################################
url(r'^getMsg',chat.getMsg, name='getMsg' ),
url(r'^sendUserMsg',chat.sendUserMsg, name='sendUserMsg' ),
url(r'^getClientMsg',chat.getClientMsg, name='getClientMsg' ),
url(r'^chat',chat.chat, name='chat' ),
url(r'^video',chat.video, name='video' ),
url(r'^geneSession',chat.generate_video_session, name='geneSession' ),
url(r'^blockf',chat.blockFriend, name='blockf' ),
#################################################################################################################
####################################################################################################################









###############################################################################################################
###############################New Ads property##############################################################
    ##########################################################################################################
url(r'^new-ads',np.newads, name='new-ads' ),
url(r'^middle_registration',np.middle_regisgration, name='middle_registration' ),
url(r'^ads-finish',np.finalRegAd, name='ads-finish' ),
###########################################################################################################
###########################################################################################################








########################################################################################################
##################################Searching Property######################################################
############################################################################################################
url(r'^property-detail', ps.detail, name='property-detail'),
url(r'^query-search', ps.property_search, name='query-search'),
url(r'^send_email', ps.send_email, name='send_email'),
url(r'^sent_sms', ps.send_mobile, name='sent_sms'),
url(r'^feedback', ps.feedback, name='feedback'),
url(r'^rating', ps.save_rating, name='rating'),

###########################################################################################################
#######################################################################################################







#####################################################################################################
###################################Web services ##################################################
#######################################################################################################
url(r'^weblogin', service.login, name='weblogin'),
url(r'^webprofile', service.profile, name='webprofile'),
url(r'^webchangepassword', service.change_password, name='webchangepassword'),
url(r'^webads', service.ads_history, name='webads'),
url(r'^websignup', service.signup, name='websignup'),
url(r'^webnewads', service.new_property, name='webnewads'),
url(r'^webproperty', service.get_property, name='webproperty'),
url(r'^webp_byid', service.get_property_by_id, name='webp_byid'),
url(r'^webp_img', service.get_property_images_by_id, name='webp_img'),
url(r'^weblogout', service.logout, name='weblogout'),
url(r'^webforget_password', service.forget_password, name='webforget_password'),
url(r'^webrecovery_p', service.recovery_password, name='webrecovery_p'),
    #################################
url(r'^webcontact', service.contact, name='webcontact'),
url(r'^websubscribed', service.subscribe, name='websubscribed'),
    #####################################
url(r'^webp_upload_media', service.save_media, name='webp_upload_media'),

url(r'^webp_savedop', service.ope_save_property, name='webp_savedop'),
url(r'^webproperation', service.operation_property, name='webproperation'),
url(r'^webnotify', service.notification_alert, name='webnotify'),
url(r'^websms', service.send_sms, name='websms'),
url(r'^webemail', service.send_email, name='webemail'),
url(r'^webp_feedrating', service.get_feedback_rating, name='webp_feedrating'),
url(r'^webp_savefr', service.feedback_rating, name='webp_savefr'),
url(r'^webp_saveproperty', service.save_property, name='webp_saveproperty'),

url(r'^webc_getfriend', service.getFriendlist, name='webc_getfriend'),
url(r'^webc_sendmsg', service.sendMsg, name='webc_sendmsg'),
url(r'^webc_history', service.getChatHistory, name='webc_history'),
url(r'^webc_receivemsg', service.getReceiveMsg, name='webc_receivemsg'),
url(r'^webc_geneSession', service.generate_video_session, name='webc_geneSession'),
####################################################################################################
######################################################################################################










##############################################################################################################
############################### public Website pages #########################################################
###############################################################################################################
url(r'^getPrice',project.getprice, name='getPrice' ),
url(r'^agents',project.agents, name='agents' ),
url(r'^about', project.about, name='about'),
url(r'^contactRequest', project.contactRequest, name='contactRequest'),
url(r'^c_subscribe', project.notify, name='c_subscribe'),
url(r'^contact', project.contact, name='contact'),


#################################################################################################################
##################################################################################################################
#####################################################################################################################
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)+[url(r'^',project.home, name='home' )]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
