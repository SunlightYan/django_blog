from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login,logout
from django.http import HttpResponse
from .forms import UserLoginForm, UserReisterForm
from django.contrib.auth.models import User
# 引入验证登入的装饰器
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from .models import Profile
# Create your views here.
# 跟发表文章的表单类类似，Form对象的主要任务就是验证数据。调用is_valid()方法验证并返回指定数据是否有效的布尔值。
#
# Form不仅负责验证数据，还可以“清洗”它：将其标准化为一致的格式，这个特性使得它允许以各种方式输入特定字段的数据，
# 并且始终产生一致的输出。一旦Form使用数据创建了一个实例并对其进行了验证，
# 就可以通过cleaned_data属性访问清洗之后的数据。
#
# authenticate()方法验证用户名称和密码是否匹配，如果是，则将这个用户数据返回。
#
# login()方法实现用户登录，将用户数据保存在session中。
def user_login(request):
    if request.method == "POST":
        user_login_form = UserLoginForm(data=request.POST)
        if user_login_form.is_valid():
            # .cleaned_data 清洗出合法数据
            data = user_login_form.cleaned_data
            # 检验账号，密码是否正确匹配数据库中的某个用户
            # 如果均匹配则返回这个user对象
            user = authenticate(username=data['username'], password=data['password'])
            if user:
                # 将用户数据保存在session中，实现登入动作
                login(request, user)
                return redirect("article:article_list")
            else:
                return HttpResponse("账号或密码输入有误，请重新输入")
        else:
            return HttpResponse("账号或密码输入不合法")
    elif request.method == "GET":
        user_login_form = UserLoginForm()
        context = {'form':user_login_form}
        return render(request,'userprofile/login.html',context)
    else:
        return HttpResponse("请使用GET或POST请求数据")

# 用户退出
def user_logout(request):
    logout(request)
    return redirect("article:article_list")

# 用户注册
def user_register(request):
    if request.method == 'POST':
        user_registration_form = UserReisterForm(data=request.POST)
        if user_registration_form.is_valid():
            new_user = user_registration_form.save(commit=False)
            #设置密码
            new_user.set_password(user_registration_form.cleaned_data['password'])
            new_user.save()
            # 保存好数据后立即登入并返回博客列表页面
            login(request, new_user)
            return redirect("article:article_list")
        else:
            return HttpResponse("注册表单输入有误，请重新输入~")
    elif request.method == 'GET':
        user_registration_form = UserReisterForm()
        context = {'form':user_registration_form}
        return render(request,'userprofile/register.html',context)
    else:
        return HttpResponse("请使用GET和POST请求数据")
# @login_required是一个Python装饰器。
# 装饰器可以在不改变某个函数内容的前提下，给这个函数添加一些功能。
# 具体来说就是@login_required要求调用user_delete()函数时，用户必须登录；
# 如果未登录则不执行函数，将页面重定向到/userprofile/login/地址去。
#
# 装饰器确认用户已经登录后，允许调用user_delete()；
# 然后需要删除的用户id通过请求传递到视图中，由if语句确认是否与登录的用户一致，
# 成功后则退出登录并删除用户数据，返回博客列表页面。
@login_required(login_url='/userprofile/login')
def user_delete(request,id):
    if request.method == 'POST':
        user = User.objects.get(id=id)
        # 验证登入用户，删除用户是否id相同
        if request.user == user:
            # 退出登入删除数据返回博客列表
            logout(request)
            user.delete()
            return redirect("article:article_list")
        else:
            return HttpResponse("你没有删除账户的权限.")
    else:
        return HttpResponse("仅接受POST请求.")

@login_required(login_url='/userprofile/login/')
def profile_edit(request, id):
    user = User.objects.get(id=id)
    # user_id 是 OneToOneField 自动生成的字段
    if Profile.objects.filter(user_id=id).exists():
        profile = Profile.objects.get(user_id=id)
    else:
        profile = Profile.objects.create(user=user)

    if request.method == 'POST':
        # 验证修改数据者，是否为用户本人
        if request.user != user:
            return HttpResponse("你没有权限修改此用户信息。")
        # 上传的文件保存在 request.FILES 中，通过参数传递给表单类
        profile_form = ProfileForm(request.POST,request.FILES)
        if profile_form.is_valid():
            # 取得清洗后的合法数据
            profile_cd = profile_form.cleaned_data
            profile.phone = profile_cd['phone']
            profile.bio = profile_cd['bio']
            if 'avatar' in request.FILES:
                profile.avatar = profile_cd['avatar']
            profile.save()
            # 带参数的 redirect()
            return redirect("userprofile:edit", id=id)
        else:
            return HttpResponse("注册表单输入有误。请重新输入~")

    elif request.method == 'GET':
        profile_form = ProfileForm()
        context = { 'profile_form': profile_form, 'profile': profile, 'user': user }
        return render(request, 'userprofile/edit.html', context)
    else:
        return HttpResponse("请使用GET或POST请求数据")