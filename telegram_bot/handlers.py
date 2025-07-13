# telegram_bot/handlers.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_config, save_config, get_stats, save_stats

# состояния FSM
STATE_PROPOSAL, STATE_TARGET = range(2)

# кнопки главного меню
def main_keyboard(config):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Состояние: {'✅' if config['enabled'] else '❌'}", callback_data="toggle_enabled")],
        [InlineKeyboardButton(f"Демпинг: {'✅' if config['dumping'] else '❌'}", callback_data="toggle_dumping")],
        [InlineKeyboardButton(f"Адаптация: {'✅' if config['adaptive'] else '❌'}", callback_data="toggle_adaptive")],
        [InlineKeyboardButton("Статистика", callback_data="show_stats")],
        [InlineKeyboardButton("Настройки", callback_data="settings_menu")],
    ])

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config = get_config()
    if update.effective_user.id not in config.get("whitelist", []):
        await update.message.reply_text("⛔️ Доступ запрещён")
        return
    await update.message.reply_text("⚙️ Главное меню:", reply_markup=main_keyboard(config))

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    config = get_config()
    stats = get_stats()
    user_id = query.from_user.id
    if user_id not in config.get("whitelist", []):
        await query.edit_message_text("⛔️ Доступ запрещён")
        return

    data = query.data

    if data == "toggle_enabled":
        config["enabled"] = not config["enabled"]
        save_config(config)
        await query.edit_message_text("⚙️ Главное меню:", reply_markup=main_keyboard(config))

    elif data == "toggle_dumping":
        config["dumping"] = not config["dumping"]
        save_config(config)
        await query.edit_message_text("⚙️ Главное меню:", reply_markup=main_keyboard(config))

    elif data == "toggle_adaptive":
        config["adaptive"] = not config["adaptive"]
        save_config(config)
        await query.edit_message_text("⚙️ Главное меню:", reply_markup=main_keyboard(config))

    elif data == "show_stats":
        text = (
            f"📊 Статистика:\n"
            f"✅ Принято с демпингом: {stats['taken_with_dump']}\n"
            f"📦 Принято без демпинга: {stats['taken_without_dump']}\n"
            f"❌ Отказано: {stats['rejected']}\n"
            f"🔍 Отфильтровано: {stats['filtered_out']}"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Сбросить статистику", callback_data="reset_stats")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
        ])
        await query.edit_message_text(text, reply_markup=keyboard)

    elif data == "reset_stats":
        stats.update({"taken_with_dump": 0, "taken_without_dump": 0, "rejected": 0, "filtered_out": 0})
        save_stats(stats)
        await query.edit_message_text("✅ Статистика сброшена.", reply_markup=main_keyboard(config))

    elif data == "settings_menu":
        target = config["target"]
        prop = config["proposal"]
        text = (
            f"⚙️ Настройки:\n"
            f"📦 Моё предложение: {prop['tons']} т, {prop['price']} KZT/т\n"
            f"🎯 Таргет: {target['location']}, {target['min_volume']}-{target['max_volume']} т, от {target['min_price']} KZT/т"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📥 Установить предложение", callback_data="set_proposal")],
            [InlineKeyboardButton("🎯 Установить таргет", callback_data="set_target")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")],
        ])
        await query.edit_message_text(text, reply_markup=keyboard)

    elif data == "set_proposal":
        await query.edit_message_text("Введите два значения через пробел: [тонн] [цена]")
        return STATE_PROPOSAL

    elif data == "set_target":
        await query.edit_message_text("Введите через пробел: [локация] [мин.объём] [макс.объём] [мин.цена] \n(локация '-' = игнорировать)" )
        return STATE_TARGET

    elif data == "back_to_main":
        await query.edit_message_text("⚙️ Главное меню:", reply_markup=main_keyboard(config))

    return -1

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config = get_config()
    user_id = update.effective_user.id
    if user_id not in config.get("whitelist", []):
        return

    text = update.message.text.strip()
    state = context.user_data.get("state")

    if state == STATE_PROPOSAL:
        try:
            tons, price = map(int, text.split())
            config["proposal"] = {"tons": tons, "price": price}
            save_config(config)
            await update.message.reply_text("✅ Моё предложение обновлено")
        except:
            await update.message.reply_text("⚠️ Неверный формат. Пример: 30 8000")
    elif state == STATE_TARGET:
        try:
            loc, minv, maxv, minp = text.split()
            config["target"] = {
                "location": loc,
                "min_volume": int(minv),
                "max_volume": int(maxv),
                "min_price": int(minp)
            }
            save_config(config)
            await update.message.reply_text("✅ Таргет обновлён")
        except:
            await update.message.reply_text("⚠️ Неверный формат. Пример: almaty 20 60 7800")

    context.user_data["state"] = None
    await update.message.reply_text("⚙️ Главное меню:", reply_markup=main_keyboard(config))