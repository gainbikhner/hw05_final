# YaTube

Социальная сеть для публикации дневников.  
Разработана по классической MVT архитектуре. Используется пагинация постов и кэширование. Регистрация реализована с верификацией данных, сменой и восстановлением пароля через почту. Написаны тесты, проверяющие работу сервиса.

## Автор

https://github.com/gainbikhner

## Стек технологий

- Python 3.9
- Django 2.2.19

## Инструкция

1. Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:gainbikhner/hw05_final.git
cd hw05_final
```

2. Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
source env/bin/activate
```

3. Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

4. Выполнить миграции:

```
python3 manage.py migrate
```

5. Запустить проект:

```
python3 manage.py runserver
```

6. Создать юзера для админки:

```
python3 manage.py createsuperuser
```
