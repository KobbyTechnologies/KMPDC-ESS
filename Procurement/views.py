import base64
from ctypes.wintypes import PHKEY
from urllib.parse import parse_qs
from django.shortcuts import render, redirect
from datetime import date, datetime
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import json
from django.conf import settings as config
import datetime as dt
from django.contrib import messages
import enum
import secrets
from django.http import HttpResponse
import io as BytesIO
import string
from zeep import Client
from zeep.transports import Transport
from requests.auth import HTTPBasicAuth
from django.http import JsonResponse

# Create your views here.


def PurchaseRequisition(request):
    try:
        fullname = request.session['User_ID']
        year = request.session['years']
        session = requests.Session()
        session.auth = config.AUTHS
        Access_Point = config.O_DATA.format("/QyPurchaseRequisitionHeaders")
        try:
            response = session.get(Access_Point, timeout=10).json()
            open = []
            Approved = []
            Rejected = []
            Pending = []
            for document in response['value']:
                if document['Status'] == 'Open' and document['Employee_No_'] == request.session['Employee_No_']:
                    output_json = json.dumps(document)
                    open.append(json.loads(output_json))
                if document['Status'] == 'Released' and document['Employee_No_'] == request.session['Employee_No_']:
                    output_json = json.dumps(document)
                    Approved.append(json.loads(output_json))
                if document['Status'] == 'Disapproved' and document['Employee_No_'] == request.session['Employee_No_']:
                    output_json = json.dumps(document)
                    Rejected.append(json.loads(output_json))
                if document['Status'] == "Pending Approval" and document['Employee_No_'] == request.session['Employee_No_']:
                    output_json = json.dumps(document)
                    Pending.append(json.loads(output_json))
            counts = len(open)
            counter = len(Approved)
            reject = len(Rejected)
            pend = len(Pending)
        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')

        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")

        ctx = {"today": todays_date, "res": open,
            "count": counts, "response": Approved,
            "counter": counter, "rej": Rejected,
            'reject': reject, "pend": pend,
            "pending": Pending, "year": year,
            "full": fullname}
    except KeyError:
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')
    return render(request, 'purchaseReq.html', ctx)


def CreatePurchaseRequisition(request):
    requisitionNo = ''
    orderDate = ''
    myAction = ' '
    if request.method == 'POST':
        try:
            requisitionNo = request.POST.get('requisitionNo')
            myUserId = request.session['User_ID']
            employeeNo = request.session['Employee_No_']
            orderDate = datetime.strptime(
                request.POST.get('orderDate'), '%Y-%m-%d').date()
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.error(request, "Missing Input")
            return redirect('purchase')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        if not requisitionNo:
            requisitionNo = " "
        try:
            response = config.CLIENT.service.FnPurchaseRequisitionHeader(
                requisitionNo, orderDate, employeeNo, myUserId, myAction)
            messages.success(request, "Request Successful")
            print(response)
        except Exception as e:
            messages.info(request, e)
            print(e)
            return redirect('purchase')
    return redirect('purchase')


