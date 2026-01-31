import os
import asyncio
import logging
import sys
import json
import datetime
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from aiogram.client.default import DefaultBotProperties


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
        pass


def run_http_server():
    """Запуск HTTP сервера в отдельном потоке"""
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f'✅ HTTP сервер запущен на порту {port}')
    print(f'🌐 Health check: http://0.0.0.0:{port}/health')
    server.serve_forever()


# ========== TELEGRAM БОТ ==========
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode

# Получаем токен из переменных окружения
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    print("❌ BOT_TOKEN не найден! Добавьте в Environment Variables на Render")
    sys.exit(1)

# Инициализация бота с новым синтаксисом для aiogram 3.7.0+
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# ========== КОНФИГУРАЦИЯ ==========
class Config:
    # НЕ ВСТАВЛЯЙТЕ ТОКЕН СЮДА! Используйте переменные окружения в Render
    BOT_TOKEN = BOT_TOKEN  # Используем переменную, полученную из os.environ
    ADMIN_IDS = [123456789]  # Замените на ваш Telegram ID
    MANAGER_USERNAME = "@ваш_менеджер"  # Замените на реальный username менеджера


# ========== СООБЩЕНИЯ ==========
class Messages:
    WELCOME_MESSAGE = """<b>🚀 Добро пожаловать в сервис продвижения малого бизнеса!</b>

Мы помогаем предпринимателям:
• 📱 Вести соцсети (SMM)
• 🛍 Продвигать товары на маркетплейсах
• 📊 Настраивать рекламу
• 💰 Увеличивать продажи

Выберите нужный раздел ниже ⤵️
"""

    ABOUT_COMPANY = """<b>🏢 О компании</b>

Мы — команда экспертов в digital-маркетинге с 8-летним опытом. 
Работаем удаленно по всей России.

<b>Наши достижения:</b>
• 150+ успешных проектов
• Средний рост продаж: +45% за 3 месяца
• ROI рекламы: от 300%

<b>Специализация:</b>
• Instagram, ВКонтакте, Telegram
• Wildberries, Ozon, Яндекс.Маркет
• Собственные маркетплейсы
"""

    SERVICES = """<b>📦 Наши услуги</b>

<u>1. Продвижение в соцсетях (SMM):</u>
• Стратегия контента
• Ведение аккаунтов
• Таргетированная реклама
• Аналитика и отчеты
• <i>от 15 000₽/мес</i>

<u>2. Маркетплейсы:</u>
• Настройка карточек товаров
• SEO-оптимизация
• Работа с отзывами
• Управление рекламой
• <i>от 12 000₽/мес</i>

<u>3. Настройка рекламы:</u>
• Анализ целевой аудитории
• Настройка таргета в соцсетях
• Настройка контекстной рекламы (Яндекс.Директ, Google Ads)
• Анализ эффективности
• <i>от 12 000₽/мес</i>

<u>4. Комплексное продвижение:</u>
• Полный цикл: от анализа до реализации
• Ежемесячные отчеты
• Персональный менеджер
• <i>от 35 000₽/мес</i>
"""

    FAQ = """<b>❓ Частые вопросы</b>

<b>1. Сколько времени нужно для первых результатов?</b>
Первые результаты видны через 2-4 недели. Значительный рост — через 3 месяца.

<b>2. Нужен ли мне свой контент?</b>
Можем работать с вашими материалами или создавать контент с нуля.

<b>3. Какой бюджет нужен на рекламу?</b>
Минимальный бюджет: от 10 000₽/мес. Оптимальный: 25 000-50 000₽/мес.

<b>4. Даете ли вы гарантии?</b>
Да, гарантируем рост ключевых метрик или возвращаем деньги.
"""

    CONTACTS = """<b>📞 Контакты</b>

Telegram менеджера: {manager_username}

<b>Режим работы:</b>
Пн-Пт: 9:00-18:00
Сб: 10:00-15:00
Вс: выходной

<b>Работаем онлайн по всей России</b>
"""

    CASE_STUDIES = """<b>📊 Наши кейсы</b>

<u>Кейс 1: Магазин косметики</u>
• Проблема: низкая узнаваемость в Instagram
• Решение: стратегия контента + таргет
• Результат: +1200 подписчиков за месяц, 45 заказов

<u>Кейс 2: Производитель сумок на WB</u>
• Проблема: товар на 50+ странице поиска
• Решение: SEO + промо-кампания
• Результат: топ-10 в категории, рост продаж в 3 раза

<u>Кейс 3: Кофейня с доставкой</u>
• Проблема: нет онлайн-продаж
• Решение: Telegram-бот + реклама
• Результат: 60+ заказов в день с бота
"""


