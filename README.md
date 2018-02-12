# Проект "Превосходство"

Данный проект подразумевает создание социальной сети, в которой необходимы регистрация, профили, стена, личные сообщения и АПИ для взаимодействия с этим всем.
И главное – нужен робот, который будет эмулировать действия пользователя. 
Планируется запустить несколько таких социальных сетей, кучу роботов и с помощью этого моделировать поведение реальных пользователей в реальных соцсетях и изучать их таким образом.

# Итерация 1 (данный репозиторий)
1.1. В ходе первой итерации создан и настроен базовый проект для социальной сети на Django 2.0.

1.2. Создан view для просмотра информации о пользователе.

1.3. Настроено логирование ошибок в Sentry.

1.4. Добавлено использование django-configurations для управления конфигурациями.

# Деплой на localhost
Шаг 1. Установить требуемые зависимости.
```
sudo pip3 install -r requirements.txt
```
Шаг 2. Зарегистрироваться на [Sentry](https://sentry.io/), получить Client Key (DSN).

Шаг 3. Заменить имеющееся значение RAVEN_DSN на полученный Client Key в параметрах окружения (файл *envs.txt*).

После этого ошибки, возникающие при работе приложения, будут логироваться в ваш аккаунт и отправляться вам на почту.

Шаг 4. Заменить значение переменной окружения SECRET_KEY на своё значение в файле *envs.txt*.

Шаг 5. Установить параметры окружения, введя в консоли
```
source envs.txt
```

Шаг 6. При необходимости поменять значение 'DevelopmentConfig' на 'ProductionConfig' в файлах *manage.py* и *wsgi.py*.

В этом случае DEBUG=False, т.е. ошибки не будут подробно отображаться при работе приложения.

Шаг 7. Выполнить миграции и обновить базу данных.
```
python3 manage.py migrate
```

Шаг 8. Создать аккаунт суперпользователя (администратора). Для этого ввести команду
```
python3 manage.py createsuperuser
```
и заполнить требуемые поля.

Шаг 9. Запустить приложение на локальном сервере.
```
python3 manage.py runserver
```

После этого приложение будет доступно по [данной ссылке](http://localhost:8000/).

Необходимо зайти в [панель администратора](http://localhost:8000/admin/) и создать нового пользователя.

Просмотр информации о пользователе доступен по [данной ссылке](http://localhost:8000/users/1/), где последняя часть адреса - это id пользователя.

# Цели проекта

Код написан в учебных целях. Обучающие курсы для веб-разработчиков - [DEVMAN.org](https://devman.org)
