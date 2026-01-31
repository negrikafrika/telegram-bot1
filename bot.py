import os
import asyncio
import logging
import sys
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler


# ========== HTTP СЕРВЕР ДЛЯ HEALTH CHECK ==========
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ['/', '/health', '/ping']:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Отключаем логирование


def run_http_server():
    """Запуск HTTP сервера в отдельном потоке"""
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f'✅ HTTP сервер запущен на порту {port}')
    print(f'🌐 Health check доступен: http://0.0.0.0:{port}/health')
    server.serve_forever()


# ========== TELEGRAM БОТ - ВАШ ПОЛНЫЙ КОД ==========
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Получаем токен
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    logger.error('❌ BOT_TOKEN не найден!')
    logger.error('Добавьте переменную BOT_TOKEN в настройках Render/Railway')
    sys.exit(1)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# ========== ВАШИ СОСТОЯНИЯ ==========
class ApplicationForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_service = State()
    waiting_for_business = State()
    waiting_for_budget = State()
    waiting_for_contact = State()


# ========== ВАШИ КЛАВИАТУРЫ ==========
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='📝 Оставить заявку')],
            [KeyboardButton(text='ℹ️ О нас'), KeyboardButton(text='💼 Услуги')],
            [KeyboardButton(text='📞 Контакты')]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_services_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='🌐 Сайт')],
            [KeyboardButton(text='📱 Мобильное приложение')],
            [KeyboardButton(text='🤖 Telegram бот')],
            [KeyboardButton(text='🔙 Назад')]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_budget_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='до 50k'), KeyboardButton(text='50k-100k')],
            [KeyboardButton(text='100k-200k'), KeyboardButton(text='200k+')],
            [KeyboardButton(text='🔙 Назад')]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


# ========== ВАШИ ОБРАБОТЧИКИ КОМАНД ==========
@dp.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer(
        '👋 <b>Добро пожаловать!</b>\n\n'
        'Я помогу вам создать цифровой продукт. '
        'Выберите действие ниже:',
        reply_markup=get_main_keyboard()
    )


@dp.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer(
        '📋 <b>Доступные команды:</b>\n\n'
        '/start - Начать диалог\n'
        '/help - Показать это сообщение\n'
        '/cancel - Отменить текущую заявку\n\n'
        'Используйте кнопки для навигации.',
        reply_markup=get_main_keyboard()
    )


@dp.message(Command('cancel'))
@dp.message(F.text == '🔙 Назад')
async def cmd_cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer('❌ Нет активной заявки для отмены.')
        return

    await state.clear()
    await message.answer(
        '✅ Заявка отменена.\n'
        'Вы вернулись в главное меню.',
        reply_markup=get_main_keyboard()
    )


# ========== ВАШИ ОБРАБОТЧИКИ КНОПОК ==========
@dp.message(F.text == '📝 Оставить заявку')
async def start_application(message: Message, state: FSMContext):
    await state.set_state(ApplicationForm.waiting_for_name)
    await message.answer(
        '📝 <b>Начнем оформление заявки!</b>\n\n'
        'Шаг 1 из 6\n'
        'Как к вам обращаться? Введите ваше имя:',
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text='🔙 Назад')]],
            resize_keyboard=True
        )
    )


@dp.message(F.text == 'ℹ️ О нас')
async def about_us(message: Message):
    await message.answer(
        '🏢 <b>О нашей компании:</b>\n\n'
        'Мы - команда разработчиков, создающая качественные цифровые продукты. '
        'Специализируемся на:\n'
        '• Веб-разработке\n'
        '• Мобильных приложениях\n'
        '• Telegram ботах\n\n'
        'Опыт работы: 5+ лет',
        reply_markup=get_main_keyboard()
    )


@dp.message(F.text == '💼 Услуги')
async def services(message: Message):
    await message.answer(
        '🛠 <b>Наши услуги:</b>\n\n'
        'Выберите интересующую услугу:',
        reply_markup=get_services_keyboard()
    )


@dp.message(F.text == '📞 Контакты')
async def contacts(message: Message):
    await message.answer(
        '📱 <b>Наши контакты:</b>\n\n'
        'Telegram: @ваш_логин\n'
        'Email: info@example.com\n'
        'Сайт: example.com\n\n'
        'Рабочие часы: Пн-Пт, 10:00-19:00',
        reply_markup=get_main_keyboard()
    )


# ========== ВАШИ ОБРАБОТЧИКИ FSM ==========
# Шаг 1: Имя
@dp.message(ApplicationForm.waiting_for_name, F.text != '🔙 Назад')
async def process_name(message: Message, state: FSMContext):
    if len(message.text) < 2:
        await message.answer('❌ Имя должно содержать минимум 2 символа. Попробуйте еще:')
        return

    await state.update_data(name=message.text)
    await state.set_state(ApplicationForm.waiting_for_phone)
    await message.answer(
        '✅ Имя сохранено!\n\n'
        'Шаг 2 из 6\n'
        'Введите ваш номер телефона (например, +79991234567):'
    )


