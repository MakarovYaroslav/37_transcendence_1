[uwsgi]

# Настройки, связанные с Django
# Корневая папка проекта (полный путь)
chdir           = {{ PROJECT_PATH }}/{{ PROJECT_NAME }}/
# Django wsgi файл
module          = social_network.wsgi
# полный путь к виртуальному окружению
home            = {{ PROJECT_PATH }}/{{ PROJECT_NAME }}/

# общие настройки
# master
master          = true
# максимальное количество процессов
processes       = 10
# полный путь к файлу сокета
socket          = {{ PROJECT_PATH }}/{{ PROJECT_NAME }}/social_network.sock
# права доступа к файлу сокета
chmod-socket    = 666
# очищать окружение от служебных файлов uwsgi по завершению
vacuum          = true