 # coding=utf-8
#
# Created by junn, on 2018-5-29
#

"""
组织/机构相关数据模型
"""

import logging

import settings
from django.db import models, transaction

from base.models import BaseModel
from utils import times
from .managers import GroupManager, RoleManager

from users.models import User, UserSecureRecord
from .managers import StaffManager, HospitalManager

from .consts import *

logs = logging.getLogger(__name__)


class BaseOrgan(BaseModel):
    """
    企业/组织机构抽象数据模型
    """

    AUTH_CHECKING = 1   # 等待审核...
    AUTH_APPROVED = 2   # 审核通过
    AUTH_FAILED = 3     # 审核失败

    # 机构认证审核状态选项
    AUTH_STATUS_CHOICES = (
        (AUTH_CHECKING, u'等待审核'),
        (AUTH_APPROVED, u'审核通过'),
        (AUTH_FAILED,   u'审核未通过'),
    )

    SCALE_CHOICES = (
        (1, '0-49人'),
        (2, '50-199人'),
        (3, '200-499人'),
        (4, '500-999人'),
        (5, '1000-1999人'),
        (6, '2000人以上'),
    )

    default_timeout = 60 * 60  # 默认在redis中缓存60分钟

    # 企业注册时的创建者. 创建者不可变并唯一, 企业管理员可以变化
    creator = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=u'创建者', on_delete=models.CASCADE)

    organ_name = models.CharField(u'企业/组织名称', max_length=100, default='')
    organ_scale = models.SmallIntegerField(u'企业规模', choices=SCALE_CHOICES, null=True, blank=True, default=1)

    contact_name = models.CharField(u'联系人姓名', max_length=32, default='')
    contact_phone = models.CharField(u'联系人手机号码', max_length=20, null=True, blank=True, default='') # 不作为登录手机号
    contact_title = models.CharField(u'联系人职位', max_length=40, null=True, blank=True, default='')

    logo = models.CharField(u'企业logo', max_length=80, blank=True, null=True, default='')
    industry = models.CharField(u'行业类型', max_length=80, null=True, blank=True, default='')
    address = models.CharField(u'企业/机构地址', max_length=100, null=True, blank=True, default='')
    contact = models.CharField(u'联系电话', max_length=20, null=True, blank=True, default='')

    auth_status = models.SmallIntegerField(u'认证状态', choices=AUTH_STATUS_CHOICES, default=AUTH_CHECKING)

    # 各报道链接以逗号分隔
    media_cover = models.CharField(u'媒体报道', max_length=800, null=True, blank=True, default='')
    desc = models.TextField(u'企业介绍', null=True, blank=True, default='')


    class Meta:
        abstract = True

    def __unicode__(self):
        return u'%s %s' % (self.id, self.organ_name)

    def is_authed(self):
        """
        是否已审核通过
        """
        return self.auth_status == self.AUTH_APPROVED

    def is_auth_failed(self):
        """是否审核失败"""
        return self.auth_status == self.AUTH_FAILED

    def is_checking(self):  # 是否等待审核中
        return self.auth_status == self.AUTH_CHECKING

    def accept(self):
        """通过审核"""
        self.auth_status = self.AUTH_APPROVED
        self.save()
        self.cache()

    def show_auth_status(self):
        """ 显示审核状态 """
        if self.is_authed():
            return u'审核通过'
        if self.auth_status == self.AUTH_CHECKING:
            return u'审核中'
        if self.auth_status == self.AUTH_FAILED:
            return u'审核未通过'

    def create_staff(self, user, name, email, contact, group=None, title=''):
        """
        创建员工对象
        :param user: 关联用户
        :param name: 员工姓名
        :param title:  员工职位
        :param contact: 联系电话
        :param email: Email
        :return:
        """
        kwargs = {
            'user': user,
            'organ': self,
            'name': name,
            'title': title,
            'contact': contact,
            'email': email,
            'group': group,
        }
        staff = BaseStaff(**kwargs)
        staff.save()
        return staff

    ################################################
    #                  权限组操作
    ################################################

    def get_all_groups(self):
        pass

    def get_specified_group(self, group_key):
        """
        通过权限组关键字获取指定的权限组
        :param group_key: 权限组关键字, 对应group模型中的cate, 字符串类型
        :return: 对应的权限组对象, Group object
        """
        return self.get_all_groups().filter(cate=group_key).first()

    def get_admin_group(self):
        """
        返回企业管理员组. 每个企业当且仅有一个admin组
        """
        return self.get_all_groups().filter(is_admin=True).first()


    ################################################
    #                  员工操作
    ################################################

    def get_all_staffs(self):
        """获取企业所有员工列表"""
        return BaseStaff.objects.custom_filter(organ=self)

    def get_staffs_in_group(self, group):
        return self.get_all_staffs().filter(group=group)