# Шаг 2: Телефон
@dp.message(ApplicationForm.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    if message.text == '🔙 Назад':
        await state.set_state(ApplicationForm.waiting_for_name)
        await message.answer('Введите ваше имя:')
        return

    phone = message.text
    if not phone.replace('+', '').replace(' ', '').isdigit():
        await message.answer('❌ Пожалуйста, введите корректный номер телефона:')
        return

    await state.update_data(phone=phone)
    await state.set_state(ApplicationForm.waiting_for_service)
    await message.answer(
        '✅ Телефон сохранен!\n\n'
        'Шаг 3 из 6\n'
        'Выберите интересующую услугу:',
        reply_markup=get_services_keyboard()
    )


# Шаг 3: Услуга
@dp.message(ApplicationForm.waiting_for_service)
async def process_service(message: Message, state: FSMContext):
    if message.text == '🔙 Назад':
        await state.set_state(ApplicationForm.waiting_for_phone)
        await message.answer('Введите ваш номер телефона:')
        return

    await state.update_data(service=message.text)
    await state.set_state(ApplicationForm.waiting_for_business)
    await message.answer(
        '✅ Услуга выбрана!\n\n'
        'Шаг 4 из 6\n'
        'Опишите ваш бизнес или проект (2-3 предложения):'
    )


# Шаг 4: Бизнес
@dp.message(ApplicationForm.waiting_for_business)
async def process_business(message: Message, state: FSMContext):
    if message.text == '🔙 Назад':
        await state.set_state(ApplicationForm.waiting_for_service)
        await message.answer('Выберите услугу:', reply_markup=get_services_keyboard())
        return

    if len(message.text) < 10:
        await message.answer('❌ Пожалуйста, опишите подробнее (минимум 10 символов):')
        return

    await state.update_data(business=message.text)
    await state.set_state(ApplicationForm.waiting_for_budget)
    await message.answer(
        '✅ Информация сохранена!\n\n'
        'Шаг 5 из 6\n'
        'Выберите примерный бюджет:',
        reply_markup=get_budget_keyboard()
    )


# Шаг 5: Бюджет
@dp.message(ApplicationForm.waiting_for_budget)
async def process_budget(message: Message, state: FSMContext):
    if message.text == '🔙 Назад':
        await state.set_state(ApplicationForm.waiting_for_business)
        await message.answer('Опишите ваш бизнес или проект:')
        return

    await state.update_data(budget=message.text)
    await state.set_state(ApplicationForm.waiting_for_contact)
    await message.answer(
        '✅ Бюджет выбран!\n\n'
        'Шаг 6 из 6\n'
        'Как с вами удобнее связаться?\n'
        'Напишите предпочтительный способ (Telegram, WhatsApp, звонок):'
    )


# Шаг 6: Контакт и финализация
@dp.message(ApplicationForm.waiting_for_contact)
async def process_contact(message: Message, state: FSMContext):
    if message.text == '🔙 Назад':
        await state.set_state(ApplicationForm.waiting_for_budget)
        await message.answer('Выберите бюджет:', reply_markup=get_budget_keyboard())
        return

    await state.update_data(contact_preference=message.text)
    user_data = await state.get_data()

    # Формируем сообщение
    summary = (
        '✅ <b>Заявка успешно отправлена!</b>\n\n'
        f'<b>Имя:</b> {user_data.get("name")}\n'
        f'<b>Телефон:</b> {user_data.get("phone")}\n'
        f'<b>Услуга:</b> {user_data.get("service")}\n'
        f'<b>Бюджет:</b> {user_data.get("budget")}\n\n'
        'Спасибо! Мы свяжемся с вами в ближайшее время.'
    )

    await message.answer(summary, reply_markup=get_main_keyboard())
    await state.clear()

    # Логируем заявку
    logger.info(f'Новая заявка от пользователя {message.from_user.id}: {user_data}')


# ========== ЗАПУСК БОТА ==========
async def start_bot():
    """Запуск Telegram бота"""
    logger.info('🤖 Запуск Telegram бота...')
    await bot.delete_webhook(drop_pending_updates=True)

    bot_info = await bot.get_me()
    logger.info(f'🤖 Бот: @{bot_info.username}')
    logger.info(f'🆔 ID: {bot_info.id}')
    logger.info('✅ Бот готов к работе!')

    # Запускаем polling
    await dp.start_polling(bot, skip_updates=True)


def main():
    """Главная функция"""
    print('=' * 50)
    print('🚀 ЗАПУСК TELEGRAM БОТА С FSM')
    print('=' * 50)

    # Запускаем HTTP сервер для health check в отдельном потоке
    http_thread = Thread(target=run_http_server, daemon=True)
    http_thread.start()

    # Даем время серверу запуститься
    import time
    time.sleep(3)

    # Запускаем бота
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print('\n⏹ Бот остановлен')
    except Exception as e:
        logger.error(f'❌ Критическая ошибка: {e}')
        print('♻️ Перезапуск через 10 секунд...')
        time.sleep(10)


if __name__ == '__main__':
    main()