from django.urls import path,include
from api.views import  *


# router.register(r'list',ListViewSet)
# router.register(r'tasks',TaskViewSet)

app_name = 'api'
urlpatterns = [
    path('login',login),
    path('signup',signup),
    path('logout',logout),
    path('create_list',create_list),
    path('get_list',get_list),
    path('get_task',get_task,name='get_task'),
    path('get_task_by_id/<id>',get_task_by_id),
    path('create_task',create_task),
    path('partial_update_task/<id>',partial_update_task),
    path('update_task/<id>',update_task),
    path('delete_task/<id>',delete_task),
    path('get_performance',get_performance)


]
