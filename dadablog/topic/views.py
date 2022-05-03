import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from tools.logging_dec import logging_check, get_user_by_request
from topic.models import Topic
from user.models import UserProfile


# 异常码 10300-10399
# Create your views here.


class TopicViews(View):

    def make_topic_res(self, author, author_topic, is_self):

        if is_self:
            # 博主访问自己
            next_topic = Topic.objects.filter(id__gt=author_topic.id, author=author).first()
            last_topic = Topic.objects.filter(id__lt=author_topic.id, author=author).last()
        else:
            next_topic = Topic.objects.filter(id__gt=author_topic.id, author=author, limit='public').first()
            last_topic = Topic.objects.filter(id__lt=author_topic.id, author=author, limit='public').last()

        next_id = next_topic.id if next_topic else None
        next_title = next_topic.title if next_topic else ''
        last_id = last_topic.id if last_topic else None
        last_title = last_topic.title if last_topic else ''

        res = {'code': 200, 'data': {}}
        res['data']['nickname'] = author.nickname
        res['data']['title'] = author_topic.title
        res['data']['category'] = author_topic.category
        res['data']['created_time'] = author_topic.created_time.strftime('%Y-%m-%d %H-%M-%S')
        res['data']['content'] = author_topic.content
        res['data']['introduce'] = author_topic.introduce
        res['data']['author'] = author.nickname
        res['data']['last_id'] = last_id
        res['data']['last_title'] = last_title
        res['data']['next_id'] = next_id
        res['data']['next_title'] = next_title
        res['data']['messages'] = []
        res['data']['messages_count'] = 0
        return res

    def make_topics_res(self, author, author_topics):

        res = {'code': 200, 'data': {}}
        topics_res = []
        for topic in author_topics:
            d = {}
            d['id'] = topic.id
            d['title'] = topic.title
            d['category'] = topic.category
            d['created_time'] = topic.created_time.strftime("%Y-%m-%d %H:%M:%S")
            d['introduce'] = topic.introduce
            d['author'] = author.nickname
            topics_res.append(d)

        res['data']['topics'] = topics_res
        res['data']['nickname'] = author.nickname
        return res

    @method_decorator(logging_check)
    def post(self, request, author_id):
        author = request.myuser

        # 取前端数据
        json_str = request.body
        json_obj = json.loads(json_str)
        title = json_obj['title']
        content = json_obj['content']
        content_text = json_obj['content_text']
        introduce = content_text[:30]
        limit = json_obj['limit']
        category = json_obj['category']
        if limit not in ['public', 'private']:
            result = {'code': 10300, 'error': 'The limit error~'}
            return JsonResponse(result)

        # 创建topic数据
        Topic.objects.create(title=title, content=content, limit=limit, category=category, introduce=introduce,
                             author=author)

        return JsonResponse({'code': 200})

    def get(self, requset, author_id):
        # /v1/topics/guoxiaonao
        # 访问者 visitor
        # 当前被访问博客的博主 author
        try:
            author = UserProfile.objects.get(username=author_id)
        except Exception as e:
            result = {'code': 10301, 'error': 'The author is not existed'}
            return JsonResponse(result)

        visitor = get_user_by_request(requset)
        visitor_username = None
        if visitor:
            visitor_username = visitor.username

        t_id = requset.GET.get('t_id')
        if t_id:
            # /v1/topics/guoxiaonao?t_id=1
            # 获取指定文章数据
            t_id = int(t_id)
            is_self = False
            if visitor_username == author_id:
                is_self = True
                try:
                    author_topic = Topic.objects.get(id=t_id, author_id=author_id)
                except Exception as e:
                    result = {'code': 10302, 'error': 'No topic'}
                    return JsonResponse(result)
            else:
                try:
                    author_topic = Topic.objects.get(id=t_id, author_id=author_id, limit='public')
                except Exception as e:
                    result = {'code': 10303, 'error': 'No topic'}
                    return JsonResponse(result)
            res = self.make_topic_res(author, author_topic, is_self)
            return JsonResponse(res)

        else:
            # 获取列表页数据
            # /v1/topics/guoxiaonao
            # /v1/topics/guoxiaonao?category=[tec|no-tec]
            category = requset.GET.get('category')
            if category in ['tec', 'no-tec']:

                if visitor_username == author_id:
                    # 博主访问自己博客
                    author_topics = Topic.objects.filter(author_id=author_id, category=category)
                else:
                    author_topics = Topic.objects.filter(author_id=author_id, limit='public', category=category)
            else:
                if visitor_username == author_id:
                    # 博主访问自己博客
                    author_topics = Topic.objects.filter(author_id=author_id)
                else:
                    author_topics = Topic.objects.filter(author_id=author_id, limit='public')

            res = self.make_topics_res(author, author_topics)
            return JsonResponse(res)