def PurchaseRequestDetails(request, pk):
    try:
        session = requests.Session()
        session.auth = config.AUTHS
        state = ''
        res = ''
        Current_Year = date.today()
        Access_Point = config.O_DATA.format("/QyPurchaseRequisitionHeaders")
        Approver = config.O_DATA.format("/QyApprovalEntries")
        ProcPlan = config.O_DATA.format("/QyProcurementPlans")
        itemNo = config.O_DATA.format("/QyItems")
        GL_Acc = config.O_DATA.format("/QyGLAccounts")
        Lines_Res = config.O_DATA.format("/QyPurchaseRequisitionLines")
        try:
            response = session.get(Access_Point, timeout=10).json()
            res_approver = session.get(Approver, timeout=10).json()
            Res_Proc = session.get(ProcPlan, timeout=10).json()
            Res_itemNo = session.get(itemNo, timeout=10).json()
            Res_GL = session.get(GL_Acc, timeout=10).json()
            response_Lines = session.get(Lines_Res, timeout=10).json()
            openLines = []
            openImp = []
            res_type = []
            Pending = []
            Approvers = []
            Proc = []
            Items = Res_itemNo['value']
            Gl_Accounts = Res_GL['value']
            planitem = []
            for plans in Res_Proc['value']:
                if plans['Shortcut_Dimension_2_Code'] == request.session['Department']:
                    output_json = json.dumps(plans)
                    planitem.append(json.loads(output_json))
            for approver in res_approver['value']:
                if approver['Document_No_'] == pk:
                    output_json = json.dumps(approver)
                    Approvers.append(json.loads(output_json))
            for document in response['value']:
                if document['Status'] == 'Disapproved' and document['Employee_No_'] == request.session['Employee_No_']:
                    output_json = json.dumps(document)
                    openImp.append(json.loads(output_json))
                    for document in openImp:
                        if document['No_'] == pk:
                            res = document
                if document['Status'] == 'Open' and document['Employee_No_'] == request.session['Employee_No_']:
                    output_json = json.dumps(document)
                    openImp.append(json.loads(output_json))
                    for document in openImp:
                        if document['No_'] == pk:
                            res = document
                            if document['Status'] == 'Open':
                                state = 1
                if document['Status'] == 'Released' and document['Employee_No_'] == request.session['Employee_No_']:
                    output_json = json.dumps(document)
                    openImp.append(json.loads(output_json))
                    for document in openImp:
                        if document['No_'] == pk:
                            res = document
                            if document['Status'] == 'Released':
                                state = 3
                if document['Status'] == "Pending Approval" and document['Employee_No_'] == request.session['Employee_No_']:
                    output_json = json.dumps(document)
                    Pending.append(json.loads(output_json))
                    for document in Pending:
                        if document['No_'] == pk:
                            res = document
                            if document['Status'] == 'Pending Approval':
                                state = 2
            for document in response_Lines['value']:
                if document['AuxiliaryIndex1'] == pk:
                    output_json = json.dumps(document)
                    openLines.append(json.loads(output_json))
        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, "Whoops! Something went wrong. Please Login to Continue")
            return redirect('purchase')
        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
        ctx = {"today": todays_date, "res": res,
            "state": state, "line": openLines,
            "type": res_type, "Approvers": Approvers,
            "plans": planitem, "items": Items,
            "gl": Gl_Accounts}
    except KeyError as e:
        print(e)
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')
    return render(request, 'purchaseDetail.html', ctx)


