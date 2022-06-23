from django.shortcuts import render, redirect
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import json
from django.conf import settings as config
import datetime
from django.contrib.sessions.models import Session
from django.contrib import messages
# Create your views here.


def dashboard(request):
    try:
        session = requests.Session()
        session.auth = config.AUTHS

        Access_Imprest = config.O_DATA.format("/Imprests")
        Access_Leave = config.O_DATA.format("/QyLeaveApplications")
        Access_Train = config.O_DATA.format("/QyTrainingRequests")
        Access_Surrender = config.O_DATA.format("/QyImprestSurrenders")
        Access_Claim = config.O_DATA.format("/QyStaffClaims")
        Access_purchase = config.O_DATA.format("/QyPurchaseRequisitionHeaders")
        Access_Repair = config.O_DATA.format("/QyRepairRequisitionHeaders")
        Access_Store = config.O_DATA.format("/QyStoreRequisitionHeaders")

        try:
            Imprest = session.get(Access_Imprest, timeout=10).json()
            Leave = session.get(Access_Leave, timeout=10).json()
            Training = session.get(Access_Train, timeout=10).json()
            Surrender = session.get(Access_Surrender, timeout=10).json()
            Claim = session.get(Access_Claim, timeout=10).json()
            Purchase = session.get(Access_purchase, timeout=10).json()
            Repair = session.get(Access_Repair, timeout=10).json()
            Store = session.get(Access_Store, timeout=10).json()

            openLeave = []
            AppLeave = []
            RejLeave = []

            openTraining = []
            AppTraining = []
            RejTraining = []

            openImprest = []
            AppImprest = []
            RejImprest = []

            openSurrender = []
            AppSurrender = []
            RejSurrender = []

            openClaim = []
            AppClaim = []
            RejClaim = []

            openPurchase = []
            AppPurchase = []
            RejPurchase = []

            openRepair = []
            AppRepair = []
            RejRepair = []

            openStore = []
            AppStore = []
            RejStore = []

            for Leave in Leave['value']:
                if Leave['Status'] == 'Open' and Leave['User_ID'] == request.session['User_ID']:
                    output_json = json.dumps(Leave)
                    openLeave.append(json.loads(output_json))
                if Leave['Status'] == 'Released' and Leave['User_ID'] == request.session['User_ID']:
                    output_json = json.dumps(Leave)
                    AppLeave.append(json.loads(output_json))
                if Leave['Status'] == 'Rejected' and Leave['User_ID'] == request.session['User_ID']:
                    output_json = json.dumps(Leave)
                    RejLeave.append(json.loads(output_json))

            for Training in Training['value']:
                if Training['Status'] == 'Open' and Training['Employee_No'] == request.session['Employee_No_']:
                    output_json = json.dumps(Training)
                    openTraining.append(json.loads(output_json))
                if Training['Status'] == 'Released' and Training['Employee_No'] == request.session['Employee_No_']:
                    output_json = json.dumps(Training)
                    AppTraining.append(json.loads(output_json))
                if Training['Status'] == 'Rejected' and Training['Employee_No'] == request.session['Employee_No_']:
                    output_json = json.dumps(Training)
                    RejTraining.append(json.loads(output_json))

            for imprest in Imprest['value']:
                if imprest['Status'] == 'Open' and imprest['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    openImprest.append(json.loads(output_json))
                if imprest['Status'] == 'Released' and imprest['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    AppImprest.append(json.loads(output_json))
                if imprest['Status'] == 'Rejected' and imprest['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    RejImprest.append(json.loads(output_json))
            for Surrender in Surrender['value']:
                if Surrender['Status'] == 'Open' and Surrender['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    openSurrender.append(json.loads(output_json))
                if Surrender['Status'] == 'Released' and Surrender['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    AppSurrender.append(json.loads(output_json))
                if Surrender['Status'] == 'Rejected' and Surrender['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    RejSurrender.append(json.loads(output_json))
            for Claim in Claim['value']:
                if Claim['Status'] == 'Open' and Claim['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    openClaim.append(json.loads(output_json))
                if Claim['Status'] == 'Released' and Claim['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    AppClaim.append(json.loads(output_json))
                if Claim['Status'] == 'Rejected' and Claim['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    RejClaim.append(json.loads(output_json))
            for Purchase in Purchase['value']:
                if Purchase['Status'] == 'Open' and Purchase['Employee_No_'] == request.session['Employee_No_']:
                    output_json = json.dumps(Purchase)
                    openPurchase.append(json.loads(output_json))
                if Purchase['Status'] == 'Released' and Purchase['Employee_No_'] == request.session['Employee_No_']:
                    output_json = json.dumps(Purchase)
                    AppPurchase.append(json.loads(output_json))
                if Purchase['Status'] == 'Rejected' and Purchase['Employee_No_'] == request.session['Employee_No_']:
                    output_json = json.dumps(Purchase)
                    RejPurchase.append(json.loads(output_json))
            for Repair in Repair['value']:
                if Repair['Status'] == 'Open' and Repair['Requested_By'] == request.session['User_ID']:
                    output_json = json.dumps(Repair)
                    openRepair.append(json.loads(output_json))
                if Repair['Status'] == 'Released' and Repair['Requested_By'] == request.session['User_ID']:
                    output_json = json.dumps(Repair)
                    AppRepair.append(json.loads(output_json))
                if Repair['Status'] == 'Rejected' and Repair['Requested_By'] == request.session['User_ID']:
                    output_json = json.dumps(Repair)
                    RejRepair.append(json.loads(output_json))
            for Store in Store['value']:
                if Store['Status'] == 'Open' and Store['Requested_By'] == request.session['User_ID']:
                    output_json = json.dumps(Store)
                    openStore.append(json.loads(output_json))
                if Store['Status'] == 'Released' and Store['Requested_By'] == request.session['User_ID']:
                    output_json = json.dumps(Store)
                    AppStore.append(json.loads(output_json))
                if Store['Status'] == 'Rejected' and Store['Requested_By'] == request.session['User_ID']:
                    output_json = json.dumps(Store)
                    RejStore.append(json.loads(output_json))

            imprest_open = len(openImprest)
            imprest_app = len(AppImprest)
            imprest_rej = len(RejImprest)

            surrender_open = len(openSurrender)
            surrender_app = len(AppSurrender)
            surrender_rej = len(RejSurrender)

            claim_open = len(openClaim)
            claim_app = len(AppClaim)
            claim_rej = len(RejClaim)

            purchase_open = len(openPurchase)
            purchase_app = len(AppPurchase)
            purchase_rej = len(RejPurchase)

            repair_open = len(openRepair)
            repair_app = len(AppRepair)
            repair_rej = len(RejRepair)

            store_open = len(openStore)
            store_app = len(AppStore)
            store_rej = len(RejStore)

            leave_open = len(openLeave)
            leave_App = len(AppLeave)
            leave_rej = len(RejLeave)

            train_open = len(openTraining)
            train_app = len(AppTraining)
            train_rej = len(RejTraining)

        except requests.exceptions.ConnectionError as e:
            print(e)

        Approval = config.O_DATA.format("/QyApprovalEntries")
        try:
            res_App = session.get(Approval, timeout=10).json()
            Approve = []
            for approve in res_App['value']:
                if approve['Status'] == 'Open' and approve['Approver_ID'] == request.session['User_ID']:
                    output_json = json.dumps(approve)
                    Approve.append(json.loads(output_json))
            countsAPP = len(Approve)
        except requests.exceptions.ConnectionError as e:
            print(e)
        fullname =  request.session['User_ID']
        Responsibility = request.session['User_Responsibility_Center']
        E_Mail = request.session['E_Mail']
        Employee_No_ = request.session['Employee_No_']
        Customer_No_ = request.session['Customer_No_']

        todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")

        ctx = {"today": todays_date,
            "res": open, "full": fullname,
            "Responsibility": Responsibility, "E_Mail": E_Mail,
            "Employee_No_": Employee_No_, "Customer_No_": Customer_No_,
            "apps": Approve, "countsAPP": countsAPP,
            "leave_open": leave_open, "leave_app": leave_App,
            "leave_rej": leave_rej, "open_train": train_open,
            "app_train": train_app, "rej_train": train_rej,
            "imprest_open": imprest_open, "imprest_app": imprest_app,
            "imprest_rej": imprest_rej, "surrender_open": surrender_open,
            "surrender_app": surrender_app, "surrender_rej": surrender_rej,
            "open_claim": claim_open, "app_claim": claim_app,
            "rej_claim": claim_rej, "open_purchase": purchase_open,
            "app_purchase": purchase_app, "rej_purchase": purchase_rej,
            "open_repair": repair_open, "app_repair": repair_app,
            "rej_repair": repair_rej, "open_store": store_open,
            "app_store": store_app, "rej_store": store_rej
            }
    except KeyError as e:
        messages.success(request, "Session Expired. Please Login")
        return redirect('auth')
    return render(request, 'main/dashboard.html', ctx)


def details(request, pk):

    todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date}
    return render(request, "main/details.html", ctx)


def Canvas(request):

    fullname =  request.session['User_ID']
    ctx = {"fullname": fullname}
    return render(request, "offcanvas.html", ctx)
