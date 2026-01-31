import os
import asyncio
import logging
import re
import sys
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler


# ========== HTTP SERVER FOR RENDER ==========
class HealthHandler(BaseHTTPRequestHandler):
    """Простой HTTP сервер для Render"""

    def do_GET(self):
        if self.path in ['/', '/health', '/ping']:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK - Bot is running')
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
    print(f'🌐 Health check: http://0.0.0.0:{port}/health')
    print(f'🤖 Telegram бот запускается...')
    server.serve_forever()


# Запускаем HTTP сервер в отдельном потоке
http_thread = Thread(target=run_http_server, daemon=True)
http_thread.start()

# ========== TELEGRAM BOT ==========
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Получаем переменные окружения Render
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id]
MANAGER_USERNAME = os.getenv("MANAGER_USERNAME", "@manager")

# Проверка токена
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN не найден!")
    logger.error("Добавьте в Render Environment Variables: BOT_TOKEN=ваш_токен")
    sys.exit(1)

# Инициализация бота
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


# ------------------ ОСНОВНЫЕ КОМАНДЫ ------------------

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    logger.info(f"👤 Новый пользователь: {message.from_user.id}")

    # Уведомляем админа (если есть)
    if ADMIN_IDS:
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(
                    admin_id,
                    f"👤 <b>Новый пользователь:</b>\n\n"
                    f"ID: {message.from_user.id}\n"
                    f"Имя: {message.from_user.full_name}\n"
                    f"Юзернейм: @{message.from_user.username if message.from_user.username else 'не указан'}"
                )
            except Exception as e:
                logger.error(f"Не удалось отправить админу {admin_id}: {e}")

    await message.answer(
        "🚀 <b>Добро пожаловать в сервис продвижения малого бизнеса!</b>\n\n"
        "Мы помогаем предпринимателям:\n"
        "• 📱 Вести соцсетях (SMM)\n"
        "• 🛍 Продвигать товары на маркетплейсах\n"
        "• 📊 Настраивать рекламу\n"
        "• 💰 Увеличивать продажи\n\n"
        "Выберите нужный раздел ниже ⤵️",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="🏢 О компании"), types.KeyboardButton(text="📦 Услуги")],
                [types.KeyboardButton(text="💰 Цены"), types.KeyboardButton(text="📞 Контакты")],
                [types.KeyboardButton(text="📝 Оставить заявку")]
            ],
            resize_keyboard=True
        )
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "🆘 <b>Помощь по боту</b>\n\n"
        "Доступные команды:\n"
        "/start - Перезапустить бота\n"
        "/help - Эта справка\n"
        "/price - Цены на услуги\n"
        "/contact - Контакты менеджера\n"
        "/request - Быстрая заявка\n\n"
        "Или используйте кнопки меню ⬇️"
    )


@dp.message(Command("price"))
async def cmd_price(message: types.Message):
    await message.answer(
        "💰 <b>Наши цены:</b>\n\n"
        "• SMM ведение: 15-30 тыс. ₽/мес\n"
        "• Маркетплейсы: 12-25 тыс. ₽/мес\n"
        "• Настройка рекламы: 12-20 тыс. ₽/мес\n"
        "• Комплексное: от 35 тыс. ₽/мес\n\n"
        "Для точного расчета оставьте заявку."
    )


@dp.message(Command("contact"))
async def cmd_contact(message: types.Message):
    await message.answer(
        f"📞 <b>Контакты менеджера:</b>\n\n"
        f"Telegram: {MANAGER_USERNAME}\n\n"
        f"<i>Ответим в течение 15 минут в рабочее время</i>"
    )


@dp.message(Command("request"))
async def cmd_request(message: types.Message):
    await message.answer(
        "📝 <b>Оставить быструю заявку:</b>\n\n"
        "Напишите:\n"
        "1. Ваше имя\n"
        "2. Номер телефона\n"
        "3. Какая услуга интересует\n\n"
        "Например:\n"
        "<i>Иван, +79991234567, нужна настройка рекламы</i>"
    )


# ------------------ МЕНЮ ------------------

@dp.message(F.text == "🏢 О компании")
async def about_company(message: types.Message):
    await message.answer(
        "🏢 <b>О компании</b>\n\n"
        "Мы — команда экспертов в digital-маркетинге с 8-летним опытом.\n\n"
        "<b>Наши достижения:</b>\n"
        "• 150+ успешных проектов\n"
        "• Средний рост продаж: +45% за 3 месяца\n"
        "• ROI рекламы: от 300%\n\n"
        "<b>Специализация:</b>\n"
        "• Instagram, ВКонтакте, Telegram\n"
        "• Wildberries, Ozon, Яндекс.Маркет\n"
        "• Собственные маркетплейсы"
    )


