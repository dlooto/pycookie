## 为什么要使用 Cookiecutter?
* 快速复制代码工程, 应对多项目多产品体系    
* 已有多年积累的基础代码框架
* 简单配置, 一键建立初始代码工程结构
    * Cookiecuter: 根据已有工程模板创建新工程
    * 原本主用于开源社区

## 配置与安装步骤 - -以Python/Django后端工程为例
* mkvirtualenv <pycookie>         --安装cookiecutter运行环境
* pip install cookiecutter
* 设置初始代码工程模板               --或提交到Code Repository
* 添加并修改配置文件: cookiecutter.json
* cookiecutter  <base_code_project>  # or <remote_code_repos>
    1.通过本地代码工程
    2.使用远端代码仓库

## 写在后面...
* Not Just for Python/Django
* 定期更新工程模板
* 用代码仓库将工程模板管理起来
* 贡献开源社区
示例代码工程模板:
    git@github.com:audreyr/cookiecutter-pypackage.git

### 工程模板示例:
```
pycookie
├── CONTRIBUTING.rst
├── LICENSE
├── Makefile
├── README.rst
├── appveyor.yml
├── cookiecutter.json
├── docs
├── hooks
│   ├── post_gen_project.py
│   └── pre_gen_project.py
├── requirements_dev.txt
├── setup.cfg
├── setup.py
├── tests
├── tox.ini
└── {{cookiecutter.project_slug}}-back
    ├── AUTHORS.rst
    ├── README.md
    ├── __init__.py
    ├── apps
    ├── deploy
    ├── docs
    ├── fabenv.py
    ├── fabfile.py
    ├── logs -> /data/nmis/logs
    ├── media -> /data/nmis/media
    ├── resources
    ├── static
    └── templates
```
