# coding=utf-8
#
# Created by junn, on 2018-6-6
#

"""

"""

import logging

from django.contrib import admin

from .models import Hospital, Staff, Department, Group

logs = logging.getLogger(__name__)


class HospitalAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'organ_name', 'industry', 'address', 'contact', 'auth_status', 'creator',
        'created_time', 'parent', 'grade'
    )
    # fields = ('creator', 'organ_name', 'desc', 'get_all_groups')
    list_display_links = ('id', 'organ_name', 'creator')
    search_fields = ('id', 'organ_name', 'contact')


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'organ', 'name', 'contact', 'attri','created_time')
    search_fields = ('id', 'name', 'desc')
    # list_filter = ('',)
    # actions = (,)


class StaffAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'organ', 'dept', 'title', 'contact', 'group')
    search_fields = ('id', 'name', 'contact', 'title', 'email', 'organ__organ_name')
    list_display_links = ('name', 'email', )
    # list_filter = ('',)
    # actions = (,)

    def save_model(self, request, obj, form, change):
        super(StaffAdmin, self).save_model(request, obj, form, change)
        obj.clear_cache()


# class PermissionInline(admin.TabularInline):
#     model = Group.permissions.through
#
# class PermissionAdmin(admin.ModelAdmin):
#     list_display = ('codename', 'name', 'cate', 'pre_defined')
#     search_fields = ('codename', 'name', )
#     list_display_links = ('codename', )
#     list_filter = ('cate', )
#     # actions = (,)


class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'organ', 'cate', 'is_admin', 'desc')
    search_fields = ('name', 'organ__organ_name')
    list_display_links = ('name', )
    list_filter = ('is_admin', 'cate')
#     # actions = (,)
#
#     inlines = [
#         PermissionInline,
#     ]
#
#     exclude = ('permissions',)


class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'codename', 'desc')
    search_fields = ('name', 'codename', 'desc')
    list_display_links = ('name', 'codename')


class UserRoleShipAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', )
    list_display_links = ('user', 'role',)


admin.site.register(Hospital, HospitalAdmin)
admin.site.register(Staff, StaffAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Group, GroupAdmin)

from django.contrib.auth.models import Group as _Group
from django.contrib.sites.models import Site as _Site

admin.site.unregister((_Group, _Site))
