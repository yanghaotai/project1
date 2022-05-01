import json

from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from .models import UserProfile
import hashlib
from tools.logging_dec import logging_check

# 异常码 10100-10199

# django提供了一个装饰器 method_decorator,可以将函数装饰器转换成 方法装饰器

# Create your views here.
# FBV
@logging_check
def users_views(request, username):
    if request.method != 'POST':
        result = {'code': 10103, 'error': 'Please use POST'}
        return JsonResponse(result)

    # try:
    #     user = UserProfile.objects.get(username=username)
    # except Exception as e:
    #     result = {'code': 10104, 'error': 'The username is error '}
    #     return JsonResponse(result)
    user = request.myuser

    avatar = request.FILES['avatar']
    user.avatar = avatar
    user.save()
    return JsonResponse({'code': 200})


# CBV
# 更灵活[可继承]
# 对未定义的http method 请求 直接返回405响应
class UserViews(View):

    def get(self, request, username=None):

        if username:
            # /v1/users/guoxiaonao
            try:
                user = UserProfile.objects.get(username=username)
            except Exception as e:
                result = {'code': 10102, 'error': 'The username is wrong'}
                return JsonResponse(result)
            result = {'code': 200, 'username': username,
                      'data': {'info': user.info, 'sign': user.sign, 'nickname': user.nickname,
                               'avatar': str(user.avatar)}}
            return JsonResponse(result)

        else:
            # /v1/users
            pass
        return JsonResponse({'code': 200, 'msg': 'test'})

    def post(self, request):
        json_str = request.body
        json_obj = json.loads(json_str)
        username = json_obj['username']
        email = json_obj['email']
        password_1 = json_obj['password_1']
        password_2 = json_obj['password_2']
        phone = json_obj['phone']

        # 参数基本检查
        if password_1 != password_2:
            result = {'code': 10100, 'error': 'The password is not same~'}
            return JsonResponse(result)
        # 检查用户名是否可用
        old_users = UserProfile.objects.filter(username=username)
        if old_users:
            result = {'code': 10101, 'error': 'The username is already existed'}
            return JsonResponse(result)
        # UserProfile插入数据(密码md5存储)
        p_m = hashlib.md5()
        p_m.update(password_1.encode())

        UserProfile.objects.create(username=username, nickname=username, password=p_m.hexdigest(), email=email,
                                   phone=phone)

        result = {'code': 200, 'username': username, 'data': {}}
        return JsonResponse(result)

    @method_decorator(logging_check)
    def put(self, request, username=None):
        # 更新用户数据【昵称 个人签名 个人描述】
        # /v1/users/guoxiaonao
        json_str = request.body
        json_obj = json.loads(json_str)

        # try:
        #     user = UserProfile.objects.get(username=username)
        # except Exception as e:
        #     result = {'code': 10105, 'error': 'The username is error'}
        #     return JsonResponse(result)
        user = request.myuser

        user.sign = json_obj['sign']
        user.info = json_obj['info']
        user.nickname = json_obj['nickname']

        user.save()
        return JsonResponse({'code': 200})
