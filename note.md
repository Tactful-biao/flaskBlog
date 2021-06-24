## 项目开发相关

+ 搭建项目结构
+ 创建视图
    * Blueprint
    * 不同功能按模块进行划分
+ 创建模板
    * 使用flask-bootstrap
    * 继承bootstrap/base.html
+ 创建配置文件
    * 数据库链接
    * 用户名
    * 密码
+ 创建数据库相关脚本
    * 表结构
+ 创建工厂函数 app/__init__.py
    * 用来注册各种组件到app上
    * 注册蓝本
+ 认证登陆
    * flask-login要求实现的用户方法
        + is_authenticated()  如果用户已经登录，必须返回True，否则返回False
        + is_active()  如果允许用户登录，必须返回True，否则返回False。如果要禁用账户，可以返回False
        + is_anonymous()  对普通用户必须返回False
        + get_id()  必须返回用户的唯一标识符，使用Unicode编码字符串
    * flask-login提供了UserMixin，包含这些默认实现
    * 在工厂函数中注册
    * 在模型中定义加载用户的回调函数  load_user
    * 路由保护， 图个未认证访问该路由会被拦截
    ```
    form flask_login import ligin_required

    @app.route('/secret')
    @login_required
    def decret():
        return 'Only authenticated users are allowed!'
    ```
    + 访问未授权的页面跳转到登录页面，登录完之后可以直接重定向到之前的页面
        * request.args.get('next') 登录之前访问的页面
    + 注册页面
        * 邮箱、用户名、密码字段
        * 验证用户名、邮箱是否被注册
        * validate_开头的函数需要配合ValidationError使用，这样前台会显示相应的错误