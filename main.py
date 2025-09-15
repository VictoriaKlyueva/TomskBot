from telegram.ext import Application, CommandHandler, MessageHandler, filters

from logger import logger
from yandex_gpt_bot import YandexGPTBot
from constants import TELEGRAM_TOKEN
from command_handler import *
from yandex_gpt_bot import YandexGPTBot

yandex_bot = YandexGPTBot()

def main():
    try:
        # Проверяем возможность генерации токена при запуске
        yandex_bot.get_iam_token()
        logger.info("IAM token test successful")

        application = Application.builder().token(TELEGRAM_TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_error_handler(error_handler)

        logger.info("Бот запускается...")
        application.run_polling()

    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")


if __name__ == "__main__":
    main()
