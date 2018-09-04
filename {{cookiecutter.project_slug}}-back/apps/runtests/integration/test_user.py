#!/usr/bin/env python
# encoding: utf-8
"""
python manage.py test runtests.test_user
"""
from collections import defaultdict
from copy import deepcopy

from django.urls import reverse

from {{cookiecutter.project_slug}}.hospitals.models import Role, Group
from users.forms import is_valid_password

from runtests import BaseTestCase
from base.authtoken import CustomToken
import datetime


class UserTestCase(BaseTestCase):

    login_api = '/api/v1/users/login'

    def test_login(self):
        """
        登录测试
        """
        account = {
            'username': 'abc_test123', 'password': 'x111111',
            'email': 'test_email@{{cookiecutter.project_slug}}.com'
        }
        user = self.create_user_with_username(active=True, **account)
        a_staff = self.create_staff(user, self.organ, self.dept)
        a_staff.set_group(self.organ.get_admin_group())

        data = deepcopy(account)
        data.update({'authkey': 'username'})
        resp = self.post(self.login_api, data=data)

        self.assert_response_success(resp)
        self.assertIsNotNone(resp.get('user'))
        self.assertIsNotNone(resp.get('staff'))
        self.assertIsNotNone(resp.get('authtoken'))

        data.update({'password': 'x222222'})
        resp = self.post(self.login_api, data=data)
        self.assert_response_not_success(resp)

    # def test_verify_key(self):
    #     user = self.create_user(active=True)
    #     record = user.generate_reset_record()
    #
    #     def do_post(key):
    #         return self.post(reverse('users_verify_key'), data={'reset_key': key})
    #
    #     response = do_post('a invalid key')
    #     self.assertEqual(response['code'], 0)
    #
    #     response2 = do_post(record.key)
    #     self.assertEqual(response2['code'], 10000)
    #
    #     record.set_invalid()
    #     response3 = do_post(record.key)
    #     self.assertEqual(response3['code'], 0)
    #
    # def test_activate_user(self):
    #     user = self.create_user(active=False)
    #     self._test_reset_password(user, 'organs_signup_activate', 'activation_key', user_activate_status=True)
    #
    #     self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)  # 登录成功
    #
    # def test_request_reset_password(self):
    #     key, captcha = self.request_captcha()
    #
    #     _do_post = lambda _user: self.post(
    #             reverse('users_request_reset'),
    #             data={'email': _user.email, 'captcha': captcha, 'captcha_key': key, }
    #         )
    #
    #     user = self.create_user(active=True)
    #     response = _do_post(user)
    #     self.assertEqual(response['code'], 10000)
    #
    #     response2 = _do_post(user)
    #     self.assertEqual(response2['code'], 11009)
    #
    # def test_reset_password(self):
    #     self._test_reset_password(self.create_user(active=True), 'users_reset_password', 'reset_key', True)
    #
    #     with self.assertRaises(AssertionError):
    #         self._test_reset_password(self.create_user(active=False), 'users_reset_password', 'reset_key')
    #
    # def test_is_valid_password(self):
    #     expects = [
    #         ('1' * 6, False),
    #         ('a' * 6, False),
    #         ('a' * 10, False),
    #
    #         ('1a' * 3, True),
    #         ('1a' * 10, True),
    #         ('1a' * 10 + '1', False),
    #         ('abc*()123', True),
    #     ]
    #
    #     for password, expected in expects:
    #         self.assertEqual(is_valid_password(password), expected)
    #
    # def _test_reset_password(self, user, viewname, keyname, user_activate_status=None):
    #     reset_record = user.generate_reset_record()
    #     self.assertTrue(reset_record.is_valid())
    #     self.assertEqual(user, reset_record.get_user())
    #     new_password = self.generate_password()
    #     response = self.post(
    #         reverse(viewname),
    #         data={keyname: reset_record.key, 'new_password': new_password},
    #     )
    #     user.refresh_from_db()
    #     reset_record.refresh_from_db()
    #     self.assertTrue(user.check_password(new_password))
    #     self.assertFalse(reset_record.is_valid())
    #
    #     if user_activate_status is not None:
    #         self.assertEqual(user.is_active, user_activate_status)


