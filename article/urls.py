from django.urls import path
from  . import views

# 正在部署的应用的名称
app_name = 'article'

urlpatterns = [
    # 目前还没有urls
    # 将url映射到视图
    path('article-list/', views.article_list, name='article_list'),
    # <int:id>：Django2.0的path新语法用尖括号<>定义需要传递的参数。这里需要传递名叫id的整数到视图函数中去。
    path('article-detail/<int:id>/',views.article_detail,name='article_detail'),
    # 写文章
    path('article-create/', views.article_create, name='article_create'),
    # 删除文章
    path('article-delete/<int:id>/',views.article_delete,name='article_delete'),
    # 安全删除文章
    path('article-safe-delete/<int:id>/',views.article_safe_delete,name='article_safe_delete'),
    # 更新文章
    path('article-update/<int:id>/', views.article_update, name='article_update'),
]

