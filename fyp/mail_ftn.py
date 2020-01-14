from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.MIMEText import MIMEText
import smtplib



class MailService:
	def sent_mail_client(self,to_email,code,html_code):
		sent_from = 'tayyabsheikh73@gmail.com'
		pwd='tayyab820575'
		to=[]
		if ',' in to_email:
			to_email=to_email.split(',')
			for _ in to_email:
				to.append(_)
		else:
			to.append(to_email)


		themsg = MIMEMultipart()
		if str(code)!='' and html_code=='':
			themsg['Subject'] = 'Password Recovery'
		else:
			themsg['Subject'] = 'Property Alert from BookIt.com'
		themsg['To'] = ', '.join(to)
		themsg['From'] = sent_from

		themsg.preamble = 'Multipart massage.\n'
		if str(code)!='' and html_code=='':
			part = MIMEText("Hi, Your Password Recovery Code:"+str(code))
		else:
			part= MIMEText(html_code,'html')
		themsg.attach(part)




		themsg = themsg.as_string()
		global server
		try:

			server=smtplib.SMTP('smtp.gmail.com',587)
			server.ehlo()
			server.starttls()
			server.login(sent_from, pwd)

			try:

				server.sendmail(sent_from, to, themsg)

				server.close()
				return True
			except Exception,e:
				return False


		except Exception,e:
			return False
