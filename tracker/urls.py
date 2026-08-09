from django.urls import path
from . import views

urlpatterns = [
    # Healthcheck
    path('healthz/', views.healthz, name='healthz'),

    # Project views
    path('', views.project_list, name='project_list'),
    path('projects/<int:project_id>/', views.project_board, name='project_board'),

    # Issue views
    path('projects/<int:project_id>/issues/create/', views.create_issue, name='create_issue'),
    path('issues/<int:issue_id>/', views.issue_detail, name='issue_detail'),
    path('issues/<int:issue_id>/update-status/', views.update_issue_status, name='update_issue_status'),

    # Comment views
    path('issues/<int:issue_id>/comments/add/', views.add_comment, name='add_comment'),
]
