from django.db import models
# 导入内建的USER模型
from django.contrib.auth.models import User
# timezone 处理时间有关函数
from django.utils import timezone
from django.urls import reverse
# Create your models here.
# 博客文章数据类型。参数 author title body created updated
class ArticlePost(models.Model):
    # 文章作者。参数 on_delete 用于指定数据删除的方式
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # 文章标题。models.CharField 为字符串字段，用于保存较短的字符串，比如标题
    title = models.CharField(max_length=100)

    # 文章正文。保存大量文本使用 TextField
    body = models.TextField()

    # 文章创建时间。参数 default=timezone.now 指定其在创建数据时将默认写入当前的时间
    created = models.DateTimeField(default=timezone.now)

    # 文章更新时间。参数 auto_now=True 指定每次数据更新时自动写入当前时间
    updated = models.DateTimeField(auto_now=True)
    # 浏览量
    # PositiveIntegerField是用于存储正整数的字段
    # default=0设定初始值从0开始
    total_views = models.PositiveIntegerField(default=0)
    # 内部类 class Meta 用于给model定义元数据 文章创建时间，负号标识倒序来排列，保证了最新文章永远在最顶部位置
    class Meta:
        #ordering 指定模型返回的数据排列顺序  注意ordering是元组，括号中只含一个元素时不要忘记末尾的逗号
        #-created 倒叙排列
        ordering = ('-created',)
    # 用 _str_ 定义当前调用对象的 s't
    def __str__ (self):
        return self.title

    # 获取文章地址
    def get_absolute_url(self):
        return reverse('article:article_detail', args=[self.id])
