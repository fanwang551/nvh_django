from django.urls import path
from . import views

urlpatterns = [
    # MainRecord
    path('main-records/', views.main_record_list, name='nvh-task-main-list'),
    path('main-records/<int:pk>/', views.main_record_detail, name='nvh-task-main-detail'),

    # TestInfo (通过 main_id 获取/更新)
    path('main-records/<int:main_id>/test-info/', views.test_info_by_main, name='nvh-task-test-info'),
    path('test-infos/<int:pk>/submit/', views.test_info_submit, name='nvh-task-test-info-submit'),
    path('test-infos/<int:pk>/unsubmit/', views.test_info_unsubmit, name='nvh-task-test-info-unsubmit'),

    # DocApproval (通过 main_id 获取/更新)
    path('main-records/<int:main_id>/doc-approval/', views.doc_approval_by_main, name='nvh-task-doc-approval'),
    path('doc-approvals/<int:pk>/submit/', views.doc_approval_submit, name='nvh-task-doc-approval-submit'),
    path('doc-approvals/<int:pk>/unsubmit/', views.doc_approval_unsubmit, name='nvh-task-doc-approval-unsubmit'),

    # EntryExit
    path('entry-exits/', views.entry_exit_list, name='nvh-task-entry-exit-list'),
    path('entry-exits/<int:pk>/', views.entry_exit_detail, name='nvh-task-entry-exit-detail'),
    path('entry-exits/<int:pk>/submit/', views.entry_exit_submit, name='nvh-task-entry-exit-submit'),
    path('entry-exits/<int:pk>/unsubmit/', views.entry_exit_unsubmit, name='nvh-task-entry-exit-unsubmit'),

    # TestProcessAttachment
    path('process-attachments/', views.process_attachment_list, name='nvh-task-attachment-list'),
    path('process-attachments/<int:pk>/', views.process_attachment_detail, name='nvh-task-attachment-detail'),

    # TestProcessList (字典表)
    path('process-list-options/', views.process_list_options, name='nvh-task-process-list-options'),

    # 图片上传
    path('upload/', views.upload_image, name='nvh-task-upload'),
]
