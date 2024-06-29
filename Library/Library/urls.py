"""Library URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myWEB import views

urlpatterns = [
    path('', views.home),
    path('admin/', admin.site.urls),

    path('login_view/', views.login_view, name='login_view'),  # 登录
    path('register/', views.register),  # 注册
    path('logout_view/', views.logout_view),  # 退出登录

    path('dz_index/', views.dz_index),  # 读者首页
    path('current_borrows/', views.current_borrows_view, name='current_borrows'), #当前借阅
    path('dz_smztcx/', views.dz_smztcx),  # 读者书目状态查询
    path('dz_js/', views.dz_js),  # 读者借书
    path('dz_hs/', views.dz_hs),  # 读者还书

    path('gly_index/', views.gly_index),  # 管理员首页
    path('gly_smztcx/', views.gly_smztcx),  # 读者书目状态查询
    path('smzt_all/', views.smzt_all),  # 所有书目状态
    path('borrowed_books/', views.borrowed_books),  # 所有书目状态
    path('gly_rk/', views.gly_rk),  # 管理员入库
    path('gly_ck/', views.gly_ck),  # 管理员出库
    path('book_count/', views.book_count_view, name='book_count'),#书籍被借次数统计
    path('reader_count/', views.reader_count_view, name='reader_count'),#读者借书数量统计
]