def CreatePurchaseLines(request, pk):
    lineNo = ""
    procPlanItem = ''
    itemTypes = ""
    itemNo = ""
    specification = ''
    quantity = 1
    myAction = ''
    if request.method == 'POST':
        try:
            myUserId = request.session['User_ID']
            lineNo = int(request.POST.get('lineNo'))
            procPlanItem = request.POST.get('procPlanItem')
            itemTypes = request.POST.get('itemTypes')
            itemNo = request.POST.get('itemNo')
            specification = request.POST.get('specification')
            quantity = int(request.POST.get('quantity'))
            myAction = request.POST.get('myAction')

        except ValueError:
            messages.error(request, "Missing Input")
            return redirect('PurchaseDetail', pk=pk)
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        class Data(enum.Enum):
            values = itemTypes
        itemType = (Data.values).value

        if not procPlanItem:
            procPlanItem = ""
        try:
            response = config.CLIENT.service.FnPurchaseRequisitionLine(
                pk, lineNo, procPlanItem, itemType, itemNo, specification, quantity, myUserId, myAction)
            messages.success(request, "Request Successful")
            print(response)
            return redirect('PurchaseDetail', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('PurchaseDetail', pk=pk)
    return redirect('PurchaseDetail', pk=pk)


def PurchaseApproval(request, pk):
    Username = request.session['User_ID']
    Password = request.session['password']
    AUTHS = Session()
    AUTHS.auth = HTTPBasicAuth(Username, Password)
    CLIENT = Client(config.BASE_URL, transport=Transport(session=AUTHS))
    requistionNo = ""
    if request.method == 'POST':
        try:
            requistionNo = request.POST.get('requistionNo')
            myUserID = request.session['User_ID']
        except ValueError as e:
            messages.error(request, "Missing Input")
            return redirect('PurchaseDetail', pk=pk)
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        try:
            response = CLIENT.service.FnRequestInternalRequestApproval(
                myUserID, requistionNo)
            messages.success(request, "Approval Request Sent Successfully")
            print(response)
            return redirect('PurchaseDetail', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('PurchaseDetail', pk=pk)
    return redirect('PurchaseDetail', pk=pk)


def UploadPurchaseAttachment(request, pk):
    response = ""
    fileName = ""
    attachment = ""
    tableID = 52177432
    if request.method == "POST":
        try:
            attach = request.FILES.getlist('attachment')
        except Exception as e:
            return redirect('PurchaseDetail', pk=pk)
        for files in attach:
            fileName = request.FILES['attachment'].name
            attachment = base64.b64encode(files.read())
            try:
                response = config.CLIENT.service.FnUploadAttachedDocument(
                    pk, fileName, attachment, tableID,request.session['User_ID'])
            except Exception as e:
                messages.error(request, e)
                print(e)
        if response == True:
            messages.success(request, "File(s) Uploaded Successfully")
            return redirect('PurchaseDetail', pk=pk)
        else:
            messages.error(request, "Failed, try Again")
            return redirect('PurchaseDetail', pk=pk)
    return redirect('PurchaseDetail', pk=pk)


def FnCancelPurchaseApproval(request, pk):
    requistionNo = ""
    if request.method == 'POST':
        requistionNo = request.POST.get('requistionNo')
        try:
            response = config.CLIENT.service.FnCancelInternalRequestApproval(
                request.session['User_ID'], requistionNo)
            messages.success(request, "Cancel Approval Successful")
            print(response)
            return redirect('PurchaseDetail', pk=pk)
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('PurchaseDetail', pk=pk)
    return redirect('PurchaseDetail', pk=pk)

def FnGeneratePurchaseReport(request, pk):
    nameChars = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                        for i in range(5))
    if request.method == 'POST':
        filenameFromApp = pk + str(nameChars) + ".pdf"
        try:
            response = config.CLIENT.service.FnGenerateRequisitionReport(
                pk, filenameFromApp)
            buffer = BytesIO.BytesIO()
            content = base64.b64decode(response)
            buffer.write(content)
            responses = HttpResponse(
                buffer.getvalue(),
                content_type="application/pdf",
            )
            responses['Content-Disposition'] = f'inline;filename={filenameFromApp}'
            return responses
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('PurchaseDetail', pk=pk)
    return redirect('PurchaseDetail', pk=pk)


def FnDeletePurchaseRequisitionLine(request, pk):
    lineNo = ""
    if request.method == 'POST':
        lineNo = int(request.POST.get('lineNo'))
        try:
            response = config.CLIENT.service.FnDeletePurchaseRequisitionLine(
                pk, lineNo)
            messages.success(request, "Successfully Deleted")
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('PurchaseDetail', pk=pk)
    return redirect('PurchaseDetail', pk=pk)


def RepairRequest(request):
    try:
        fullname = request.session['User_ID']
        year = request.session['years']
        session = requests.Session()
        session.auth = config.AUTHS

        Access_Point = config.O_DATA.format("/QyRepairRequisitionHeaders")
        try:
            response = session.get(Access_Point, timeout=10).json()
            open = []
            Approved = []
            Rejected = []
            Pending = []
            for document in response['value']:
                if document['Status'] == 'Open' and document['Requested_By'] == request.session['User_ID']:
                    output_json = json.dumps(document)
                    open.append(json.loads(output_json))
                if document['Status'] == 'Released' and document['Requested_By'] == request.session['User_ID']:
                    output_json = json.dumps(document)
                    Approved.append(json.loads(output_json))
                if document['Status'] == 'Disapproved' and document['Requested_By'] == request.session['User_ID']:
                    output_json = json.dumps(document)
                    Rejected.append(json.loads(output_json))
                if document['Status'] == "Pending Approval" and document['Requested_By'] == request.session['User_ID']:
                    output_json = json.dumps(document)
                    Pending.append(json.loads(output_json))
            counts = len(open)
            counter = len(Approved)
            reject = len(Rejected)
            pend = len(Pending)
        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')

        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
        ctx = {"today": todays_date, "res": open,
            "count": counts, "response": Approved,
            "counter": counter, "rej": Rejected,
            'reject': reject, "pend": pend,
            "year": year, "full": fullname,
            "pending": Pending
            }
    except KeyError:
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')
    return render(request, 'repairReq.html', ctx)


def CreateRepairRequest(request):
    requisitionNo = ''
    orderDate = ''
    reason = ""
    myAction = ' '
    if request.method == 'POST':
        try:
            employeeNo = request.session['Employee_No_']
            myUserId = request.session['User_ID']
            requisitionNo = request.POST.get('requisitionNo')
            orderDate = datetime.strptime(
                request.POST.get('orderDate'), '%Y-%m-%d').date()
            reason = request.POST.get('reason')
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.error(request, "Missing Input")
            return redirect('repair')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        if not requisitionNo:
            requisitionNo = " "
        try:
            response = config.CLIENT.service.FnRepairRequisitionHeader(
                requisitionNo, orderDate, employeeNo, reason, myUserId, myAction)
            messages.success(request, "Request Successful")
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('repair')
    return redirect('repair')


def RepairRequestDetails(request, pk):
    try:
        fullname = request.session['User_ID']
        year = request.session['years']
        session = requests.Session()
        session.auth = config.AUTHS
        state = ''
        res = ''
        output_json = ''
        Access_Point = config.O_DATA.format("/QyRepairRequisitionHeaders")
        Assets = config.O_DATA.format("/QyFixedAssets")
        Approver = config.O_DATA.format("/QyApprovalEntries")
        Lines_Res = config.O_DATA.format("/QyRepairRequisitionLines")
        try:
            response = session.get(Access_Point, timeout=10).json()
            Assest_res = session.get(Assets, timeout=10).json()
            res_approver = session.get(Approver, timeout=10).json()
            response_Lines = session.get(Lines_Res, timeout=10).json()
            openLines = []
            openImp = []
            res_type = []
            Approvers = []
            my_asset =[]

            for assest in Assest_res['value']:
                if assest['Responsible_Employee'] == request.session['Employee_No_']:
                    output_json = json.dumps(assest)
                    my_asset.append(json.loads(output_json))
            for approver in res_approver['value']:
                if approver['Document_No_'] == pk:
                    output_json = json.dumps(approver)
                    Approvers.append(json.loads(output_json))
            for document in response['value']:
                if document['Status'] == 'Open' and document['Requested_By'] == request.session['User_ID']:
                    output_json = json.dumps(document)
                    openImp.append(json.loads(output_json))
                    for document in openImp:
                        if document['No_'] == pk:
                            res = document
                            if document['Status'] == 'Open':
                                state = 1
                if document['Status'] == 'Released' and document['Requested_By'] == request.session['User_ID']:
                    output_json = json.dumps(document)
                    openImp.append(json.loads(output_json))
                    for document in openImp:
                        if document['No_'] == pk:
                            res = document
                            if document['Status'] == 'Released':
                                state = 3

                if document['Status'] == 'Disapproved' and document['Requested_By'] == request.session['User_ID']:
                    output_json = json.dumps(document)
                    openImp.append(json.loads(output_json))
                    for document in openImp:
                        if document['No_'] == pk:
                            res = document
                if document['Status'] == "Pending Approval" and document['Requested_By'] == request.session['User_ID']:
                    output_json = json.dumps(document)
                    openImp.append(json.loads(output_json))
                    for document in openImp:
                        if document['No_'] == pk:
                            res = document
                            if document['Status'] == 'Pending Approval':
                                state = 2
            for document in response_Lines['value']:
                if document['AuxiliaryIndex1'] == pk:
                    output_json = json.dumps(document)
                    openLines.append(json.loads(output_json))
        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, "Whoops! Something went wrong. Please Login to Continue")
            return redirect('repair')
        ctx = {"res": res,
            "state": state, "line": openLines,
            "type": res_type, "Approvers": Approvers,
            "asset": my_asset, "full": fullname,
            "year": year}
    except KeyError:
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')
    return render(request, 'repairDetail.html', ctx)


