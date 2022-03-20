from django.contrib import admin
from django.urls import path, re_path
from bbs_blog import views
from django.views.static import serve

from pythonlxBBS import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login),
    path('logout/', views.logout),
    path('index/', views.index),
    re_path('^$', views.index),
    path('get_validCode_img/', views.get_validCode_img),
    path('register/', views.register),
    path('digg/', views.digg),

    # media配置
    re_path(r"media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),

    # 文章
    re_path("^(?P<username>\w+)/articles/(?P<article_id>\d+)$", views.article_detail),

    # 个人站点的跳转
    re_path("^(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<param>.*)/$", views.home_site),

    # 个人站点url
    re_path("^(?P<username>\w+)$", views.home_site),
]