@dp.message(F.text == "📦 Услуги")
async def services(message: types.Message):
    await message.answer(
        "📦 <b>Наши услуги:</b>\n\n"
        "<u>1. Продвижение в соцсетях (SMM):</u>\n"
        "• Стратегия контента\n"
        "• Ведение аккаунтов\n"
        "• Таргетированная реклама\n"
        "• Аналитика и отчеты\n\n"
        "<u>2. Маркетплейсы:</u>\n"
        "• Настройка карточек товаров\n"
        "• SEO-оптимизация\n"
        "• Работа с отзывами\n"
        "• Управление рекламой\n\n"
        "<u>3. Настройка рекламы:</u>\n"
        "• Анализ целевой аудитории\n"
        "• Настройка таргета в соцсетях\n"
        "• Настройка контекстной рекламы\n"
        "• Анализ эффективности\n\n"
        "<u>4. Комплексное продвижение:</u>\n"
        "• Полный цикл\n"
        "• Ежемесячные отчеты\n"
        "• Персональный менеджер"
    )


@dp.message(F.text == "💰 Цены")
async def prices(message: types.Message):
    await cmd_price(message)


@dp.message(F.text == "📞 Контакты")
async def contacts(message: types.Message):
    await cmd_contact(message)


@dp.message(F.text == "📝 Оставить заявку")
async def create_request(message: types.Message):
    await message.answer(
        "📝 <b>Форма заявки</b>\n\n"
        "Пожалуйста, напишите:\n\n"
        "1. <b>Ваше имя</b>\n"
        "2. <b>Номер телефона</b>\n"
        "3. <b>Какая услуга интересует</b>\n\n"
        "Или используйте команду /request для быстрой заявки."
    )


# ------------------ ОБРАБОТКА ЗАЯВОК ------------------

@dp.message(F.text.regexp(r'(заявка|нужно|интересует|помощь|стоимость)', flags=re.IGNORECASE))
async def handle_request(message: types.Message):
    # Уведомляем админа о заявке
    if ADMIN_IDS:
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(
                    admin_id,
                    f"📥 <b>Новое сообщение от клиента:</b>\n\n"
                    f"ID: {message.from_user.id}\n"
                    f"Имя: {message.from_user.full_name}\n"
                    f"Юзернейм: @{message.from_user.username if message.from_user.username else 'не указан'}\n"
                    f"Текст: {message.text}"
                )
            except Exception as e:
                logger.error(f"Не удалось отправить админу {admin_id}: {e}")

    await message.answer(
        "✅ <b>Ваше сообщение получено!</b>\n\n"
        "Менеджер свяжется с вами в ближайшее время.\n\n"
        f"Также вы можете написать напрямую: {MANAGER_USERNAME}"
    )


# ------------------ ОБРАБОТКА ЛЮБЫХ СООБЩЕНИЙ ------------------

@dp.message()
async def echo_message(message: types.Message):
    if message.text and not message.text.startswith('/'):
        await message.answer(
            "🤖 <b>Бот понимает команды:</b>\n\n"
            "• /start - главное меню\n"
            "• /help - помощь\n"
            "• /price - цены\n"
            "• /contact - контакты\n"
            "• /request - оставить заявку\n\n"
            "Или используйте кнопки меню ⬆️"
        )


# ------------------ ЗАПУСК БОТА ------------------

async def main():
    """Основная функция запуска бота"""
    # Получаем информацию о боте
    bot_info = await bot.get_me()
    logger.info(f"🤖 Бот: @{bot_info.username}")
    logger.info(f"🆔 ID бота: {bot_info.id}")
    logger.info(f"👨‍💼 Менеджер: {MANAGER_USERNAME}")
    logger.info(f"👥 Админы: {ADMIN_IDS}")
    logger.info(f"🌐 HTTP порт: {os.environ.get('PORT', 10000)}")

    # Удаляем вебхук, если был
    await bot.delete_webhook(drop_pending_updates=True)

    # Запускаем polling
    logger.info("🚀 Запуск Telegram бота для продвижения бизнеса...")
    await dp.start_polling(bot)


# ------------------ ОБРАБОТКА СИГНАЛОВ ------------------

def signal_handler(signum, frame):
    """Обработчик сигналов завершения"""
    logger.info(f"🛑 Получен сигнал {signum}, завершение работы...")
    sys.exit(0)


# ------------------ ТОЧКА ВХОДА ------------------

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 ЗАПУСК ПРИЛОЖЕНИЯ НА RENDER.COM")
    print(f"🔧 Режим: {'Production' if BOT_TOKEN else 'Development'}")
    print(f"🤖 Бот токен: {'Установлен' if BOT_TOKEN else 'Отсутствует'}")
    print(f"👥 Админы: {ADMIN_IDS if ADMIN_IDS else 'Не указаны'}")
    print("=" * 50)

    # Регистрируем обработчики сигналов
    import signal

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        # Запускаем бота
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹ Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
        logger.info("♻️ Перезапуск через 10 секунд...")
        import time

        time.sleep(10)