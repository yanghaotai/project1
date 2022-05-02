from dadablog.celery import app
from tools.sms import YunTongXin

@app.task
def send_sms_c(phone, code):
    config = {
        'accountSid': '8aaf0708806f236e01807e964d8102f9',
        'accountToken': 'c7c424c5eca1422b9f9cf86258e8fdfb',
        'appId': '8aaf0708806f236e01807e964e8802ff',
        'templateId': '1'
    }

    yun = YunTongXin(**config)
    res = yun.run(phone, code)
    return res
