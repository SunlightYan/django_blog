from django.shortcuts import render
# 导入HttpRespond模块
from django.http import HttpResponse
from .models import ArticlePost
import markdown
# 引入redirect重定向模块
from django.shortcuts import render, redirect
# 引入刚才定义的ArticlePostForm表单类
from .forms import ArticlePostForm
# 引入User模型
from django.contrib.auth.models import User
# 引入分页模块
from django.core.paginator import Paginator
# 引入Q对象
from django.db.models import Q
from comment.models import Comment
# Create your views here.
# 视图函数  视图函数中的request与网页发来的请求有关，里面包含get或post的内容、用户浏览器、系统等信息。。
def article_list(request):
    # ArticlePost.objects.all() 可以获得所有的对象（即博客文章），并传递给articles变量
    articles_list = ArticlePost.objects.all()
    search = request.GET.get('search')
    order = request.GET.get('order')
    if search:
        if order == 'total_views':
            article_list = ArticlePost.objects.filter(
                Q(title__icontains=search) |
                Q(body__icontains=search)
            ).order_by('-total_views')
        else:
            article_list = ArticlePost.objects.filter(
                Q(title__icontains=search) |
                Q(body__icontains=search)
            )
    else:
        # 将 search 参数重置为空
        # 用户没有搜索操作，
        # 则search = request.GET.get('search')会使得search = None，
        # 而这个值传递到模板中会错误地转换成"None"字符串
        search = ''
        if order == 'total_views':
            article_list = ArticlePost.objects.all().order_by('-total_views')
        else:
            article_list = ArticlePost.objects.all()
    # 每页显示一篇文章
    paginator = Paginator(articles_list,3)
    # 获取url的页码
    page = request.GET.get('page')
    # 将导航对象页面返回给articles
    articles = paginator.get_page(page)
    # context定义了需要传递给模板的上下文，这里即articles
    # context = {'articles':articles}
    context = {'articles':articles, 'order':order,'search':search}
    # 最后返回了render函数。它的作用是结合模板和上下文，并返回渲染后的HttpResponse对象。
    # request  get或post的内容、用户浏览器、系统等信息
    # article/list.html定义了模板文件的位置、名称
    # context定义了需要传入模板文件的上下文
    # 通俗的讲就是把context的内容，加载进模板，并通过浏览器呈现。
    return render(request,'article/list.html',context)
# 文章详细页 id 这是Django自动生成的用于索引数据表的主键（Primary Key，即pk）
def article_detail(request,id):
    # 获取对应id文章
    article = ArticlePost.objects.get(id=id)
    # 取出文章评论
    comments = Comment.objects.filter(article=id)

    article.total_views += 1
    article.save(update_fields=['total_views'])
    # 将markdown语法渲染成html样式
    # markdown.markdown语法接收两个参数：
    # 第一个参数是需要渲染的文章正文article.body；
    # 第二个参数载入了常用的语法扩展：
    # markdown.extensions.extra中包括了缩写、表格等扩展，
    # markdown.extensions.codehilite则是后面要使用的代码高亮扩展。
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
        ]
    )
    article.body = md.convert(article.body)
    # 需要传递给模板的对象
    context = {'article':article,'toc':md.toc,'comments':comments}
    #载入模板返回context对象
    return render(request,'article/detail.html',context)
# 文章编辑页
def article_create(request):
    # 判断用户是否提交数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存数据，但暂时不提交到数据库中
            new_article = article_post_form.save(commit=False)
            # 指定数据库中 id=1 的用户为作者
            # 如果你进行过删除数据表的操作，可能会找不到id=1的用户
            # 此时请重新创建用户，并传入此用户的id
            new_article.author = User.objects.get(id=request.user.id)
            # 将新文章保存到数据库中
            new_article.save()
            # 完成后返回到文章列表
            return redirect("article:article_list")
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 如果用户请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        # 赋值上下文
        context = {'article_post_form': article_post_form}
        # 返回模板
        return render(request, 'article/create.html', context)
# 删除文章
def article_delete(request, id):
    # 根据id获取文章
    article = ArticlePost.objects.get(id=id)
    article.user = User.objects.get(id=request.user.id)
    # 调用delete（）方法
    article.delete()
    # 删除后返回list页面
    return redirect("article:article_list")
#凡是重要的数据操作，都应该考虑带有 csrf 令牌的 POST 请求；或者更简单的方法，数据查询用 GET，数据更改用 POST。
def article_safe_delete(request, id):
    if request.method == 'POST':
        article = ArticlePost.objects.get(id=id)
        if request.user != article.author:
            return HttpResponse("抱歉，你无权修改这篇文章。")
        article.delete()
        return redirect("article:article_list")
    else:
        return HttpResponse("仅允许post请求")

# 更新文章
"""
    更新文章的视图函数
    通过POST方法提交表单，更新titile、body字段
    GET方法进入初始表单页面
    id： 文章的 id
"""
def article_update(request ,id):
    # 获取需要修改的文章数据
    article = ArticlePost.objects.get(id=id)
    # 过滤非作者用户
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章~")
    # 判断用户是否为POST提交表单
    if request.method == "POST":
        # 将提交的数据付给表单实例
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断实例是否满足模型要求
        if article_post_form.is_valid():
            # 保存新写入的title和body
            article.title = request.POST['title']
            article.body = request.POST['body']
            article.save()
            # 完成后返回到修改的文章中，要传入id值
            return redirect("article:article_detail",id=id)
        else:
            # 数据不合法就重写
            return HttpResponse("表单内容有误，请重新填写")
    else:
        # 创建表单实例  为update界面的默认值  传入update界面
        article_post_form = ArticlePostForm()
        context = {'article':article,'article_post_from':article_post_form}
        return render(request, 'article/update.html',context)