# ========== КЛАВИАТУРЫ ==========
class Keyboards:
    @staticmethod
    def get_main_menu():
        return types.ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(text="🏢 О компании"),
                    types.KeyboardButton(text="📦 Услуги")
                ],
                [
                    types.KeyboardButton(text="💰 Рассчитать стоимость"),
                    types.KeyboardButton(text="📊 Наши кейсы")
                ],
                [
                    types.KeyboardButton(text="❓ FAQ"),
                    types.KeyboardButton(text="📞 Контакты")
                ],
                [
                    types.KeyboardButton(text="👨‍💼 Связаться с менеджером"),
                    types.KeyboardButton(text="📝 Оставить заявку")
                ]
            ],
            resize_keyboard=True
        )

    @staticmethod
    def get_services_keyboard():
        return types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(text="SMM", callback_data="service_smm"),
                    types.InlineKeyboardButton(text="Маркетплейсы", callback_data="service_marketplaces")
                ],
                [
                    types.InlineKeyboardButton(text="Реклама", callback_data="service_ads"),
                    types.InlineKeyboardButton(text="Комплекс", callback_data="service_complex")
                ],
                [
                    types.InlineKeyboardButton(text="Telegram боты", callback_data="service_bot")
                ]
            ]
        )

    @staticmethod
    def get_contact_keyboard():
        return types.ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)
                ],
                [
                    types.KeyboardButton(text="↩️ Назад")
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )

    @staticmethod
    def get_budget_keyboard():
        return types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(text="10-25 тыс. ₽", callback_data="budget_10_25"),
                    types.InlineKeyboardButton(text="25-50 тыс. ₽", callback_data="budget_25_50")
                ],
                [
                    types.InlineKeyboardButton(text="50-100 тыс. ₽", callback_data="budget_50_100"),
                    types.InlineKeyboardButton(text="100+ тыс. ₽", callback_data="budget_100_plus")
                ]
            ]
        )

    @staticmethod
    def get_manager_keyboard(user_id):
        return types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="📥 Взять заявку в работу",
                        callback_data=f"take_lead_{user_id}"
                    )
                ]
            ]
        )


# ========== БАЗА ДАННЫХ (JSON вместо SQLite) ==========
class Database:
    def __init__(self, filename='leads.json'):
        self.filename = filename

    def _load_data(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {'users': [], 'leads': []}

    def _save_data(self, data):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    def add_user(self, user_id, username, full_name):
        data = self._load_data()

        # Проверяем, есть ли уже пользователь
        for user in data['users']:
            if user['user_id'] == user_id:
                return user

        # Добавляем нового пользователя
        user = {
            'user_id': user_id,
            'username': username,
            'full_name': full_name,
            'created_at': datetime.datetime.now().isoformat()
        }
        data['users'].append(user)
        self._save_data(data)
        return user

    def add_lead(self, user_id, service_type, business_type, budget, contact_preference, name, phone):
        data = self._load_data()

        lead = {
            'id': len(data['leads']) + 1,
            'user_id': user_id,
            'service_type': service_type,
            'business_type': business_type,
            'budget': budget,
            'contact_preference': contact_preference,
            'name': name,
            'phone': phone,
            'status': 'new',
            'created_at': datetime.datetime.now().isoformat()
        }
        data['leads'].append(lead)
        self._save_data(data)
        return lead

    def get_user_count(self):
        data = self._load_data()
        return len(data['users'])

    def get_leads_count(self):
        data = self._load_data()
        return len(data['leads'])

    def get_new_leads_count(self):
        data = self._load_data()
        return sum(1 for lead in data['leads'] if lead['status'] == 'new')

    def update_lead_status(self, lead_id, status, manager_id=None):
        data = self._load_data()
        for lead in data['leads']:
            if lead['id'] == lead_id:
                lead['status'] = status
                if manager_id:
                    lead['manager_id'] = manager_id
                self._save_data(data)
                return True
        return False


# Инициализация базы данных
db = Database()


# ========== СОСТОЯНИЯ ДЛЯ ФОРМЫ ЗАЯВКИ ==========
class ApplicationForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_service = State()
    waiting_for_business = State()
    waiting_for_budget = State()
    waiting_for_contact = State()


# ========== ОБРАБОТЧИКИ КОМАНД ==========
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Сохраняем пользователя в БД
    user = db.add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name
    )

    # Уведомляем админов о новом пользователе
    for admin_id in Config.ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"👤 <b>Новый пользователь:</b>\n\n"
                f"ID: {message.from_user.id}\n"
                f"Имя: {message.from_user.full_name}\n"
                f"Юзернейм: @{message.from_user.username}\n"
                f"Дата: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}"
            )
        except:
            pass

    await message.answer(
        Messages.WELCOME_MESSAGE,
        reply_markup=Keyboards.get_main_menu()
    )


