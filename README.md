# Telegram Assistant (Event-driven keyword monitor)

A lightweight Telegram client built on top of Telethon, designed to monitor incoming messages, detect predefined keywords, and forward relevant content to a target chat.

The project focuses on reliability, controlled runtime behavior, and production-like constraints such as reconnect limits, activity windows, and safe message delivery.

---

## Features

- Keyword-based message filtering (case-insensitive, regex-safe)
- Human-like message sending (delays + typing simulation)
- Activity schedule (only works during configured hours)
- Reconnect protection (prevents infinite restart loops)
- File-based locking (no parallel runs)
- Graceful handling of Telegram API limits (FloodWait)
- Structured logging for observability

---

## Tech Stack

- Python 3.11+
- Telethon
- Pydantic Settings
- Asyncio
- Pytest

---

## Project Structure

app/ → core logic
config/ → configuration
tests/ → unit tests


---
## Configuration

Create `.env` file:
    API_ID=your_api_id
    API_HASH=your_api_hash


---
## Run
python -m app.main

---




## Design Notes

This project intentionally avoids:
- aggressive auto-reconnect loops
- unrealistic message bursts
- tight polling cycles

Instead, it mimics real user behavior and includes safeguards that would be expected in a production automation tool.

---

## Use Cases

- Marketplace monitoring (e.g. detecting specific products)
- Lead generation
- Personal notification pipelines

---

# 🇷🇺 Русская версия

## Описание

Асинхронный Telegram-клиент для отслеживания входящих сообщений и пересылки только тех, которые содержат заданные ключевые слова.

Проект сделан с упором на:
- стабильность
- предсказуемое поведение
- ограничения, близкие к реальным условиям эксплуатации

---

## Возможности

- Фильтрация по ключевым словам
- Имитация поведения человека (задержки, “печатает…”)
- Работа по расписанию
- Защита от бесконечных реконнектов
- Блокировка параллельного запуска
- Обработка FloodWait
- Подробные логи

---

## Запуск

python -m app.main


---

## Зачем это всё

Проект демонстрирует:

- работу с асинхронным кодом
- архитектуру небольшого сервиса
- контроль состояния приложения
- обработку ошибок внешнего API

Подходит как pet-project для middle Python / backend / automation позиций.



## ⚙️ Установка

```bash
git clone https://github.com/kod1984/tg-assistant
python -m venv .venv
pip install -r requirements.txt
.venv/bin/python -m app.main

## Запуск как демона 
sudo nano /etc/systemd/system/tg-assistant.service
[Unit]
Description=Telegram Assistant
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/tg-assistant

ExecStart=/opt/tg-assistant/.venv/bin/python -m app.main

# ❌ ВАЖНО: никаких рестартов
Restart=no

# (опционально) чтобы лог был живой в journalctl
StandardOutput=journal
StandardError=journal

Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target


sudo systemctl daemon-reload
sudo systemctl start tg-assistant
sudo systemctl status tg-assistant
