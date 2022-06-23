from logging import exception
from django.http import response
from django.shortcuts import render, HttpResponse, redirect
from django.conf import settings as config
import json
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import datetime
from datetime import date
from zeep import Client
from zeep.transports import Transport
from django.contrib import messages
from requests.auth import HTTPBasicAuth
# Create your views here.


def login_request(request):
    todays_date = date.today()
    year = todays_date.year
    request.session['years'] = year
    if request.method == 'POST':
        username = request.POST.get('username').upper().strip()
        password = request.POST.get('password').strip()
        print(username, password)
        user = Session()
        user.auth = HTTPBasicAuth(username, password)
        Access_Point = config.O_DATA.format("/QyEmployees")
        Access2 = config.O_DATA.format("/QyUserSetup")
        try:
            CLIENT = Client(config.BASE_URL, transport=Transport(session=user))
            response = user.get(Access_Point, timeout=10).json()
            res_data = user.get(Access2, timeout=10).json()
            Employees = []
            Data = []
            for data in res_data['value']:
                if data['User_ID'] == username:
                    output_json = json.dumps(data)
                    Data.append(json.loads(output_json))
                    request.session['Employee_No_'] = Data[0]['Employee_No_']
                    request.session['Customer_No_'] = Data[0]['Customer_No_']
                    request.session['User_ID'] = Data[0]['User_ID']
                    request.session['E_Mail'] = Data[0]['E_Mail']
                    request.session['User_Responsibility_Center'] = Data[0]['User_Responsibility_Center']
                    print(request.session['User_ID'])
                    print("Emp",request.session['Employee_No_'])

                    for emp in response['value']:
                        if emp['No_'] == request.session['Employee_No_']:
                            request.session['Department'] = emp['Department_Code']
                            print("Department:",request.session['Department'])
                    return redirect('dashboard')

        except requests.exceptions.RequestException as e:
            messages.info(request, e)
            return redirect('auth')
    ctx = {"year": year}
    return render(request, 'auth.html', ctx)
def logout(request):
    try:
        del request.session['User_ID']
        del request.session['Employee_No_']
        del request.session['Customer_No_']
        del request.session['User_Responsibility_Center']
        del request.session['Department']
        messages.success(request,"Logged out successfully")
    except KeyError:
        print(False)
    return redirect('auth')

def profile(request):
    return render(request,"profile.html")