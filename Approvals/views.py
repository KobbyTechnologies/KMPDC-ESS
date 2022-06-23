from django.shortcuts import render, redirect
from datetime import date
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import json
from django.conf import settings as config
import datetime as dt
from django.contrib import messages
import io as BytesIO
import base64
from django.http import HttpResponse

# Create your views here.


def Approve(request):
    try:
        fullname = request.session['User_ID']
        year = request.session['years']
        session = requests.Session()
        session.auth = config.AUTHS

        Access_Point = config.O_DATA.format("/QyApprovalEntries")
        try:
            response = session.get(Access_Point, timeout=10).json()
            open = []
            approved = []
            rejected = []
            for approve in response['value']:
                if approve['Status'] == 'Open' and approve['Approver_ID'] == request.session['User_ID']:
                    output_json = json.dumps(approve)
                    open.append(json.loads(output_json))
                if approve['Status'] == 'Approved' and approve['Approver_ID'] == request.session['User_ID']:
                    output_json = json.dumps(approve)
                    approved.append(json.loads(output_json))
                if approve['Status'] == 'Canceled' and approve['Approver_ID'] == request.session['User_ID']:
                    output_json = json.dumps(approve)
                    rejected.append(json.loads(output_json))
            counts = len(open)
            countApproved = len(approved)
            countReject = len(rejected)
        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')

        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
        ctx = {"today": todays_date, "res": open,
            "year": year, "full": fullname,
            "count": counts,"countApproved":countApproved, "approved":approved,
            "countReject":countReject,"reject":rejected}
    except KeyError:
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')       
    return render(request, 'Approve.html', ctx)


def ApproveDetails(request, pk):
    try:
        fullname = request.session['User_ID']
        year = request.session['years']
        session = requests.Session()
        session.auth = config.AUTHS
        res = ''
        Access_Point = config.O_DATA.format("/QyApprovalEntries")
        Access_File = config.O_DATA.format("/QyDocumentAttachments")
        try:
            response = session.get(Access_Point, timeout=10).json()
            Approves = []
            for approve in response['value']:
                if approve['Status'] == 'Open' and approve['Approver_ID'] == request.session['User_ID']:
                    output_json = json.dumps(approve)
                    Approves.append(json.loads(output_json))
                    for claim in Approves:
                        if claim['Document_No_'] == pk:
                            res = claim
                if approve['Status'] == 'Approved' and approve['Approver_ID'] == request.session['User_ID']:
                    output_json = json.dumps(approve)
                    Approves.append(json.loads(output_json))
                    for claim in Approves:
                        if claim['Document_No_'] == pk:
                            res = claim
                if approve['Status'] == 'Canceled' and approve['Approver_ID'] == request.session['User_ID']:
                    output_json = json.dumps(approve)
                    Approves.append(json.loads(output_json))
                    for claim in Approves:
                        if claim['Document_No_'] == pk:
                            res = claim
            allFiles = []
            res_file = session.get(Access_File, timeout=10).json()
            for file in res_file['value']:
                if file['No_'] == pk:
                    output_json = json.dumps(file)
                    allFiles.append(json.loads(output_json))
        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')
        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
        ctx = {"today": todays_date, "res": res, "full": fullname, "year": year,
        "file":allFiles}
    except KeyError:
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')
    return render(request, 'approveDetails.html', ctx)


def All_Approved(request, pk):
    entryNo = ''
    approvalComments = ""
   
    if request.method == 'POST':
        try:
            entryNo = int(request.POST.get('entryNo'))
            myUserID = request.session['User_ID']
            myAction = 'approve'
            documentNo = pk
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        try:
            response = config.CLIENT.service.FnDocumentApproval(
                entryNo, documentNo, myUserID, approvalComments, myAction)
            messages.success(request, "Document Approval successful")
            print(response)
            return redirect('approve')
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('ApproveData', pk=pk)
    return redirect('ApproveData', pk=pk)


def Rejected(request, pk):
    entryNo = ''
    approvalComments = ""
    
    if request.method == 'POST':
        try:
            entryNo = int(request.POST.get('entryNo'))
            approvalComments = request.POST.get('approvalComments')
            myAction = 'reject'
            documentNo = pk
            userID = request.session['User_ID']
        except ValueError:
            messages.error(request, "Missing Input")
            return redirect('ApproveData', pk=pk)
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        try:
            response = config.CLIENT.service.FnDocumentApproval(
                entryNo, documentNo, userID, approvalComments, myAction)
            messages.success(request, "Reject Document Approval successful")
            print(response)
            return redirect('approve')
        except Exception as e:
            messages.info(request, e)
            return redirect('ApproveData', pk=pk)
    return redirect('ApproveData', pk=pk)

def viewDocs(request,pk,id):
    if request.method == 'POST':
        docNo = pk
        attachmentID = int(request.POST.get('attachmentID'))
        File_Name = request.POST.get('File_Name')
        File_Extension = request.POST.get('File_Extension')
        tableID = int(id)
         
        try:
            response = config.CLIENT.service.FnGetDocumentAttachment(
                docNo, attachmentID, tableID)
            
            filenameFromApp = File_Name + "." + File_Extension
            buffer = BytesIO.BytesIO()
            content = base64.b64decode(response)
            buffer.write(content)
            responses = HttpResponse(
                buffer.getvalue(),
                content_type="application/ms-excel",
            )
            responses['Content-Disposition'] = f'inline;filename={filenameFromApp}'
            return responses
        except Exception as e:
            messages.info(request, e)
            return redirect('ApproveData', pk=pk)
    return redirect('ApproveData', pk=pk)