def RepairApproval(request, pk):
    Username = request.session['User_ID']
    Password = request.session['password']
    AUTHS = Session()
    AUTHS.auth = HTTPBasicAuth(Username, Password)
    CLIENT = Client(config.BASE_URL, transport=Transport(session=AUTHS))
    requistionNo = ""
    if request.method == 'POST':
        try:
            requistionNo = request.POST.get('requistionNo')
            myUserID = request.session['User_ID']
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        try:
            response = CLIENT.service.FnRequestInternalRequestApproval(
                myUserID, requistionNo)
            messages.success(request, "Approval Request Sent Successfully")
            print(response)
            return redirect('RepairDetail', pk=pk)
        except Exception as e:
            messages.info(request, e)
            print(e)
            return redirect('RepairDetail', pk=pk)
    return redirect('RepairDetail', pk=pk)

def FnCancelRepairApproval(request, pk):
    requistionNo = ""
    if request.method == 'POST':
        try:
            myUserID = request.session['User_ID']
            requistionNo = request.POST.get('requistionNo')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        try:
            response = config.CLIENT.service.FnCancelInternalRequestApproval(
                myUserID, requistionNo)
            messages.success(request, "Cancel Approval Successful")
            print(response)
            return redirect('RepairDetail', pk=pk)
        except Exception as e:
            messages.info(request, e)
            print(e)
            return redirect('RepairDetail', pk=pk)
    return redirect('RepairDetail', pk=pk)


