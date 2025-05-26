## Инструкция по запуску
1. Клонировать репозиторий
 git clone <your-repository-url>
 cd todolist

2. Создать файлы .env, где есть .env_sample файлы(backend, Celery, TelegramBot)

3. Запуск проекта и работоспособность
 - Выполнить команду для запуска: docker-compose up --build 
 - Выполнить команды:
	1. docker ps(для просмотра создавшихся контейнеров)
	2. Выбираем поле где todolist-backend_service и копируем ID контейнера, выполняем команду: docker exec -it <ID контейнера> /bin/bash
	3. Выполняем команды для миграций: 
		- python manage.py makemigrations
		- python manage.py migrate
	4. После выполняем команду: python manage.py createsuperuser для создания супер пользователя для входа в админку


## Архитектура проекта
Проект состоит из следующих основных компонентов:

Django Rest Framework Backend - основной сервис управления задачами

Telegram Bot (на aiogram и aiogram-dialog) - интерфейс для пользователей

Celery - обработка асинхронных задач и уведомлений

PostgreSQL - основное хранилище данных

Redis - брокер сообщений для Celery и кеширование