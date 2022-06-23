import base64
import imp
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
import string
from django.http import HttpResponse
import io as BytesIO
from django.template.response import TemplateResponse


# Create your views here.


def ImprestRequisition(request):
    try:
        fullname =  request.session['User_ID']
        year = request.session['years']
        session = requests.Session()
        session.auth = config.AUTHS

        Access_Point = config.O_DATA.format("/Imprests")
        try:
            response = session.get(Access_Point, timeout=10).json()
            open = []
            Approved = []
            Rejected = []
            Pending = []
            for imprest in response['value']:
                if imprest['Status'] == 'Open' and imprest['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    open.append(json.loads(output_json))
                if imprest['Status'] == 'Released' and imprest['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    Approved.append(json.loads(output_json))
                if imprest['Status'] == 'Rejected' and imprest['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    Rejected.append(json.loads(output_json))
                if imprest['Status'] == 'Pending Approval' and imprest['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    Pending.append(json.loads(output_json))
            counts = len(open)

            pend = len(Pending)

            counter = len(Approved)

            reject = len(Rejected)

        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')

        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")

        ctx = {"today": todays_date, "res": open,
            "count": counts, "response": Approved,
            "counter": counter, "reject": Rejected,
            "rej": reject, "pend": pend,
            "pending": Pending, "year": year,
            "full": fullname}
    except KeyError:
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')
    return render(request, 'imprestReq.html', ctx)


def CreateImprest(request):
    session = requests.Session()
    session.auth = config.AUTHS
    imprestNo = ""
    purpose = ''
    isImprest = ''
    isDsa = ''
    myAction = ''
    if request.method == 'POST':
        try:
            accountNo = request.session['Customer_No_']
            responsibilityCenter = request.session['User_Responsibility_Center']
            usersId = request.session['User_ID']
            personalNo = request.session['Employee_No_']
            imprestNo = request.POST.get('imprestNo')
            travelType = int(request.POST.get('travelType'))
            purpose = request.POST.get('purpose')
            isImprest = eval(request.POST.get('isImprest'))
            isDsa = eval(request.POST.get('isDsa'))
            myAction = request.POST.get('myAction')
            imprestNo = request.POST.get('imprestNo')
        except ValueError:
            messages.error(request, "Missing Input")
            return redirect('imprestReq')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        if not imprestNo:
            imprestNo = " "
        try:
            response = config.CLIENT.service.FnImprestHeader(
                imprestNo, accountNo, responsibilityCenter, travelType, purpose, usersId, personalNo, isImprest, isDsa, myAction)
            messages.success(request, "Request Successful")
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('imprestReq')
    return redirect('imprestReq')


def ImprestDetails(request, pk):
    try:
        fullname = request.session['User_ID']
        year = request.session['years']

        session = requests.Session()
        session.auth = config.AUTHS
        state = ''
        res = ''
        Access_Point = config.O_DATA.format("/Imprests")
        Imprest_Type = config.O_DATA.format("/QyReceiptsAndPaymentTypes")
        Dimension = config.O_DATA.format("/QyDimensionValues")
        destination = config.O_DATA.format("/QyDestinations")
        Approver = config.O_DATA.format("/QyApprovalEntries")
        Lines_Res = config.O_DATA.format("/QyImprestLines")
        try:
            response = session.get(Access_Point, timeout=10).json()
            Imprest_RES = session.get(Imprest_Type, timeout=10).json()
            Dimension_RES = session.get(Dimension, timeout=10).json()
            res_dest = session.get(destination, timeout=10).json()
            res_approver = session.get(Approver, timeout=10).json()
            responses = session.get(Lines_Res, timeout=10).json()
            openLines = []

            openImp = []
            res_type = []
            Area = []
            BizGroup = []
            Approvers = []
            Pending = []
            Local = []
            ForegnDest = []
            for dest in res_dest['value']:
                if dest['Destination_Type'] == "Local":
                    output_json = json.dumps(dest)
                    Local.append(json.loads(output_json))
                if dest['Destination_Type'] == "Foreign":
                    output_json = json.dumps(dest)
                    ForegnDest.append(json.loads(output_json))
            for approver in res_approver['value']:
                if approver['Document_No_'] == pk:
                    output_json = json.dumps(approver)
                    Approvers.append(json.loads(output_json))
            for types in Dimension_RES['value']:
                if types['Global_Dimension_No_'] == 1:
                    output_json = json.dumps(types)
                    Area.append(json.loads(output_json))
                if types['Global_Dimension_No_'] == 2:
                    output_json = json.dumps(types)
                    BizGroup.append(json.loads(output_json))
            for types in Imprest_RES['value']:
                if types['Type'] == "Imprest":
                    output_json = json.dumps(types)
                    res_type.append(json.loads(output_json))
            for imprest in response['value']:
                if imprest['Status'] == 'Released' and imprest['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    openImp.append(json.loads(output_json))
                    for imprest in openImp:
                        if imprest['No_'] == pk:
                            res = imprest
                            if imprest['Status'] == 'Released':
                                state = 3
                if imprest['Status'] == 'Open' and imprest['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    openImp.append(json.loads(output_json))
                    for imprest in openImp:
                        if imprest['No_'] == pk:
                            res = imprest
                            if imprest['Status'] == 'Open':
                                state = 1
                            if imprest['Travel_Type'] == 'Local':
                                destination = "Local"
                            if imprest['Travel_Type'] == 'Foreign':
                                destination = "Foreign"
                if imprest['Status'] == 'Rejected' and imprest['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    openImp.append(json.loads(output_json))
                    for imprest in openImp:
                        if imprest['No_'] == pk:
                            res = imprest
                if imprest['Status'] == "Pending Approval" and imprest['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    Pending.append(json.loads(output_json))
                    for imprest in Pending:
                        if imprest['No_'] == pk:
                            res = imprest
                            if imprest['Status'] == 'Pending Approval':
                                state = 2
            for imprest in responses['value']:
                if imprest['AuxiliaryIndex1'] == pk:
                    output_json = json.dumps(imprest)
                    openLines.append(json.loads(output_json))
        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, "Whoops! Something went wrong. Please Login to Continue")
            return redirect('imprestReq')
        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
                    
        print(ForegnDest)
        ctx = {"today": todays_date, "res": res,
            "line": openLines, "state": state,
            "Approvers": Approvers, "type": res_type,
            "area": Area, "biz": BizGroup,
            "Local": Local, "year": year,
            "full": fullname, "Foreign": ForegnDest, "dest": destination}
    except KeyError as e:
        print(e)
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')
    return render(request, 'imprestDetail.html', ctx)


def UploadAttachment(request, pk):
    if request.method == "POST":
        try:
            attach = request.FILES.getlist('attachment')
            tableID = 52177430
        except Exception as e:
            return redirect('IMPDetails', pk=pk)
        for files in attach:
            fileName = request.FILES['attachment'].name
            attachment = base64.b64encode(files.read())
            try:
                response = config.CLIENT.service.FnUploadAttachedDocument(
                    pk, fileName, attachment, tableID)
            except Exception as e:
                messages.error(request, e)
                print(e)
        if response == True:
            messages.success(request, "File(s) Upload Successful")
            return redirect('IMPDetails', pk=pk)
        else:
            messages.error(request, "Failed, Try Again")
            return redirect('IMPDetails', pk=pk)
    return redirect('IMPDetails', pk=pk)

# Delete Imprest Header

def FnDeleteImprestLine(request, pk):
    if request.method == 'POST':
        try:
            lineNo = int(request.POST.get('lineNo'))
        except ValueError as e:
            return redirect('IMPDetails', pk=pk)

        try:
            response = config.CLIENT.service.FnDeleteImprestLine(
                lineNo, pk)
            messages.success(request, "Approval Request Sent Successfully")
            print(response)
            return redirect('IMPDetails', pk=pk)
        except Exception as e:
            messages.info(request, e)
            print(e)
            return redirect('IMPDetails', pk=pk)
    return redirect('IMPDetails', pk=pk)


def FnGenerateImprestReport(request, pk):
    nameChars = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                        for i in range(5))
    if request.method == 'POST':

        filenameFromApp = pk + str(nameChars) + ".pdf"
        try:
            response = config.CLIENT.service.FnGenerateImprestReport(
                request.session['Employee_No_'], filenameFromApp, pk)
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
            return redirect('auth')
    return redirect('IMPDetails', pk=pk)


def FnRequestPaymentApproval(request, pk):

    if request.method == 'POST':
        try:
            requisitionNo = request.POST.get('requisitionNo')
        except ValueError as e:
            return redirect('IMPDetails', pk=pk)
        try:
            response = config.CLIENT.service.FnRequestPaymentApproval(
                request.session['Employee_No_'], requisitionNo)
            messages.success(request, "Approval Request Sent Successfully")
            print(response)
            return redirect('IMPDetails', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('auth')
    return redirect('IMPDetails', pk=pk)


def FnCancelPaymentApproval(request, pk):
    if request.method == 'POST':
        try:
            requisitionNo = request.POST.get('requisitionNo')
        except ValueError as e:
            return redirect('IMPDetails', pk=pk)
        try:
            response = config.CLIENT.service.FnCancelPaymentApproval(
                request.session['Employee_No_'], requisitionNo)
            messages.success(request, "Cancel Approval Successful")
            print(response)
            return redirect('IMPDetails', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('auth')
    return redirect('IMPDetails', pk=pk)


def CreateImprestLines(request, pk):
    if request.method == 'POST':
        try:
            lineNo = int(request.POST.get('lineNo'))
            destination = request.POST.get('destination')
            imprestTypes = request.POST.get('imprestType')
            requisitionType = request.POST.get('requisitionType')
            travelDate = datetime.strptime(
                request.POST.get('travel'), '%Y-%m-%d').date()
            amount = request.POST.get("amount")
            returnDate = datetime.strptime(
                request.POST.get('returnDate'), '%Y-%m-%d').date()
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.error(request, "Missing Input")
            return redirect('IMPDetails', pk=pk)

        class Data(enum.Enum):
            values = imprestTypes
        imprestType = (Data.values).value

        if not amount:
            amount = 0
        try:
            response = config.CLIENT.service.FnImprestLine(
                lineNo, pk, imprestType, destination, travelDate, returnDate, requisitionType, float(amount), myAction)
            messages.success(request, "Request Successful")
            print(response)
            return redirect('IMPDetails', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('IMPDetails', pk=pk)
    return redirect('IMPDetails', pk=pk)


def ImprestSurrender(request):
    try:
        fullname = request.session['User_ID']
        year = request.session['years']
        session = requests.Session()
        session.auth = config.AUTHS

        Access_Point = config.O_DATA.format("/QyImprestSurrenders")
        Released_imprest = config.O_DATA.format("/Imprests")
        try:
            response = session.get(Access_Point, timeout=10).json()
            Released = session.get(Released_imprest, timeout=10).json()
            open = []
            Approved = []
            Reject = []
            APPImp = []
            Pending = []
            for imprest in response['value']:
                if imprest['Status'] == 'Open' and imprest['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    open.append(json.loads(output_json))
                if imprest['Status'] == 'Released' and imprest['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    Approved.append(json.loads(output_json))
                if imprest['Status'] == 'Rejected' and imprest['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    Reject.append(json.loads(output_json))
                if imprest['Status'] == 'Pending Approval' and imprest['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    Pending.append(json.loads(output_json))
            for imprest in Released['value']:
                if imprest['Status'] == 'Released' and imprest['User_Id'] == request.session['User_ID'] and imprest['DSA'] == False and imprest['Surrendered'] == False and imprest['Posted'] == True:
                    output_json = json.dumps(imprest)
                    APPImp.append(json.loads(output_json))
            
            counts = len(open)

            counter = len(Approved)

            Rejects = len(Reject)

            pend = len(Pending)
        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')

        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
        ctx = {"today": todays_date, "res": open,
            "count": counts, "full": fullname,
            "response": Approved, "counter": counter,
            "reject": Rejects, "rej": Reject,
            "app": APPImp, "year": year,
            "pend": pend, "pending": Pending}
    except KeyError:
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')
    return render(request, 'imprestSurr.html', ctx)


def CreateSurrender(request):
    if request.method == 'POST':
        try:
            usersId = request.session['User_ID']
            staffNo = request.session['Employee_No_']
            accountNo = request.session['Customer_No_']
            surrenderNo = request.POST.get('surrenderNo')
            imprestIssueDocNo = request.POST.get('imprestIssueDocNo')
            purpose = request.POST.get('purpose')
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.error(request, "Missing Input")
            return redirect('imprestSurr')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        if not surrenderNo:
            surrenderNo = " "
        try:
            response = config.CLIENT.service.FnImprestSurrenderHeader(
                surrenderNo, imprestIssueDocNo, accountNo, purpose, usersId, staffNo, myAction)
            messages.success(request, "Request Successful")
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('imprestSurr')
    return redirect('imprestSurr')


def SurrenderDetails(request, pk):
    try:
        fullname = request.session['User_ID']
        year = request.session['years']
        session = requests.Session()
        session.auth = config.AUTHS
        state = ''
        res = ''
        Imprest_Issue_Doc__No = ""
        Access_Point = config.O_DATA.format("/QyImprestSurrenders")
        Imprest_Type = config.O_DATA.format("/QyReceiptsAndPaymentTypes")
        Approver = config.O_DATA.format("/QyApprovalEntries")
        try:
            response = session.get(Access_Point, timeout=10).json()
            Imprest_RES = session.get(Imprest_Type, timeout=10).json()
            res_approver = session.get(Approver, timeout=10).json()
            openImp = []
            res_type = []
            Approvers = []
            Pending = []
            for approver in res_approver['value']:
                if approver['Document_No_'] == pk:
                    output_json = json.dumps(approver)
                    Approvers.append(json.loads(output_json))
            for types in Imprest_RES['value']:
                if types['Type'] == "Imprest":
                    output_json = json.dumps(types)
                    res_type.append(json.loads(output_json))
            for imprest in response['value']:
                if imprest['Status'] == 'Released' and imprest['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    openImp.append(json.loads(output_json))
                    for imprest in openImp:
                        if imprest['No_'] == pk:
                            request.session['Imprest_Issue_Doc__No'] = imprest['Imprest_Issue_Doc__No']
                            Imprest_Issue_Doc__No = request.session['Imprest_Issue_Doc__No']
                            res = imprest
                            if imprest['Status'] == 'Released':
                                state = 3
                if imprest['Status'] == 'Open' and imprest['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    openImp.append(json.loads(output_json))
                    for imprest in openImp:
                        if imprest['No_'] == pk:
                            request.session['Imprest_Issue_Doc__No'] = imprest['Imprest_Issue_Doc__No']
                            Imprest_Issue_Doc__No = request.session['Imprest_Issue_Doc__No']
                            res = imprest
                            if imprest['Status'] == 'Open':
                                state = 1
                if imprest['Status'] == 'Rejected' and imprest['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    openImp.append(json.loads(output_json))
                    for imprest in openImp:
                        if imprest['No_'] == pk:
                            request.session['Imprest_Issue_Doc__No'] = imprest['Imprest_Issue_Doc__No']
                            Imprest_Issue_Doc__No = request.session['Imprest_Issue_Doc__No']
                            res = imprest
                if imprest['Status'] == "Pending Approval" and imprest['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    Pending.append(json.loads(output_json))
                    for imprest in Pending:
                        if imprest['No_'] == pk:
                            request.session['Imprest_Issue_Doc__No'] = imprest['Imprest_Issue_Doc__No']
                            Imprest_Issue_Doc__No = request.session['Imprest_Issue_Doc__No']
                            res = imprest
                            if imprest['Status'] == 'Pending Approval':
                                state = 2
        except requests.exceptions.ConnectionError as e:
            print(e)
        Lines_Res = config.O_DATA.format("/QyImprestSurrenderLines")
        try:
            ress = session.get(Lines_Res, timeout=10).json()
            openLines = []
            for imprest in ress['value']:
                if imprest['No'] == pk:
                    output_json = json.dumps(imprest)
                    openLines.append(json.loads(output_json))
        except requests.exceptions.ConnectionError as e:
            print(e)
        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
        ctx = {"today": todays_date, "res": res,
            "state": state, "line": openLines,
            "Approvers": Approvers, "type": res_type,
            "year": year, "full": fullname}
    except KeyError:
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')
    return render(request, 'SurrenderDetail.html', ctx)


def CreateSurrenderLines(request, pk):
    if request.method == 'POST':
        try:
            lineNo = int(request.POST.get('lineNo'))
            actualSpent = float(request.POST.get('actualSpent'))
        except ValueError:
            messages.error(request, "Missing Input")
            return redirect('IMPDetails', pk=pk)
        try:
            response = config.CLIENT.service.FnImprestSurrenderLine(
                lineNo, pk, actualSpent)
            messages.success(request, "Request Successful")
            print(response)
            return redirect('IMPSurrender', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('IMPSurrender', pk=pk)
    return redirect('IMPSurrender', pk=pk)


def UploadSurrenderAttachment(request, pk):
    if request.method == "POST":
        try:
            tableID = 52177430
            attach = request.FILES.getlist('attachment')
        except Exception as e:
            return redirect('IMPSurrender', pk=pk)
        for files in attach:
            fileName = request.FILES['attachment'].name
            attachment = base64.b64encode(files.read())
            try:
                response = config.CLIENT.service.FnUploadAttachedDocument(
                    pk, fileName, attachment, tableID)
            except Exception as e:
                messages.error(request, e)
                print(e)
        if response == True:
            messages.success(request, "File(s) Upload Successful")
            return redirect('IMPSurrender', pk=pk)
        else:
            messages.error(request, "Failed, Try Again")
            return redirect('IMPSurrender', pk=pk)
    return redirect('IMPSurrender', pk=pk)


def FnGenerateImprestSurrenderReport(request, pk):
    nameChars = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                        for i in range(5))
    if request.method == 'POST':
        filenameFromApp = pk + str(nameChars) + ".pdf"
        try:
            response = config.CLIENT.service.FnGenerateImprestSurrenderReport(
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
            return redirect('IMPSurrender', pk=pk)
    return redirect('IMPSurrender', pk=pk)


def SurrenderApproval(request, pk):
    if request.method == 'POST':
        try:
            requisitionNo = request.POST.get('requisitionNo')
        except ValueError as e:
            return redirect('IMPSurrender', pk=pk)
        try:
            response = config.CLIENT.service.FnRequestPaymentApproval(
                request.session['Employee_No_'], requisitionNo)
            messages.success(request, "Approval Request Sent Successfully")
            print(response)
            return redirect('IMPSurrender', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('IMPSurrender', pk=pk)


def FnCancelSurrenderApproval(request, pk):
    if request.method == 'POST':
        try:
            requisitionNo = request.POST.get('requisitionNo')
        except ValueError as e:
            return redirect('IMPSurrender', pk=pk)
        try:
            response = config.CLIENT.service.FnCancelPaymentApproval(
                request.session['Employee_No_'], requisitionNo)
            messages.success(request, "Cancel Approval Successful !!")
            print(response)
            return redirect('IMPSurrender', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('IMPSurrender', pk=pk)


def StaffClaim(request):
    try:
        fullname = request.session['User_ID']
        year = request.session['years']

        session = requests.Session()
        session.auth = config.AUTHS

        Access_Point = config.O_DATA.format("/QyStaffClaims")
        Claim = config.O_DATA.format("/QyImprestSurrenders")
        try:
            response = session.get(Access_Point, timeout=10).json()
            res_claim = session.get(Claim, timeout=10).json()
            open = []
            Approved = []
            Rejected = []
            My_Claim = []
            Pending = []

            for imprest in res_claim['value']:
                if imprest['Actual_Amount_Spent'] > imprest['Imprest_Amount']:
                    output_json = json.dumps(imprest)
                    My_Claim.append(json.loads(output_json))
            for imprest in response['value']:
                if imprest['Status'] == 'Open' and imprest['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    open.append(json.loads(output_json))
                if imprest['Status'] == 'Released' and imprest['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    Approved.append(json.loads(output_json))
                if imprest['Status'] == 'Rejected' and imprest['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    Rejected.append(json.loads(output_json))
                if imprest['Status'] == 'Pending Approval' and imprest['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(imprest)
                    Pending.append(json.loads(output_json))
            counts = len(open)

            counter = len(Approved)
            rej = len(Rejected)
            pend = len(Pending)
        except requests.exceptions.ConnectionError as e:
            print(e)
            messages.info(request,e)
            return redirect('auth')
        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
        ctx = {"today": todays_date, "res": open,
            "count": counts, "rej": rej,
            "response": Approved, "claim": counter,
            'reject': Rejected, "my_claim": My_Claim,
            "pend": pend,
            "year": year, "pending": Pending,
            "full": fullname}
    except KeyError:
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')
    return render(request, 'staffClaim.html', ctx)


def CreateClaim(request):
    claimNo = ""
    claimType = ""
    accountNo = request.session['Customer_No_']
    purpose = ''
    usersId = request.session['User_ID']
    staffNo = request.session['Employee_No_']
    imprestSurrDocNo = ''
    myAction = ''
    if request.method == 'POST':
        claimNo = request.POST.get('claimNo')
        claimType = int(request.POST.get('claimType'))
        imprestSurrDocNo = request.POST.get('imprestSurrDocNo')
        purpose = request.POST.get('purpose')
        myAction = request.POST.get('myAction')
        if not claimNo:
            claimNo = " "
        if not imprestSurrDocNo:
            imprestSurrDocNo = " "
        try:
            response = config.CLIENT.service.FnStaffClaimHeader(
                claimNo, claimType, accountNo, purpose, usersId, staffNo, imprestSurrDocNo, myAction)
            messages.success(request, "Request Successful")
            print(response)
            return redirect('claim')
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('claim')


def ClaimDetails(request, pk):
    try:
        fullname = request.session['User_ID']
        year = request.session['years']

        session = requests.Session()
        session.auth = config.AUTHS
        state = ''
        res = ''
        Access_Point = config.O_DATA.format("/QyStaffClaims")
        Claim_Type = config.O_DATA.format("/QyReceiptsAndPaymentTypes")
        Approver = config.O_DATA.format("/QyApprovalEntries")
        try:
            response = session.get(Access_Point, timeout=10).json()
            Claim_RES = session.get(Claim_Type, timeout=10).json()
            res_approver = session.get(Approver, timeout=10).json()
            openClaim = []
            res_type = []
            Approvers = []
            Pending = []
            for approver in res_approver['value']:
                if approver['Document_No_'] == pk:
                    output_json = json.dumps(approver)
                    Approvers.append(json.loads(output_json))
            for types in Claim_RES['value']:
                if types['Type'] == "Claim":
                    output_json = json.dumps(types)
                    res_type.append(json.loads(output_json))
            for claim in response['value']:
                if claim['Status'] == 'Released' and claim['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(claim)
                    openClaim.append(json.loads(output_json))
                    for claim in openClaim:
                        if claim['No_'] == pk:
                            res = claim
                            if claim['Status'] == 'Released':
                                state = 3
                if claim['Status'] == 'Open' and claim['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(claim)
                    openClaim.append(json.loads(output_json))
                    for claim in openClaim:
                        if claim['No_'] == pk:
                            res = claim
                            if claim['Status'] == 'Open':
                                state = 1
                if claim['Status'] == 'Rejected' and claim['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(claim)
                    openClaim.append(json.loads(output_json))
                    for claim in openClaim:
                        if claim['No_'] == pk:
                            res = claim
                if claim['Status'] == "Pending Approval" and claim['User_Id'] == request.session['User_ID']:
                    output_json = json.dumps(claim)
                    Pending.append(json.loads(output_json))
                    for claim in Pending:
                        if claim['No_'] == pk:
                            res = claim
                            if claim['Status'] == 'Pending Approval':
                                state = 2
        except requests.exceptions.ConnectionError as e:
            print(e)
        Lines_Res = config.O_DATA.format("/QyStaffClaimLines")
        try:
            res_Line = session.get(Lines_Res, timeout=10).json()
            openLines = []
            for claim in res_Line['value']:
                if claim['No'] == pk:
                    output_json = json.dumps(claim)
                    openLines.append(json.loads(output_json))
        except requests.exceptions.ConnectionError as e:
            print(e)

        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
        ctx = {"today": todays_date, "res": res,
            "state": state, "res_type": res_type,
            "Approvers": Approvers, "line": openLines,
            "year": year, "full": fullname}
    except KeyError:
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')
    return render(request, "ClaimDetail.html", ctx)


def CreateClaimLines(request, pk):
    lineNo = ""
    claimNo = pk
    claimType = ""
    
    amount = ""
    claimReceiptNo = ""
    dimension3 = ''
    expenditureDate = ""
    expenditureDescription = ""
    myAction = ''
    if request.method == 'POST':
        try:
            accountNo = request.session['Customer_No_']
            lineNo = int(request.POST.get('lineNo'))
            claimType = request.POST.get('claimType')
            amount = float(request.POST.get('amount'))
            expenditureDate = datetime.strptime(
                request.POST.get('expenditureDate'), '%Y-%m-%d').date()
            expenditureDescription = request.POST.get('expenditureDescription')
            attach = request.FILES.getlist('attachment')
            myAction = request.POST.get('myAction')
            tableID = 52177431
        except Exception as e:
            messages.error(request, "Invalid Input.")
            return redirect('ClaimDetail', pk=pk)

        try:
            response = config.CLIENT.service.FnStaffClaimLine(
                lineNo, claimNo, claimType, accountNo, amount, claimReceiptNo, dimension3, expenditureDate, expenditureDescription, myAction)
            print(response)
            if response != 0:
                for files in attach:
                    fileName = request.FILES['attachment'].name
                    attachment = base64.b64encode(files.read())
                    try:
                        responses = config.CLIENT.service.FnUploadAttachedDocument(
                            pk +'#'+str(response), fileName, attachment, tableID)
                        if responses == True:
                            messages.success(request, "Request Successful")
                            return redirect('ClaimDetail', pk=pk)
                        else:
                            messages.error(request, "Failed, Try Again")
                            return redirect('ClaimDetail', pk=pk)
                    except Exception as e:
                        messages.error(request, e)
                        print(e)

        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('ClaimDetail', pk=pk)


def ClaimApproval(request, pk):
    if request.method == 'POST':
        try:
            requisitionNo = request.POST.get('requisitionNo')
        except ValueError as e:
            return redirect('ClaimDetail', pk=pk)
        try:
            response = config.CLIENT.service.FnRequestPaymentApproval(
                request.session['Employee_No_'], requisitionNo)
            messages.success(request, "Approval Request Sent Successfully")
            print(response)
            return redirect('ClaimDetail', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('ClaimDetail', pk=pk)

def FnCancelClaimApproval(request, pk):
    if request.method == 'POST':
        try:
            requisitionNo = request.POST.get('requisitionNo')
        except ValueError as e:
            return redirect('ClaimDetail', pk=pk)
        try:
            response = config.CLIENT.service.FnCancelPaymentApproval(
                request.session['Employee_No_'], requisitionNo)
            messages.success(request, "Cancel Approval Successful !!")
            print(response)
            return redirect('ClaimDetail', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('ClaimDetail', pk=pk)

def FnDeleteStaffClaimLine(request, pk):
    if request.method == 'POST':
        lineNo = int(request.POST.get('lineNo'))
        try:
            response = config.CLIENT.service.FnDeleteStaffClaimLine(lineNo,
                                                                    pk)
            messages.success(request, "Successfully Deleted")
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('ClaimDetail', pk=pk)


def FnGenerateStaffClaimReport(request, pk):
    nameChars = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                        for i in range(5))
    if request.method == 'POST':
        filenameFromApp = pk + str(nameChars) + ".pdf"
        try:
            response = config.CLIENT.service.FnGenerateStaffClaimReport(
                request.session['Employee_No_'], filenameFromApp, pk)
            messages.success(request, "Successfully Sent!!")
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
    return redirect('ClaimDetail', pk=pk)
