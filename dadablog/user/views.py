import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from .models import UserProfile
import hashlib


# 异常码 10100-10199

# Create your views here.
# FBV
def user_views(request):
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        pass


# CBV
# 更灵活[可继承]
# 对未定义的http method 请求 直接返回405响应
class UserViews(View):
    # def get(self, request):
    #     return JsonResponse({'code': 200, 'msg': 'test'})

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