def CreateRepairLines(request, pk):
    lineNo = ""
    assetCode = ''
    description = ''
    myAction = ''
    if request.method == 'POST':
        try:
            lineNo = int(request.POST.get('lineNo'))
            assetCode = request.POST.get('assetCode')
            OtherAsset = request.POST.get('OtherAsset')
            description = request.POST.get('description')
            attach = request.FILES.getlist('attachment')
            myAction = request.POST.get('myAction')
            tableID = 52177433
        except ValueError:
            messages.error(request, "Missing Input")
            return redirect('RepairDetail', pk=pk)

        if not OtherAsset:
            OtherAsset = ''
        try:
            response = config.CLIENT.service.FnRepairRequisitionLine(
                pk, lineNo, assetCode, description, myAction,OtherAsset)
            print(response)
            if response !=0 and not attach:
                messages.success(request, "Request Successful")
                return redirect('RepairDetail', pk=pk)
            if attach and response != 0:
                for files in attach:
                    fileName = request.FILES['attachment'].name
                    attachment = base64.b64encode(files.read())
                    try:
                        responses = config.CLIENT.service.FnUploadAttachedDocument(
                            pk +'#'+str(response), fileName, attachment, tableID,request.session['User_ID'])
                        if responses == True:
                            messages.success(request, "Request Successful")
                            return redirect('RepairDetail', pk=pk)
                        else:
                            messages.error(request, "Failed, Try Again")
                            return redirect('RepairDetail', pk=pk)
                    except Exception as e:
                        messages.error(request, e)
                        print(e)
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('RepairDetail', pk=pk)
    return redirect('RepairDetail', pk=pk)

def FnDeleteRepairRequisitionLine(request, pk):
    lineNo = ""
    if request.method == 'POST':
        lineNo = int(request.POST.get('lineNo'))
        try:
            response = config.CLIENT.service.FnDeleteRepairRequisitionLine(
                pk, lineNo)
            messages.success(request, "Successfully Deleted")
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('RepairDetail', pk=pk)
    return redirect('RepairDetail', pk=pk)


def StoreRequest(request):
    try:
        fullname = request.session['User_ID']
        year = request.session['years']
        session = requests.Session()
        session.auth = config.AUTHS

        Access_Point = config.O_DATA.format("/QyStoreRequisitionHeaders")
        try:
            response = session.get(Access_Point, timeout=10).json()
            open = []
            Approved = []
            Rejected = []
            Pending = []
            for document in response['value']:
                if document['Status'] == 'Open' and document['Requested_By'] == request.session['User_ID']:
                    output_json = json.dumps(document)
                    open.append(json.loads(output_json))
                if document['Status'] == 'Released' and document['Requested_By'] == request.session['User_ID']:
                    output_json = json.dumps(document)
                    Approved.append(json.loads(output_json))
                if document['Status'] == 'Disapproved' and document['Requested_By'] == request.session['User_ID']:
                    output_json = json.dumps(document)
                    Rejected.append(json.loads(output_json))
                if document['Status'] == "Pending Approval" and document['Requested_By'] == request.session['User_ID']:
                    output_json = json.dumps(document)
                    Pending.append(json.loads(output_json))
            counts = len(open)
            counter = len(Approved)
            reject = len(Rejected)
            pend = len(Pending)
        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')

        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
        ctx = {"today": todays_date, "res": open,
            "count": counts, "response": Approved,
            "counter": counter, "rej": Rejected,
            'reject': reject,
            "pend": pend, "pending": Pending,
            "full": fullname, "year": year}
    except KeyError:
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')
    return render(request, 'storeReq.html', ctx)


