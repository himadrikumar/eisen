from django.urls import path

from . import views

app_name = 'eisens'
urlpatterns = [
    path('', views.index, name='index'),
    path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    # path('new_page/', views.new_page, name='new_page'),
]
