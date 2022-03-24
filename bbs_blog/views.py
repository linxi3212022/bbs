import json

from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect

from bbs_blog.Myforms import UserForm
from bbs_blog.models import UserInfo
from bbs_blog.utils.validCode import get_valid_code_img
from django.contrib import auth
from bbs_blog import models


def login(request):
    if request.method == "POST":
        response = {"response": None, "msg": None}
        user = request.POST.get("user")
        pwd = request.POST.get("pwd")
        valid_code = request.POST.get("valid_code")
        valid_code_str = request.session.get("valid_code_str")
        if valid_code.upper() == valid_code_str.upper():
            user = auth.authenticate(username=user, password=pwd)
            if user:
                auth.login(request, user)  # request.user== 当前登录对象
                response["user"] = user.username

            else:
                response["msg"] = 'username or password error!'
        else:
            response["msg"] = 'valid code error'
        return JsonResponse(response)
    else:
        return render(request, "login.html")


def index(request):
    article_list = models.Article.objects.all()
    return render(request, "index.html", {'article_list': article_list})


def logout(request):
    auth.logout(request)  # request.session.flush()
    return redirect("/index/")


def get_validCode_img(request):
    data = get_valid_code_img(request)
    return HttpResponse(data)


def register(request):
    response = {"user": None, "msg": None}
    if request.is_ajax():
        form = UserForm(request.POST)
        if form.is_valid():
            response["user"] = form.cleaned_data.get("user")
            # 生成一条用户记录
            user = form.cleaned_data.get("user")
            pwd = form.cleaned_data.get("pwd")
            email = form.cleaned_data.get("email")
            avatar_obj = request.FILES.get("avatar")
            extra = {}
            if avatar_obj:
                extra["avatar"] = avatar_obj
            UserInfo.objects.create_user(username=user, password=pwd, email=email, **extra)

        else:
            # print(form.cleaned_data)
            # print(form.errors)
            response["msg"] = form.errors
        return JsonResponse(response)
    form = UserForm()
    return render(request, "register.html", {"form": form})


def home_site(request, username, **kwargs):
    """
    个人站点视图函数
    :return
    """
    user = UserInfo.objects.filter(username=username).first()
    # 判断用户是否存在
    if not user:
        return render(request, "not_found.html")
    # 当前用户或者当前站点对应的所有文章全取出来
    # 基于对象查询
    # article_list = user.article_set.all()
    # 基于双下划线查询
    article_list = models.Article.objects.filter(user=user)

    # 区分访问的是站点页面还是站点下的跳转页面
    if kwargs:
        condition = kwargs.get("condition")
        param = kwargs.get("param")
        if condition == 'category':
            article_list = article_list.filter(category__title=param)
        elif condition == 'tag':
            article_list = article_list.filter(tags__title=param)
        else:
            year, month = param.split("-")
            article_list = article_list.filter(creat_time__year=year, creat_time__month=month)

    return render(request, "home_site.html", {"article_list": article_list, "username": username})


# 文章详情页
def article_detail(request, username, article_id):
    # context = get_classification_data(username)
    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog
    article_obj = models.Article.objects.filter(pk=article_id).first()
    comment_list = models.Comment.objects.filter(article_id=article_id)
    return render(request, "article_detail.html", locals())


# 点赞视图函数
def digg(request):
    print(request.POST)
    article_id = request.POST.get("article_id")
    is_up = json.loads(request.POST.get("is_up"))

    # 点赞人即当前登陆人
    user_id = request.user.pk
    ard = models.ArticleUpDown.objects.create(user_id=user_id, article_id=article_id, is_up=is_up)
    print(request.user)
    return HttpResponse("OK")


# 评论视图
def comment(request):
    article_id = request.POST.get('article_id')
    pid = request.POST.get('pid')
    content = request.POST.get('content')
    user_id = request.user.pk

    # 生成评论对象
    comment_obj = models.Comment.objects.create(user_id=user_id, article_id=article_id, content=content,
                                                parent_comment_id=pid)

    response = {}
    response['create_time'] = comment_obj.create_time.strftime('%Y-%m-%d %X')
    response["username"] = request.user.username
    response["content"] = content
    return JsonResponse(response)