# class TokenTestCase(BaseTestCase):
#     """
#     用户登录权限Token测试用例
#     """
#
#     def setUp(self):
#         super(self.__class__, self).setUp()
#
#         response = self.login(self.user)
#         self.token = response.get('authtoken')
#
#     def test_refresh(self):
#         """
#         刷新用户Token
#         :return:
#         """
#         url = reverse('token_refresh')
#         token = self.token
#         for i in xrange(3):
#             response = self.post(url, data={'old_token': token})
#             self.assert_response_success(response)
#             self.assertNotEqual(response.get('token'), token)
#             token = response.get('token')
#             self.client.defaults['HTTP_AUTHORIZATION'] = 'Token {}'.format(token)
#         response = self.post(url, data={'old_token': self.token})
#         self.assert_response_failure(response)
#         self.token = token
#
#     def test_verify(self):
#         """
#         验证Token是否有效
#         :return:
#         """
#         url = reverse('token_verify')
#         response = self.post(url, data={'token': self.token})
#         self.assert_response_success(response)
#         self.assertFalse(response.get('is_expired'))
#         response = self.post(url, data={'token': self.token[4:] + self.token[:4]})
#         self.assert_response_failure(response)
#
#         token = CustomToken.objects.get(key=self.token)
#         token.created = token.created - datetime.timedelta(days=token.expired_day)
#         token.save()  # 修改创建时间
#         response = self.post(url, data={'token': self.token})
#         self.assert_response_success(response)
#         self.assertTrue(response.get('is_expired'))
#
#     def test_custom_token(self):
#         """
#         测试Proxy Token对象的可用性
#         :return:
#         """
#         token = CustomToken.objects.get(key=self.token)
#         self.assertFalse(token.is_expired())
#         token.created = token.created - datetime.timedelta(days=token.expired_day)
#         token.save()
#         self.assertTrue(token.is_expired())
#         token.refresh(token)


class RoleTestCase(BaseTestCase):

    def test_assign_role_dept_domains(self):
        api = '/api/v1/users/assign-roles-dept-domains/'

        # 创建初始化数据
        self.login_with_username(self.user)
        user1 = self.create_user_with_username('测试用户0001', '123456', active=True)
        staff1 = self.create_staff(user1, self.organ, self.dept, '测试员工0001')
        dept1 = self.create_department(self.organ, dept_name='测试部门0001')
        user2 = self.create_user_with_username('测试用户0002', '123456', active=True)
        staff2 = self.create_staff(user2, self.organ, self.dept, '测试员工0002')
        dept2 = self.create_department(self.organ, dept_name='测试部门0002')

        groups = Group.objects.all()
        permissions =[]

        for group in groups:
            permissions.append(group.id)

        role1 = Role.objects.create_role(data={'name': '测试角色0001', 'permissions': [permissions[0]]})
        role2 = Role.objects.create_role(data={'name': '测试角色0002', 'permissions': [permissions[1]]})

        self.login_with_username(self.user)
        # 封装请求参数
        data = defaultdict(list)
        user_ids = [user1.id, user2.id]
        role_ids = [role1.id, role2.id]
        dept_domain_ids = [dept1.id, dept2.id]
        data['user_ids'] = user_ids
        data['role_ids'] = role_ids
        data['dept_domain_ids'] = dept_domain_ids

        resp1 = self.post(api.format(), data=data)
        self.assert_response_success(resp1)
        for role in user1.get_roles():
            self.assertTrue((role.id == role1.id or role.id == role2.id))
            dept_domains = role.get_user_role_dept_domains(user1)
            for dept in dept_domains:
                self.assertTrue((dept.id == dept1.id or dept.id == dept2.id))

        for role in user2.get_roles():
            self.assertTrue((role.id == role1.id or role.id == role2.id))
            dept_domains = role.get_user_role_dept_domains(user2)
            for dept in dept_domains:
                self.assertTrue((dept.id == dept1.id or dept.id == dept2.id))

        data.get('user_ids').remove(user1.id)
        data.get('role_ids').remove(role1.id)
        data.get('dept_domain_ids').remove(dept1.id)
        resp2 = self.post(api.format(), data=data)
        self.assert_response_success(resp2)

        for role in user1.get_roles():
            self.assertTrue((role.id == role1.id or role.id == role2.id))
            dept_domains = role.get_user_role_dept_domains(user1)
            for dept in dept_domains:
                self.assertTrue((dept.id == dept1.id or dept.id == dept2.id))
        self.assertEqual(1, len(user2.get_roles()))
        for role in user2.get_roles():
            self.assertTrue((role.id == role2.id))
            dept_domains = role.get_user_role_dept_domains(user2)
            self.assertEqual(1, len(dept_domains))
            for dept in dept_domains:
                self.assertTrue(dept.id == dept2.id)

        data.get('user_ids').append(user1.id)
        data.get('role_ids').append(role1.id)
        data.get('role_ids').remove(role2.id)
        data.get('dept_domain_ids').append(dept1.id)
        data.get('dept_domain_ids').remove(dept2.id)
        resp3 = self.post(api.format(), data=data)
        self.assert_response_success(resp3)
        roles = user1.get_roles()
        self.assertEqual(1, len(roles))
        role = user1.get_roles()[0]
        self.assertTrue(role.id == role1.id)
        dept_domains = role.get_user_role_dept_domains(user1)
        self.assertEqual(1, len(dept_domains))
        self.assertTrue(dept_domains[0].id == dept1.id)

        roles = user2.get_roles()
        self.assertEqual(1, len(roles))
        role = user1.get_roles()[0]
        self.assertTrue(role.id == role1.id)
        dept_domains = role.get_user_role_dept_domains(user2)
        self.assertEqual(1, len(dept_domains))
        self.assertTrue(dept_domains[0].id == dept1.id)













