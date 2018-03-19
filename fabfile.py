import os
from fabric.api import cd, env, prefix, sudo, task, settings
from fabric.contrib.files import exists

PROJECT_NAME = os.getenv('PROJECT_NAME')
DB_NAME = os.getenv('DB_NAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
PROJECT_PATH = os.getenv('PROJECT_PATH')
PROJECT_ROOT = PROJECT_PATH + '/' + PROJECT_NAME
VENV_DIR = os.path.join(PROJECT_ROOT, '.venv')
REPO = '%s/%s.git' % (os.getenv('USER_REPO'), PROJECT_NAME)

env.hosts = [os.getenv('HOST')]
env.environment = 'staging'
env.user = os.getenv('HOST_USER')
env.password = os.getenv('HOST_PASSWORD')


def install_system_packages():
    with settings(prompts={'Do you want to continue? [Y/n] ': 'Y'}):
        sudo('apt-get install python3')
        sudo('apt-get install nginx')
        sudo('apt-get install python3-pip python3-dev libpq-dev postgresql '
             'postgresql-contrib')
        sudo('apt-get install git')
        sudo('pip3 install virtualenv')
    return


def recreate_database():
    try:
        sudo('su - postgres psql -c "dropdb %s"' % DB_NAME)
    except:
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
    sudo('python3 manage.py migrate')
    superuser_password = os.getenv('SUPERUSER_PASSWORD')
    with settings(prompts={"Password: ": superuser_password,
                           "Password (again): ": superuser_password}):
        sudo('python3 manage.py createsuperuser --username admin '
             '--email admin@admin.com')
    return


def collect_static():
    with settings(prompts={"Type 'yes' to continue, or 'no' "
                           "to cancel: ": 'yes'}):
        sudo('python3 manage.py collectstatic')
    return


def create_nginx_symlink_from_tpl(tpl_filename):
    sudo('PROJECT_PATH=$PROJECT_PATH PROJECT_NAME=$PROJECT_NAME envtpl '
         'configs/%s --keep-template' % tpl_filename)
    sudo('ln -sf %s/%s/configs/nginx.conf '
         '/etc/nginx/nginx.conf' % (PROJECT_PATH, PROJECT_NAME))
    sudo('service nginx restart')
    return


def create_uwsgi_config_from_tpl(tpl_filename):
    sudo('PROJECT_PATH=$PROJECT_PATH PROJECT_NAME=$PROJECT_NAME '
         'envtpl configs/%s --keep-template' % tpl_filename)
    sudo('uwsgi --ini configs/uwsgi.ini')
    return


@task
def bootstrap():
    install_system_packages()
    recreate_database()
    change_postgres_user_password(DB_PASSWORD)
    clone_or_pull_git_repo()
    install_pip_requirements()
    with cd(PROJECT_ROOT):
        with prefix('source envs.txt && source bin/activate'):
            create_dj_superuser()
            collect_static()
            create_nginx_symlink_from_tpl('nginx.conf.tpl')
            create_uwsgi_config_from_tpl('uwsgi.ini.tpl')