def CreateStoreRequisition(request):
    requisitionNo = ''
    reason = ""
    myAction = ''
    if request.method == 'POST':
        try:
            requisitionNo = request.POST.get('requisitionNo')
            reason = request.POST.get('reason')
            myAction = request.POST.get('myAction')
            myUserId = request.session['User_ID']
            employeeNo = request.session['Employee_No_']
        except ValueError:
            messages.error(request, "Missing Input")
            return redirect('store')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        if not requisitionNo:
            requisitionNo = " "

        try:
            response = config.CLIENT.service.FnStoreRequisitionHeader(
                requisitionNo, employeeNo, reason, myUserId, myAction)
            messages.success(request, "Request Successful")
            print(response)
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('store')
    return redirect('store')


def StoreRequestDetails(request, pk):
    try:
        fullname = request.session['User_ID']
        year = request.session['years']
        session = requests.Session()
        session.auth = config.AUTHS
        state = ''
        res = ''
        Access_Point = config.O_DATA.format("/QyStoreRequisitionHeaders")
        ItemCategory = config.O_DATA.format("/QyItemCategories")
        Location = config.O_DATA.format("/QyLocations")
        Approver = config.O_DATA.format("/QyApprovalEntries")
        Lines_Res = config.O_DATA.format("/QyStoreRequisitionLines")
        try:
            response = session.get(Access_Point, timeout=10).json()
            Loc_res = session.get(Location, timeout=10).json()
            res_approver = session.get(Approver, timeout=10).json()
            response_Lines = session.get(Lines_Res, timeout=10).json()
            openLines = []
            openImp = []
            res_type = []
            Approvers = []
            Item_Cat = session.get(ItemCategory, timeout=10).json()
            itemsCategory = Item_Cat['value']
            Location = Loc_res['value']
            for approver in res_approver['value']:
                if approver['Document_No_'] == pk:
                    output_json = json.dumps(approver)
                    Approvers.append(json.loads(output_json))
            for document in response['value']:
                if document['Status'] == 'Released' and document['Requested_By'] == request.session['User_ID']:
                    output_json = json.dumps(document)
                    openImp.append(json.loads(output_json))
                    for document in openImp:
                        if document['No_'] == pk:
                            res = document
                            if document['Status'] == 'Released':
                                state = 3
                if document['Status'] == 'Open' and document['Requested_By'] == request.session['User_ID']:
                    output_json = json.dumps(document)
                    openImp.append(json.loads(output_json))
                    for document in openImp:
                        if document['No_'] == pk:
                            res = document
                            if document['Status'] == 'Open':
                                state = 1
                if document['Status'] == 'Disapproved' and document['Requested_By'] == request.session['User_ID']:
                    output_json = json.dumps(document)
                    openImp.append(json.loads(output_json))
                    for document in openImp:
                        if document['No_'] == pk:
                            res = document
                if document['Status'] == "Pending Approval" and document['Requested_By'] == request.session['User_ID']:
                    output_json = json.dumps(document)
                    openImp.append(json.loads(output_json))
                    for document in openImp:
                        if document['No_'] == pk:
                            res = document
                            if document['Status'] == 'Pending Approval':
                                state = 2                
            for document in response_Lines['value']:
                if document['AuxiliaryIndex1'] == pk:
                    output_json = json.dumps(document)
                    openLines.append(json.loads(output_json))
        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')
        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
        ctx = {"today": todays_date, "res": res,
            "state": state, "line": openLines,
            "type": res_type, 
            "Approvers": Approvers, "loc": Location,
            "year": year, "full": fullname,
            "itemsCategory": itemsCategory}
    except KeyError:
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')
    return render(request, 'storeDetail.html', ctx)

def itemCategory(request):
    session = requests.Session()
    session.auth = config.AUTHS
    Item = config.O_DATA.format("/QyItems")
    text = request.GET.get('ItemCode')
    try:
        Item_res = session.get(Item, timeout=10).json()
        return JsonResponse(Item_res)

    except  Exception as e:
        pass
    return redirect('store')

