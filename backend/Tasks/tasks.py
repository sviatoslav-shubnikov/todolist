from aiogram import Bot, types
import os
import asyncio
import requests
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import urlencode
from django.conf import settings
from django.core.cache import cache
from celery import shared_task
from datetime import datetime
import sys
from pathlib import Path
from django.utils import timezone
from django.utils.timezone import localtime
import pytz


TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_MAIN_BOT_TOKEN')



@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def send_telegram_notification(self, chat_id: int, message: str):

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        print(f"🔐 Telegram Token: {TELEGRAM_BOT_TOKEN}")
        response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})

        print(f"📤 Sending to: {chat_id}")
        print(f"📨 Message: {message}")
        response.raise_for_status()
        return True
    
    except Exception as e:
        print(f"Ошибка отправки уведомления: {e}")
        self.retry(exc=e, countdown=60)


@shared_task
def check_overdue_tasks():

    # ADAK_TZ = pytz.timezone("America/Adak")

    from ToDoList.models import Task
    now = localtime()
    overdue_tasks = Task.objects.filter(
        DueDate__lt=now,
        Status=Task.StatusChoices.PENDING,
        IsNotified=False
    ).select_related('User')

    print(f"🔍 Найдено просроченных задач: {overdue_tasks.count()}")
    print(f"🕒 Текущее время: {now.isoformat()}")
    for task in overdue_tasks:
        message = (
            f"⏰ <b>Просроченная задача!</b>\n"
            f"📌 {task.Title}\n"
           f"📅 Дедлайн: {localtime(task.DueDate).strftime('%d.%m.%Y %H:%M')}\n"
            f"ℹ️ {task.Description or 'Нет описания'}"
        )
        send_telegram_notification.delay(chat_id=task.User.TelegramId, message=message)
        task.Status = Task.StatusChoices.OVERDUE
        task.IsNotified = True
        task.save()