class CommonOrgan(BaseOrgan):
    """
    通用/一般的企业/组织机构数据模型. 企业/机构相关数据逻辑的默认实现, 若企业/机构数据没有特殊性,
    可考虑采用该默认数据模型

    """

    class Meta:
        verbose_name = u'A 企业/组织'
        verbose_name_plural = u'A 企业/组织'
        db_table = 'organs_organ'


class BaseDepartment(BaseModel):
    """
    企业的部门数据模型
    """

    organ = models.ForeignKey(BaseOrgan, verbose_name=u'所属医疗机构', on_delete=models.CASCADE)
    name = models.CharField(u'部门名称', max_length=100, default='')
    contact = models.CharField(u'联系电话', max_length=20, null=True, blank=True, default='')
    desc = models.TextField(u'描述', null=True, blank=True, default='')

    class Meta:
        abstract = True

    def __str__(self):
        return u'%s' % self.name


class BaseStaff(BaseModel):
    """
    企业员工数据模型
    """
    DELETE_STATUS = 'D'
    NORMAL_STATUS = 'N'
    STAFF_STATUS = (
        (DELETE_STATUS, u'删除'),
        (NORMAL_STATUS, u'正常')
    )

    default_timeout = 60 * 60  # 默认在redis中缓存60分钟

    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=u'用户账号', on_delete=models.CASCADE)
    organ = models.ForeignKey(BaseOrgan, verbose_name=u'所属机构', null=True, blank=True, on_delete=models.CASCADE)
    dept = models.ForeignKey(BaseDepartment, verbose_name=u'所属部门', null=True, blank=True, on_delete=models.SET_NULL)

    name = models.CharField(u'名字', max_length=40, null=True, blank=True, default='')
    title = models.CharField(u'职位名称', max_length=40, null=True, blank=True, default='') # 后续或可考虑扩展成对象
    contact = models.CharField(u'联系电话', max_length=20, null=True, blank=True, default='')
    email = models.EmailField(u'Email', null=True, blank=True, default='')  # 非账号email

    # 一个staff仅可以加入一个权限group
    group = models.ForeignKey('organs.Group', verbose_name=u'权限组', null=True, blank=True, on_delete=models.SET_NULL)

    status = models.CharField(u'员工状态', max_length=1, default=NORMAL_STATUS)

    objects = StaffManager()

    class Meta:
        abstract = True

    def __unicode__(self):
        return u'%s, %s' % (self.id, self.name)

    def is_organ_admin(self):
        """是否为所属企业的管理员"""
        return self.organ.get_admin_group() == self.group

    def is_admin_for_organ(self, organ):
        """
        是否为指定企业的管理员
        """
        return self.organ == organ and self.is_organ_admin()

    def set_group(self, group):
        """
        给员工设置权限组
        :param group: Group object
        """
        self.group = group
        self.save()

    def has_group_perm(self, group):
        """
        员工是否拥有所属企业指定某权限组的权限
        :return:
        """
        if not group.organ == self.organ:
            return False

        return self.is_organ_admin() or group == self.group

    def get_group_permissions(self, obj=None):  # TODO: 权限组及权限可以考虑从cache中读取
        """
        返回权限码列表. 若传入obj, 则仅返回与obj匹配的权限码列表
        """
        if self.is_organ_admin():
            return Permission.objects.values_list(['codename'])

        return Permission.objects.filter(group__in=self.groups).values('codename')

    def has_perm(self, perm, obj=None):
        """
        :param perm: 权限codename字符串
        """
        return True if perm in self.get_group_permissions() else False

    def has_perms(self, perm_list, obj=None):
        """
        """
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True

    def get_secure_key(self):
        """
        对于登录账号未激活的企业员工用户, 需要该secure_key以访问系统
        若存在可用key, 则直接返回. 否则新生成key返回
        :return:
        """
        secure_record = StaffSecureRecord.objects.filter(
            user=self.user, is_used=False, expire_datetime__gt=times.now()
        ).first()
        if secure_record:
            return secure_record.key
        return self.user.generate_secure_record(StaffSecureRecord, expire_hours=7*24).key

    def set_delete(self):
        """删除员工,标记未已删除"""
        self.user.is_active = False
        self.user.save()
        self.status = self.DELETE_STATUS
        self.save()
        self.user.clear_cache()
        self.clear_cache()

    def add_to_organ(self, name, contact, organ, group):
        """用于恢复删除用户操作"""
        self.name = name
        self.contact = contact
        self.organ = organ
        self.group = group
        self.status = self.NORMAL_STATUS
        self.save()


