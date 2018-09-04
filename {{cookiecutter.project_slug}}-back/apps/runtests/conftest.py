# coding=utf-8

import os
import django
from django.conf import settings
from settings import configure_logging_params

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

LOGGING_SETTINGS = {
    'log_file_root':        os.path.join(os.path.dirname(__file__), '../../logs'),
    'log_file_path':        '{{cookiecutter.project_slug}}-back/runtests.log',
    'log_sql_in_file':      False,      # 是否将debug级别的SQL语句输出写入日志文件
    'sql_log_level':        'INFO',     # 该设置决定是否输出SQL语句, django框架的SQL语句仅在DEBUG级才能输出. 默认仅输出到console
    'django_log_level':     'DEBUG',    # 该设置决定django框架自身的日志输出
    'business_log_level':   'DEBUG',    # 业务模块日志级别
}

# 运行测试用例时使用该配置
DATABASES = {
    "default": {
        "ENGINE":   'django.db.backends.mysql',
        "OPTIONS": {
            'sql_mode': 'TRADITIONAL',
        },

        'TEST': {
            'NAME':     'test_{{cookiecutter.project_slug}}1',
            'CHARSET':  'utf8',
            'COLLATION': 'utf8_general_ci',
        },
    }
}

# 本模板中相关注释代码请勿删 !!!
# `pytest` automatically calls this function once when runtests are run.
def pytest_configure():
    # settings.DEBUG = False

    # If you have any test specific settings, you can declare them here, e.g.
    # settings.PASSWORD_HASHERS = (
    #     'django.contrib.auth.hashers.MD5PasswordHasher',
    # )
    settings.LOGGING = configure_logging_params(**LOGGING_SETTINGS)
    django.setup()
