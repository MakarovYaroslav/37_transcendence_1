import os
from fabric.api import cd, env, prefix, sudo, task, settings, run, shell_env
from fabric.contrib.files import exists

PROJECT_NAME = os.getenv('PROJECT_NAME')
DB_NAME = os.getenv('DB_NAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
PROJECT_PATH = os.getenv('PROJECT_PATH')
PROJECT_ROOT = os.path.join(PROJECT_PATH, PROJECT_NAME)
REPO = '%s/%s.git' % (os.getenv('USER_REPO'), PROJECT_NAME)

env.hosts = ['%s@%s:%s' % (os.getenv('HOST_USER'), os.getenv('HOST'),
                           os.getenv('HOST_PORT'))]
env.user = os.getenv('HOST_USER')
env.password = os.getenv('HOST_PASSWORD')


def install_system_packages():
    sudo('apt-get -y install python3')
    sudo('apt-get -y install nginx')
    sudo('apt-get -y install python3-pip python3-dev libpq-dev postgresql '
         'postgresql-contrib')
    sudo('apt-get -y install git')
    run('pip3 install virtualenv --user')


def create_database():
    with settings(warn_only=True):
        sudo('su - postgres psql -c "createdb %s"' % DB_NAME)


def change_postgres_user_password():
    command = "alter user postgres with password '%s'" % DB_PASSWORD
    sudo('sudo -u postgres psql -c "%s"' % command)


def clone_or_pull_git_repo():
    if not exists(PROJECT_ROOT, use_sudo=True):
        sudo('mkdir -p %s' % PROJECT_PATH)
        sudo('chown -R %s %s' % (env.user, PROJECT_PATH))
        with(cd(PROJECT_PATH)):
            run('git clone %s' % REPO)
    else:
        with cd(PROJECT_ROOT):
            run('git pull origin')


def install_pip_requirements():
    with cd(PROJECT_PATH):
        run('python3 -m virtualenv %s' % PROJECT_NAME)
    with cd(PROJECT_ROOT):
        run('source bin/activate && pip3 install -r requirements.txt')


def create_dj_superuser():
    run('python3 manage.py migrate')
    superuser_password = os.getenv('SUPERUSER_PASSWORD')
    with settings(prompts={"Password: ": superuser_password,
                           "Password (again): ": superuser_password}):
        run('python3 manage.py createsuperuser --username admin '
            '--email admin@admin.com')


def collect_static():
    run('python3 manage.py collectstatic --no-input')


def create_nginx_symlink_from_tpl(tpl_filename):
    nginx_path = os.path.join('/etc', 'nginx')
    run('PROJECT_PATH=%s PROJECT_NAME=%s envtpl %s --keep-template' % (
        PROJECT_PATH, PROJECT_NAME, os.path.join('configs', tpl_filename)))
    sudo('chmod -R 777 %s' % nginx_path)
    run('ln -sf %s %s' % (
        os.path.join(PROJECT_PATH, PROJECT_NAME, 'configs', 'nginx.conf'),
        os.path.join(nginx_path, 'nginx.conf')))
    sudo('service nginx restart')


def create_uwsgi_config_from_tpl(tpl_filename):
    run('PROJECT_PATH=%s PROJECT_NAME=%s envtpl %s --keep-template' % (
        PROJECT_PATH, PROJECT_NAME, os.path.join('configs', tpl_filename)))
    run('uwsgi --ini configs/uwsgi.ini')


def initialize_env_vars():
    secret_key = os.getenv('SECRET_KEY')
    raven_dsn = os.getenv('RAVEN_DSN')
    return shell_env(SECRET_KEY=secret_key, RAVEN_DSN=raven_dsn,
                     DB_NAME=DB_NAME, DB_PASSWORD=DB_PASSWORD)


@task
def bootstrap():
    install_system_packages()
    change_postgres_user_password()
    create_database()
    clone_or_pull_git_repo()
    install_pip_requirements()
    with cd(PROJECT_ROOT), initialize_env_vars(), prefix('source bin/activate'):
        create_dj_superuser()
        collect_static()
        create_nginx_symlink_from_tpl('nginx.conf.tpl')
        create_uwsgi_config_from_tpl('uwsgi.ini.tpl')
