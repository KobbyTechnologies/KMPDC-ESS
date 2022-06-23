from django.urls import path

from . import views

urlpatterns = [
    path('dashboard/leave/Planner', views.Leave_Planner, name="LeavePlanner"),
    path('CreatePlanner', views.CreatePlanner, name="CreatePlanner"),
    path('PlanDetail/<str:pk>', views.PlanDetail, name='PlanDetail'),
    path('PlannerLine/<str:pk>', views.CreatePlannerLine, name='PlannerLine'),
    path('FnDeleteLeavePlannerLine/<str:pk>',
         views.FnDeleteLeavePlannerLine, name='FnDeleteLeavePlannerLine'),

    path('leave', views.Leave_Request, name="leave"),
    path('CreateLeave', views.CreateLeave, name="CreateLeave"),
    path('leave/detail/<str:pk>', views.LeaveDetail, name='LeaveDetail'),
    path('LeaveApprove/<str:pk>', views.LeaveApproval, name='LeaveApprove'),
    path('LeaveCancel/<str:pk>', views.LeaveCancelApproval, name='LeaveCancel'),
    path('FnGenerateLeave/<str:pk>', views.FnGenerateLeaveReport,
         name='FnGenerateLeaveReport'),
    path('UploadLeaveAttachment/<str:pk>', views.UploadLeaveAttachment,
         name='UploadLeaveAttachment'),


    path('training', views.Training_Request, name='training_request'),
    path('training/detail/<str:pk>', views.TrainingDetail, name='TrainingDetail'),
    path('TrainApprove/<str:pk>', views.TrainingApproval, name='TrainApprove'),
    path('TrainCancel/<str:pk>', views.TrainingCancelApproval, name='TrainCancel'),
    path('TrainingRequest', views.CreateTrainingRequest,
         name='CreateTrainingRequest'),
    path('FnGenerateTraining/<str:pk>', views.FnGenerateTrainingReport,
         name='FnGenerateTrainingReport'),
    path('UploadTrainingAttachment/<str:pk>', views.UploadTrainingAttachment,
         name='UploadTrainingAttachment'),

    path('FnAdhocTraining/<str:pk>', views.FnAdhocTrainingNeedRequest,
         name='FnAdhocTraining'),
    path('FnAdhocEdit/<str:pk>/<str:no>',
         views.FnAdhocTrainingEdit, name='FnAdhocEdit'),
    path('FnAdhocLineDelete/<str:pk>',
         views.FnAdhocLineDelete, name='FnAdhocLineDelete'),
    path('p9', views.PNineRequest, name='pNine'),
    path('payslip', views.PayslipRequest, name='payslip'),
    
    path('disciplinary',views.Disciplinary,name="disciplinary"),
    path('DisciplineDetails/<str:pk>', views.DisciplineDetail,
         name='DisciplineDetail'),
    path('DisciplineResponse/<str:pk>', views.DisciplinaryResponse,
         name='DisciplineResponse'),
]