def StoreApproval(request, pk):
    Username = request.session['User_ID']
    Password = request.session['password']
    AUTHS = Session()
    AUTHS.auth = HTTPBasicAuth(Username, Password)
    CLIENT = Client(config.BASE_URL, transport=Transport(session=AUTHS))
    requistionNo = ""
    if request.method == 'POST':
        try:
            requistionNo = request.POST.get('requistionNo')
            myUserID = request.session['User_ID']
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        try:
            response = CLIENT.service.FnRequestInternalRequestApproval(
                myUserID, requistionNo)
            messages.success(request, "Approval Request Sent Successfully")
            print(response)
            return redirect('StoreDetail', pk=pk)
        except Exception as e:
            messages.info(request, e)
            print(e)
            return redirect('StoreDetail', pk=pk)
    return redirect('StoreDetail', pk=pk)


def FnCancelStoreApproval(request, pk):
    requistionNo = ""
    if request.method == 'POST':
        try:
            requistionNo = request.POST.get('requistionNo')
            myUserID = request.session['User_ID']
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        try:
            response = config.CLIENT.service.FnCancelInternalRequestApproval(
                myUserID, requistionNo)
            messages.success(request, "Cancel Approval Successful")
            print(response)
            return redirect('StoreDetail', pk=pk)
        except Exception as e:
            messages.info(request, e)
            print(e)
            return redirect('StoreDetail', pk=pk)
    return redirect('StoreDetail', pk=pk)


def CreateStoreLines(request, pk):
    lineNo = ""
    itemCode = ""
    quantity = ""
    myAction = ''
    if request.method == 'POST':
        try:
            requisitionNo = pk
            lineNo = int(request.POST.get('lineNo'))
            itemCode = request.POST.get('itemCode')
            quantity = int(request.POST.get('quantity'))
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.error(request, "Missing Input")
            return redirect('StoreDetail', pk=pk)
        try:
            response = config.CLIENT.service.FnStoreRequisitionLine(
                requisitionNo, lineNo, itemCode, quantity, myAction)
            messages.success(request, "Request Successful")
            print(response)
            return redirect('StoreDetail', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('StoreDetail', pk=pk)
    return redirect('StoreDetail', pk=pk)

# Delete Store Header

def FnDeleteStoreRequisitionLine(request, pk):
    lineNo = ""
    if request.method == 'POST':
        lineNo = int(request.POST.get('lineNo'))
        requisitionNo = pk
        try:
            response = config.CLIENT.service.FnDeleteStoreRequisitionLine(
                requisitionNo, lineNo)
            messages.success(request, "Successfully Deleted")
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('StoreDetail', pk=pk)
    return redirect('StoreDetail', pk=pk)


def FnGenerateStoreReport(request, pk):
    nameChars = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                        for i in range(5))
    filenameFromApp = ''
    if request.method == 'POST':
        try:
            filenameFromApp = pk + str(nameChars) + ".pdf"
            response = config.CLIENT.service.FnGenerateStoreReport(
                pk, filenameFromApp)
            buffer = BytesIO.BytesIO()
            content = base64.b64decode(response)
            buffer.write(content)
            responses = HttpResponse(
                buffer.getvalue(),
                content_type="application/pdf",
            )
            responses['Content-Disposition'] = f'inline;filename={filenameFromApp}'
            return responses
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('StoreDetail', pk=pk)
    return redirect('StoreDetail', pk=pk)

def UploadStoreAttachment(request, pk):
    response = ""
    fileName = ""
    attachment = ""
    
    if request.method == "POST":
        try:
            attach = request.FILES.getlist('attachment')
            tableID = 52177432
        except Exception as e:
            return redirect('StoreDetail', pk=pk)
        for files in attach:
            fileName = request.FILES['attachment'].name
            attachment = base64.b64encode(files.read())
            try:
                response = config.CLIENT.service.FnUploadAttachedDocument(
                    pk, fileName, attachment, tableID,request.session['User_ID'])
            except Exception as e:
                messages.error(request, e)
                print(e)
        if response == True:
            messages.success(request, "File(s) Uploaded Successfully")
            return redirect('StoreDetail', pk=pk)
        else:
            messages.error(request, "Failed, Try Again.")
            return redirect('StoreDetail', pk=pk)
    return redirect('StoreDetail', pk=pk)
