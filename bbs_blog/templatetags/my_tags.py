from django import template
from django.db.models import Count

from bbs_blog import models

register = template.Library()


@register.simple_tag()
def multi_tig(x, y):
    return x * y


@register.inclusion_tag("classification.html")
def get_classification_style(username):
    user = models.UserInfo.objects.filter(username=username).first()
    blog = user.blog
    # 查询每一个分类名称以及对应的文章数
    ret = models.Category.objects.values('pk').annotate(c=Count("article__title")).values("title", "c")

    # 查询当前站点的每一个分类名称以及对应的文章数
    cate_list = models.Category.objects.filter(blog=blog).values('pk').annotate(c=Count("article__title")).values_list(
        "title", "c")

    # 查询当前站点的每一个标签名称以及对应的文章数
    tag_list = models.Tag.objects.filter(blog=blog).values('pk').annotate(c=Count("article__title")).values_list(
        "title", "c")

    # 查询当前站点的每一个年月的名称以及对应的文章数
    # ret = models.Article.objects.extra(select={'is_recent': "create_time > '2022-03-04'"}).values('title', 'is_recent')

    # 方式一：
    date_list = models.Article.objects.filter(user=user).extra(
        select={'y_m_date': "date_format(creat_time, '%%Y-%%m')"}).values('y_m_date').annotate(
        c=Count('nid')).values_list(
        'y_m_date', 'c')

    return {"username":username, "blog": blog, "cate_list": cate_list, "tag_list": tag_list, "date_list": date_list}