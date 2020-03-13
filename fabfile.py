from fabric import task, Connection
from invoke import Responder
from _credentials import github_username, github_password


def _get_github_auth_responders():
    """
    返回 GitHub 用户名密码自动填充器
    """
    username_responder = Responder(
        pattern="Username for 'https://github.com':",
        response='{}\n'.format(github_username)
    )
    password_responder = Responder(
        pattern="Password for 'https://{}@github.com':".format(github_username),
        response='{}\n'.format(github_password)
    )
    return [username_responder, password_responder]


def _raw_deploy_task(c, conf_path, root_path, program):
    # 进入项目根目录，从 Git 拉取最新代码
    with c.cd(root_path):
        cmd = 'git pull'
        responders = _get_github_auth_responders()
        c.run(cmd, watchers=responders)

    # 安装依赖，迁移数据库，收集静态文件
    with c.cd(root_path):
        c.run('pipenv install --deploy --ignore-pipfile')
        c.run('pipenv run python manage.py makemigrations')
        c.run('pipenv run python manage.py migrate')
        c.run('pipenv run python manage.py collectstatic --noinput')

    # 重新启动应用
    with c.cd(conf_path):
        cmd = 'supervisorctl restart {}'.format(program)
        c.run(cmd)


@task()
def deploy(c):
    """
    :param c: 这个参数的值是 Fabric 在连接服务器时创建的 ssh 客户端实例，使用这个实例可以在服务器上运行相关命令
    :return:
    """
    supervisor_conf_path = '/home/slgweb/'
    supervisor_program_name = 'wasteland'

    project_root_path = '/home/slgweb'
    _raw_deploy_task(c, supervisor_conf_path, project_root_path, supervisor_program_name)


@task()
def deploy_feimi(c):
    """
    feimi 内网192.168.1.5 pyweb
    """
    c = Connection('192.168.1.5:22', user='root', connect_kwargs={"password": "RXozGdpWcyCfzk1X"})
    supervisor_conf_path = '/home/pyweb'
    supervisor_program_name = 'wasteland'

    project_root_path = '/home/pyweb'
    _raw_deploy_task(c, supervisor_conf_path, project_root_path, supervisor_program_name)