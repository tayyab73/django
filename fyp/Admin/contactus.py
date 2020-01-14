from django.shortcuts import render
from django.http import request,JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from dbconfig import DataBase
from mail_ftn import MailService
from random import randint

