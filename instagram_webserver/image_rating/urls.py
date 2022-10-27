from django.urls import path

from . import views

app_name = 'image_rating'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('new_image/', views.new_image, name='new_image'),
    path('update/', views.update, name='update'),
    path('get_stats/', views.get_stats, name='stats')


]