@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if message.from_user.id not in Config.ADMIN_IDS:
        return

    user_count = db.get_user_count()
    leads_count = db.get_leads_count()
    new_leads = db.get_new_leads_count()

    await message.answer(
        f"📊 <b>Панель администратора</b>\n\n"
        f"👥 Пользователей: {user_count}\n"
        f"📥 Заявок всего: {leads_count}\n"
        f"🆕 Новых заявок: {new_leads}\n\n"
        f"<i>Файл с данными: leads.json</i>"
    )


# ========== ОСНОВНОЕ МЕНЮ ==========
@dp.message(F.text == "🏢 О компании")
async def about_company(message: types.Message):
    await message.answer(Messages.ABOUT_COMPANY)


@dp.message(F.text == "📦 Услуги")
async def services(message: types.Message):
    await message.answer(
        Messages.SERVICES,
        reply_markup=Keyboards.get_services_keyboard()
    )


@dp.message(F.text == "❓ FAQ")
async def faq(message: types.Message):
    await message.answer(Messages.FAQ)


@dp.message(F.text == "📞 Контакты")
async def contacts(message: types.Message):
    contact_message = Messages.CONTACTS.replace("{manager_username}", Config.MANAGER_USERNAME)
    await message.answer(contact_message)


@dp.message(F.text == "📊 Наши кейсы")
async def cases(message: types.Message):
    await message.answer(Messages.CASE_STUDIES)


@dp.message(F.text == "👨‍💼 Связаться с менеджером")
async def contact_manager(message: types.Message):
    await message.answer(
        f"📞 <b>Связь с менеджером</b>\n\n"
        f"Напишите напрямую: {Config.MANAGER_USERNAME}\n\n"
        f"<i>Ответим в течение 15 минут в рабочее время</i>"
    )


# ========== ФОРМА ЗАЯВКИ ==========
@dp.message(F.text == "📝 Оставить заявку")
async def start_application(message: types.Message, state: FSMContext):
    await message.answer(
        "📋 <b>Заполните заявку</b>\n\n"
        "Введите ваше имя и фамилию:"
    )
    await state.set_state(ApplicationForm.waiting_for_name)


@dp.message(ApplicationForm.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        "📱 <b>Контактные данные</b>\n\n"
        "Отправьте номер телефона или нажмите кнопку ниже:",
        reply_markup=Keyboards.get_contact_keyboard()
    )
    await state.set_state(ApplicationForm.waiting_for_phone)


@dp.message(ApplicationForm.waiting_for_phone, F.contact)
async def process_contact(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    await ask_service_type(message, state)


@dp.message(ApplicationForm.waiting_for_phone)
async def process_phone_text(message: types.Message, state: FSMContext):
    if message.text == "↩️ Назад":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=Keyboards.get_main_menu())
        return

    await state.update_data(phone=message.text)
    await ask_service_type(message, state)


async def ask_service_type(message: types.Message, state: FSMContext):
    await message.answer(
        "🎯 <b>Выберите услугу:</b>",
        reply_markup=Keyboards.get_services_keyboard()
    )
    await state.set_state(ApplicationForm.waiting_for_service)


@dp.callback_query(F.data.startswith("service_"))
async def process_service(callback: types.CallbackQuery, state: FSMContext):
    service_map = {
        "service_smm": "Продвижение в соцсетях (SMM)",
        "service_marketplaces": "Маркетплейсы",
        "service_ads": "Настройка рекламы",
        "service_complex": "Комплексное продвижение",
        "service_bot": "Разработка бота"
    }

    service = service_map.get(callback.data, callback.data)
    await state.update_data(service=service)

    await callback.message.answer(
        "🏢 <b>Опишите ваш бизнес:</b>\n\n"
        "Например: 'Интернет-магазин одежды', "
        "'Кофейня', 'Услуги ремонта' и т.д."
    )
    await state.set_state(ApplicationForm.waiting_for_business)
    await callback.answer()


@dp.message(ApplicationForm.waiting_for_business)
async def process_business(message: types.Message, state: FSMContext):
    await state.update_data(business=message.text)

    await message.answer(
        "💰 <b>Примерный бюджет на продвижение:</b>",
        reply_markup=Keyboards.get_budget_keyboard()
    )
    await state.set_state(ApplicationForm.waiting_for_budget)


