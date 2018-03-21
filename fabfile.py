import os
from fabric.api import cd, env, prefix, sudo, task, settings, run, shell_env
from fabric.contrib.files import exists

PROJECT_NAME = os.getenv('PROJECT_NAME')
DB_NAME = os.getenv('DB_NAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
PROJECT_PATH = os.getenv('PROJECT_PATH')
PROJECT_ROOT = os.path.join(PROJECT_PATH, PROJECT_NAME)
REPO = '%s/%s.git' % (os.getenv('USER_REPO'), PROJECT_NAME)

env.hosts = ['%s@%s:%s' % (os.getenv('HOST_USER'),
                           os.getenv('HOST'),
                           os.getenv('HOST_PORT'))]
env.environment = 'staging'
env.user = os.getenv('HOST_USER')
env.password = os.getenv('HOST_PASSWORD')


class FabricException(Exception):
    pass


def install_system_packages():
    sudo('apt-get -y install python3')
    sudo('apt-get -y install nginx')
    sudo('apt-get -y install python3-pip python3-dev libpq-dev postgresql '
         'postgresql-contrib')
    sudo('apt-get -y install git')
    sudo('pip3 install virtualenv')
    return


def recreate_database():
    with settings(abort_exception=FabricException):
        try:
            sudo('su - postgres psql -c "dropdb %s"' % DB_NAME)
        except FabricException:
            pass
        sudo('su - postgres psql -c "createdb %s"' % DB_NAME)
    return


def change_postgres_user_password(db_password):
    command = "alter user postgres with password '%s'" % db_password
    sudo('sudo -u postgres psql -c "%s"' % command)
    return


def clone_or_pull_git_repo():
    if not exists(PROJECT_ROOT, use_sudo=True):
        sudo('mkdir -p %s' % PROJECT_PATH)
        with(cd(PROJECT_PATH)):
            sudo('git clone %s' % REPO)
    else:
        with cd(PROJECT_ROOT):
            sudo('git pull origin')
    return


def install_pip_requirements():
    with cd(PROJECT_PATH):
        sudo('virtualenv %s' % PROJECT_NAME)
    with cd(PROJECT_ROOT):
        sudo('source bin/activate && pip3 install -r requirements.txt')
    return


def create_dj_superuser():
    run('python3 manage.py migrate')
    superuser_password = os.getenv('SUPERUSER_PASSWORD')
    with settings(prompts={"Password: ": superuser_password,
                           "Password (again): ": superuser_password}):
        run('python3 manage.py createsuperuser --username admin '
            '--email admin@admin.com')
    return


def collect_static():
    sudo('python3 manage.py collectstatic --no-input')
    return


def create_nginx_symlink_from_tpl(tpl_filename):
    sudo('PROJECT_PATH=%s PROJECT_NAME=%s envtpl '
         'configs/%s --keep-template' % (PROJECT_PATH, PROJECT_NAME,
                                         tpl_filename))
    sudo('ln -sf %s/configs/nginx.conf '
         '/etc/nginx/nginx.conf' % (os.path.join(PROJECT_PATH, PROJECT_NAME)))
    sudo('service nginx restart')
    return


def create_uwsgi_config_from_tpl(tpl_filename):
    sudo('PROJECT_PATH=%s PROJECT_NAME=%s '
         'envtpl configs/%s --keep-template' % (PROJECT_PATH, PROJECT_NAME,
                                                tpl_filename))
    sudo('uwsgi --ini configs/uwsgi.ini')
    return


def initialize_env_vars():
    secret_key = os.getenv('SECRET_KEY')
    raven_dsn = os.getenv('RAVEN_DSN')
    return shell_env(SECRET_KEY=secret_key, RAVEN_DSN=raven_dsn,
                     DB_NAME=DB_NAME, DB_PASSWORD=DB_PASSWORD)


@task
def bootstrap():
    install_system_packages()
    recreate_database()
    change_postgres_user_password(DB_PASSWORD)
    clone_or_pull_git_repo()
    install_pip_requirements()
    with cd(PROJECT_ROOT):
        with initialize_env_vars():
            with prefix('source bin/activate'):
                create_dj_superuser()
                collect_static()
                create_nginx_symlink_from_tpl('nginx.conf.tpl')
                create_uwsgi_config_from_tpl('uwsgi.ini.tpl')