class StaffSecureRecord(UserSecureRecord):
    """非登录企业员工key相关信息"""
    pass

class Permission(BaseModel):
    """
    自定义权限数据模型
    """

    name = models.CharField(u'权限名', max_length=255)
    codename = models.CharField(u'权限码', max_length=100)
    pre_defined = models.BooleanField(u'平台预定义', default=False)

    class Meta:
        verbose_name = '权限'
        verbose_name_plural = '权限'
        db_table = 'perm_permission'
        ordering = ('codename', )


class BaseGroup(BaseModel):
    """
    权限组数据模型. 每个权限组有一个归属的企业
    """

    GROUP_CATE_CHOICES = ()

    organ = models.ForeignKey('organs.BaseOrgan', verbose_name=u'所属企业', null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(u'权限组名', max_length=40)
    cate = models.CharField(u'权限组类别', max_length=4, choices=GROUP_CATE_CHOICES, null=True, blank=True)
    is_admin = models.BooleanField(u'管理员组', default=False)

    permissions = models.ManyToManyField(Permission, verbose_name=u'权限集', blank=True)
    desc = models.CharField(u'描述', max_length=100, null=True, blank=True, default='')

    class Meta:
        abstract = True

    def __unicode__(self):
        return u'%s' % self.name

    def set_permissions(self, perms):
        """
        为权限组初始化设置权限集
        """
        pass

    def add_permission(self, perm):
        """
        权限组内新加权限
        :param perm: 权限对象,
        """
        pass



class Hospital(BaseOrgan):
    """
    医疗机构数据模型
    """

    parent = models.ForeignKey('self', verbose_name=u'上级医疗单位', on_delete=models.SET_NULL, null=True, blank=True)
    grade = models.CharField('分类等级', choices=HOSP_GRADE_CHOICES, max_length=10, null=True, blank=True, default='')

    objects = HospitalManager()

    class Meta:
        verbose_name = u'A 医疗机构'
        verbose_name_plural = u'A 医疗机构'
        db_table = 'hosp_hospital'

    def __str__(self):
        return '%s %s' % (self.id, self.organ_name)

    def save(self, *args, **kwargs):  # 重写save函数，当admin后台保存表单后，更新缓存
        super(self.__class__, self).save(*args, **kwargs)
        self.cache()


    ################################################
    #                   科室与员工管理
    ################################################

    def get_all_depts(self):
        """
        返回科室所有列表
        """
        return Department.objects.filter(organ=self).order_by('id')

    def add_dept(self, dept):
        """
        添加科室
        :param dept:
        :return:
        """
        pass

    def create_dept(self, **dept_data):
        """
        创建新科室
        :param dept_data: dict data
        :return:
        """
        pass

    def delete_dept(self):
        pass

    def add_staff_to_dept(self, staff, dept):
        """
        添加某员工到指定科室
        :param staff:
        :param dept:
        :return:
        """
        pass

    def create_staff(self, dept, **staff_data):
        """
        创建新员工
        :param staff: dict data
        :param dept:
        :return:
        """
        return Staff.objects.create_staff(self, dept, **staff_data)

    def get_staffs(self, dept=None):
        """
        返回机构的员工列表
        :param dept: 科室, Department object
        """
        staffs_queryset = Staff.objects.filter(organ=self).order_by('id')
        return staffs_queryset.filter(dept=dept) if dept else staffs_queryset

    ################################################
    #                  权限组操作
    ################################################

    def get_all_groups(self):
        """返回企业的所有权限组"""
        return Group.objects.filter(organ=self)

    def create_group(self, **kwargs):
        """
        创建权限组
        :param kwargs: 输入参数
        :return:
        """
        return Group.objects.create_group(self, **kwargs)

    def init_default_groups(self):
        """
        机构初建时初始化默认权限组
        :return:
        """

        group_list = []
        for k in GROUP_CATE_DICT.keys():
            group_data = {'is_admin': False, 'commit': False}
            group_data.update(GROUPS.get(k))
            group_list.append(
                self.create_group(**group_data)
            )
        with transaction.atomic():
            self.create_admin_group()
            Group.objects.bulk_create(group_list)

    def create_admin_group(self):
        """创建管理员组"""
        if self.get_admin_group():
            logs.warn('Create Error: admin group existed for organ: %s' % self.id)
            return

        group_data = {'is_admin': True}
        group_data.update(GROUPS.get('admin'))
        return self.create_group(**group_data)

    def assign_roles_dept_domains(self, users, roles, depts):
        old_ships = []
        ship_args = []
        same_ships = []
        for user in users:
            for role in roles:
                ship_args.append(UserRoleShip(user=user, role=role))

            old_ship_query = UserRoleShip.objects.filter(user=user).all()
            if old_ship_query:
                for query in old_ship_query:
                    old_ships.append(query)

        for ship_arg in ship_args[:]:
            for old_ship in old_ships[:]:
                if ship_arg.user.id == old_ship.user.id and ship_arg.role.id == old_ship.role.id:
                    ship_args.remove(ship_arg)
                    same_ships.append(old_ship)
                    old_ships.remove(old_ship)
        try:
            with transaction.atomic():

                if ship_args:
                    for ship in ship_args:
                        ship.save()
                        ship.cache()
                        ship.dept_domains.set(depts)
                if old_ships:
                    for ship in old_ships:
                        ship.clear_cache()
                        ship.dept_domains.set(depts)
                        ship.delete()
                if same_ships:
                    for s in same_ships:
                        s.dept_domains.set(depts)
                        s.cache
                return True
        except Exception as e:
            logs.info(e.__cause__)
            logs.exception(e)
            return False

    def create_department(self, **dept_data):
        return Department.objects.create(organ=self, **dept_data)

    def batch_upload_departments(self, depts_data):
        try:
            with transaction.atomic():
                dept_list = []
                for data in depts_data:
                    dept_list.append(
                        Department(
                            organ=data.get('organ'),
                            name=data.get('name'),
                            attri=DPT_ATTRI_MEDICAL,
                            desc=data.get('desc')
                    ))
            Department.objects.bulk_create(dept_list)
            return True
        except Exception as e:
            logging.exception(e)
            return False


class Department(BaseDepartment):
    """
    医疗机构下设科室数据模型
    """

    organ = models.ForeignKey(Hospital, verbose_name=u'所属医疗机构', on_delete=models.CASCADE, related_name='organ')  # 重写父类
    attri = models.CharField('科室/部门属性', choices=DPT_ATTRI_CHOICES, max_length=2, null=True, blank=True)

    class Meta:
        verbose_name = u'B 科室/部门'
        verbose_name_plural = u'B 科室/部门'
        db_table = 'hosp_department'

    VALID_ATTRS = [
        'name', 'contact', 'attri', 'desc'
    ]

    def __str__(self):
        return '%s %s' % (self.id, self.name)


class Staff(BaseStaff):
    """
    医疗机构一般员工(非医生)
    """

    # 一个员工仅属于一个企业
    organ = models.ForeignKey(Hospital, verbose_name=u'所属医院', on_delete=models.CASCADE, null=True, blank=True)
    dept = models.ForeignKey(Department, verbose_name=u'所属科室/部门', on_delete=models.CASCADE, null=True, blank=True)
    group = models.ForeignKey('hospitals.Group', verbose_name=u'权限组', null=True, blank=True, on_delete=models.SET_NULL)

    objects = StaffManager()

    VALID_ATTRS = [
        'name', 'title', 'organ', 'dept', 'contact', 'email', 'status'
    ]

    class Meta:
        verbose_name = 'C 员工'
        verbose_name_plural = 'C 员工'
        permissions = (
            ('view_staff', 'can view staffs'),
        )
        db_table = 'hosp_staff'

    def __str__(self):
        return '%s %s' % (self.id, self.name)

    def has_project_dispatcher_perm(self, ):
        group = self.organ.get_specified_group(GROUP_CATE_PROJECT_APPROVER)
        return self.has_group_perm(group)


class Doctor(Staff):
    """
    医生数据模型. 子类和父类都产生表结构, 而子表仅存储额外的属性字段
    """
    medical_title = models.CharField('医生职称', choices=DOCTOR_TITLE_CHOICES, max_length=3, null=True, blank=True)

    class Meta:
        verbose_name = 'D 医生'
        verbose_name_plural = 'D 医生'
        db_table = 'hosp_doctor'


class Group(BaseGroup):
    """
    机构权限组数据模型. 每个权限组有一个归属的企业
    """
    group_cate_choices = GROUP_CATE_CHOICES

    organ = models.ForeignKey(Hospital, verbose_name=u'所属医院', on_delete=models.CASCADE, null=True, blank=True)
    cate = models.CharField(u'权限组类别', max_length=4, choices=GROUP_CATE_CHOICES,
                            null=True, blank=True)
    objects = GroupManager()

    class Meta:
        verbose_name = '权限组'
        verbose_name_plural = '权限组'
        db_table = 'perm_group'


class Role(BaseModel):
    """
    角色数据模型
    """
    name = models.CharField('角色名称', max_length=40)
    codename = models.CharField('角色代码', max_length=100, unique=False, null=True, blank=True, default='')
    cate = models.CharField('类别', max_length=4, choices=GROUP_CATE_CHOICES,
                            null=False, blank=True)
    permissions = models.ManyToManyField(
        Group, verbose_name='权限集',
        related_name="roles", related_query_name='role',
        blank=True
    )
    desc = models.CharField('描述', max_length=100, null=True, blank=True, default='')
    users = models.ManyToManyField(
        User, verbose_name='角色所属用户集',
        through='hospitals.UserRoleShip', through_fields=('role', 'user'),
        related_name="roles", related_query_name='role',
        blank=True
    )
    objects = RoleManager()

    class Meta:
        verbose_name = '角色'
        verbose_name_plural = '角色'
        db_table = 'perm_role'

    def __str__(self):
        return u'%s' % self.name

    def set_permissions(self, perms):
        """
        为角色设置权限集
        """
        self.permissions.set(perms)
        self.save()

    def add_permission(self, perm):
        """
        角色内新加权限
        :param perm: 权限对象,
        """
        self.permissions.set(perm)

    def get_permissions(self):
        """获取去角色下的权限"""
        return self.permissions.all()

    def get_user_role_ships(self, user=None):
        """
        获取用户角色关系记录
        :param user:
        :return:
        """
        return UserRoleShip.objects.filter(user=user, role=self).all()

    def get_user_role_dept_domains(self, user):
        """
        获取用户当前角色可操作的部门域
        :param user:
        :return:
        """
        if not user:
            return None
        return UserRoleShip.objects.filter(user=user, role=self).first().dept_domains.all()


class UserRoleShip(BaseModel):
    user = models.ForeignKey(
        'users.User', verbose_name='用户',
        related_name='user_role_ships', on_delete=models.CASCADE,
    )
    role = models.ForeignKey(
        'hospitals.Role', verbose_name='角色',
        related_name='user_role_ships', on_delete=models.CASCADE,
    )
    dept_domains = models.ManyToManyField(
        Department, verbose_name='用户当前角色可操作部门域集合',
        related_name="user_role_ships", related_query_name='user_role_ship', blank=True
    )

    class Meta:
        verbose_name = '用户角色关系'
        verbose_name_plural = verbose_name
        unique_together = ('user', 'role')
        db_table = 'perm_user_roles'

    def __str__(self):
        return '%s %s' % (self.user_id, self.role_id)
