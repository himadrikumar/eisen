from django.urls import path

from . import views

app_name = 'eisens'
urlpatterns = [
    path('', views.landing_page, name='landing_page'),  # Landing page
    path('app/', views.index, name='index'),
    path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('account/', views.account_details, name='account_details'),
]