@dp.callback_query(F.data.startswith("budget_"))
async def process_budget(callback: types.CallbackQuery, state: FSMContext):
    budget_map = {
        "budget_10_25": "10-25 тыс. ₽",
        "budget_25_50": "25-50 тыс. ₽",
        "budget_50_100": "50-100 тыс. ₽",
        "budget_100_plus": "100+ тыс. ₽"
    }

    budget = budget_map.get(callback.data, callback.data)
    await state.update_data(budget=budget)

    await callback.message.answer(
        "📞 <b>Как с вами удобнее связаться?</b>\n\n"
        "Напишите предпочтительный способ связи:\n"
        "• Telegram\n• WhatsApp\n• Телефонный звонок\n• Email"
    )
    await state.set_state(ApplicationForm.waiting_for_contact)
    await callback.answer()


@dp.message(ApplicationForm.waiting_for_contact)
async def process_contact_pref(message: types.Message, state: FSMContext):
    data = await state.get_data()

    # Сохраняем заявку в БД
    lead = db.add_lead(
        user_id=message.from_user.id,
        service_type=data['service'],
        business_type=data['business'],
        budget=data['budget'],
        contact_preference=message.text,
        name=data['name'],
        phone=data.get('phone', 'Не указан')
    )

    # Формируем сообщение для клиента
    await message.answer(
        f"✅ <b>Заявка #{lead['id']} принята!</b>\n\n"
        f"<b>Ваши данные:</b>\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data.get('phone', 'Не указан')}\n"
        f"Услуга: {data['service']}\n"
        f"Бизнес: {data['business']}\n"
        f"Бюджет: {data['budget']}\n"
        f"Связь: {message.text}\n\n"
        f"Менеджер свяжется с вами в течение часа в рабочее время.",
        reply_markup=Keyboards.get_main_menu()
    )

    # Отправляем уведомление всем админам
    for admin_id in Config.ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"🆕 <b>НОВАЯ ЗАЯВКА #{lead['id']}</b>\n\n"
                f"👤 Клиент: {data['name']}\n"
                f"ID: {message.from_user.id}\n"
                f"Юзернейм: @{message.from_user.username}\n"
                f"📱 Телефон: {data.get('phone', 'Не указан')}\n"
                f"🎯 Услуга: {data['service']}\n"
                f"🏢 Бизнес: {data['business']}\n"
                f"💰 Бюджет: {data['budget']}\n"
                f"📞 Способ связи: {message.text}",
                reply_markup=Keyboards.get_manager_keyboard(message.from_user.id)
            )
        except Exception as e:
            print(f"Ошибка отправки админу {admin_id}: {e}")

    await state.clear()


# ========== РАССЧЕТ СТОИМОСТИ ==========
@dp.message(F.text == "💰 Рассчитать стоимость")
async def calculate_cost(message: types.Message):
    await message.answer(
        "🧮 <b>Калькулятор стоимости</b>\n\n"
        "Примерные цены:\n"
        "• SMM ведение: 15-30 тыс. ₽/мес\n"
        "• Маркетплейсы: 12-25 тыс. ₽/мес\n"
        "• Настройка рекламы: 12-20 тыс. ₽/мес\n"
        "• Комплекс: от 35 тыс. ₽/мес\n\n"
        "Для точного расчета оставьте заявку, "
        "и наш менеджер сделает персональное предложение."
    )


# ========== ОБРАБОТКА ОТ МЕНЕДЖЕРА ==========
@dp.callback_query(F.data.startswith("take_lead_"))
async def take_lead(callback: types.CallbackQuery):
    user_id = int(callback.data.replace("take_lead_", ""))

    # В реальном приложении здесь была бы логика обновления статуса заявки в БД
    # Для упрощения просто отправляем уведомление
    await callback.answer("✅ Заявка взята в работу!")

    # Уведомляем клиента
    try:
        await bot.send_message(
            user_id,
            f"👋 <b>Вашей заявкой занялся менеджер!</b>\n\n"
            f"Скоро он с вами свяжется.\n"
            f"Если есть срочные вопросы, пишите: {Config.MANAGER_USERNAME}"
        )
    except:
        pass


# ========== ЗАПУСК БОТА ==========
async def start_bot():
    print("🤖 Запуск бота для продвижения бизнеса...")
    await dp.start_polling(bot)


def main():
    """Главная функция"""
    print('=' * 50)
    print('🚀 ЗАПУСК БОТА ДЛЯ ПРОДВИЖЕНИЯ БИЗНЕСА')
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
        print(f'❌ Критическая ошибка: {e}')
        print('♻️ Перезапуск через 10 секунд...')
        time.sleep(10)


if __name__ == '__main__':
    main()