# telegram_bot/main.py

import asyncio
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters
)

from telegram_bot.handlers import (
    start,
    button_handler,
    input_tons,
    input_price,
    input_location,
    input_min_vol,
    input_max_vol,
    input_min_price,
    cancel,
    STATE_TONS,
    STATE_PRICE,
    STATE_LOC,
    STATE_MIN_VOL,
    STATE_MAX_VOL,
    STATE_MIN_PRICE
)

from config import get_config


async def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    config = get_config()
    app = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()

    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(button_handler)
        ],
        states={
            STATE_TONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_tons)],
            STATE_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_price)],
            STATE_LOC: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_location)],
            STATE_MIN_VOL: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_min_vol)],
            STATE_MAX_VOL: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_max_vol)],
            STATE_MIN_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_min_price)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    await app.run_polling()


if __name__ == '__main__':
    asyncio.run(main())
