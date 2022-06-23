from django.urls import path
from . import views


urlpatterns = [
    path('imprest/requisition', views.ImprestRequisition, name='imprestReq'),
    path('CreateImp', views.CreateImprest, name='create'),
    path('CreateImpLines/<str:pk>',
         views.CreateImprestLines, name='CreateImpLines'),
    path('FnDeleteImprestLine/<str:pk>',
         views.FnDeleteImprestLine, name='FnDeleteImprestLine'),
    path('Impres/<str:pk>', views.FnRequestPaymentApproval, name='Impres'),
    path('FnGenerateImprestReport/<str:pk>',
         views.FnGenerateImprestReport, name='FnGenerateImprestReport'),
    path('ImpresCancel/<str:pk>', views.FnCancelPaymentApproval, name='ImpresCancel'),
    path('Imp/<str:pk>', views.ImprestDetails, name='IMPDetails'),
    path('UploadAttachment/<str:pk>',
         views.UploadAttachment, name='UploadAttachment'),


    path('ImprestSurrender', views.ImprestSurrender, name='imprestSurr'),
    path('CreateSurrender', views.CreateSurrender, name="CreateSurrender"),
    path('ImpSurrender/<str:pk>',
         views.SurrenderDetails, name='IMPSurrender'),
    path('SurrenderApprove/<str:pk>',
         views.SurrenderApproval, name='SurrenderApprove'),
    path('ImpSurrenderLines/<str:pk>',
         views.CreateSurrenderLines, name='CreateSurrenderLines'),
    path('CancelSurrenderApproval/<str:pk>',
         views.FnCancelSurrenderApproval, name='CancelSurrenderApproval'),
    path('UploadSurrenderAttachment/<str:pk>',
         views.UploadSurrenderAttachment, name='UploadSurrenderAttachment'),
    path('FnGenerateImprestSurrenderReport/<str:pk>',
         views.FnGenerateImprestSurrenderReport, name='FnGenerateImprestSurrenderReport'),

    path('StaffClaim', views.StaffClaim, name='claim'),
    path("NewClaim", views.CreateClaim, name="NewClaim"),
    path('Claim/<str:pk>', views.ClaimDetails, name='ClaimDetail'),
    path('ClaimLines/<str:pk>', views.CreateClaimLines, name='ClaimLines'),
    path('ClaimApprove/<str:pk>', views.ClaimApproval, name='ClaimApprove'),
    path('ClaimCancel/<str:pk>', views.FnCancelClaimApproval, name='ClaimCancel'),
    path('FnDeleteStaffClaimLine/<str:pk>', views.FnDeleteStaffClaimLine,
         name='FnDeleteStaffClaimLine'),
    path('FnGenerateStaffClaimReport/<str:pk>', views.FnGenerateStaffClaimReport,
         name='FnGenerateStaffClaimReport'),

]
