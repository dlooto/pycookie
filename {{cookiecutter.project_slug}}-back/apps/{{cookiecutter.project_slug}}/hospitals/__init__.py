# coding=utf-8
#
# Created by junn, on 2018/5/29
#

# This is a sample


from django.apps import AppConfig


class HospitalsAppConfig(AppConfig):
    name = '{{cookiecutter.project_slug}}.hospitals'
    verbose_name = "医疗机构管理"

default_app_config = '{{cookiecutter.project_slug}}.hospitals.HospitalsAppConfig'
