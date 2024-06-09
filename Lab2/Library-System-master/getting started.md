# Getting started

### 如何部署

- 下载项目

- 用Pycharm打开工程

- 安装对应的包（都用最新的应该就行了）

- 修改数据库配置文件`\Library\manage.py`中数据库配置文件

  - 在django中创建`django_library`数据库

  - 找到本地数据库一个可用的管理员账号和密码（当然也可以再注册一个新的）

  - 修改`\Library\settings.py`中以下配置

    ```Python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': '127.0.0.1',  # 数据库主机
            'PORT': ,  # 数据库端口
            'USER': '',  # 数据库用户名
            'PASSWORD': '',  # 数据库用户密码
            'NAME': 'django_library'  # 数据库名字
        }
    }
    ```

- 运行项目

  - 在Pycharm中运行选项`manage.py`
  - 如果看到白字提示已经运行在`localhost:8000`则提示成功，可用浏览器验证
  - 如果提示缺少参数则配置运行选项`manage.py`需要的参数parameters`runserver 127.0.0.1:8000`

- 创建管理员账号（可选）

  - 找到目录下的`manage.py`
  - 用命令行进入当前目录
  - 运行命令`python manage.py makemigrations`创建迁移文件
  - 运行命令`python manage.py migrate`进行迁移
  - 运行命令`python manage.py createsuperuser`创建超级用户

- 数据库迁移

  - 首先保证django已经成功连上数据库
  - 修改`models.py`
  - 运行命令`python manage.py makemigrations`创建迁移文件
  - 运行命令`python manage.py migrate`进行迁移

- 修改数据库中的数据

  - 可以直接通过`localhost:8000/admin`修改
  - 可以直接用过MySQL修改

### Django框架

Django开发手册：https://docs.djangoproject.com/en/3.0/

Django光速入门视频：https://www.bilibili.com/video/BV1Wt411K7QH

Django快速入门系列：https://www.bilibili.com/video/BV18W41137Qx

- `Library`
  - `settings.py`：配置文件
  - `urls.py`：浏览器中的路径和`views.py`中函数的对应
- `MyWEB`
  - `models.py`：MySQL中表格的定义
  - `views.py`：全部后台逻辑
  - `templates`：存放所有html的文件夹