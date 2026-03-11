import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import os

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID  = int(os.environ.get("ADMIN_ID", "0"))

BOOK = {
    "title":  "Парень из Алмалыка",
    "author": "Альберт",
    "desc": (
        "📖 *Парень из Алмалыка* — реальная история 24-летнего парня из Узбекистана.\n\n"
        "Ему было два года, когда умерла мама. Отец ушёл. Сестра Кристина в 15 лет взяла "
        "братишку на руки — и не отпускала двадцать лет.\n\n"
        "Школа, армия, попытка в спецназ, кредит, работа без зарплаты — и Виктория, "
        "которую он любил молча *десять лет*.\n\n"
        "История о потерях, силе и любви. Настоящая. Без украшений."
    ),
    "price_digital": "15 000 сум / 149 ₽",
    "price_print":   "99 000 сум / 990 ₽",
}

ASK_FORMAT, ASK_NAME, ASK_ADDRESS = range(3)

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("📖 О книге",              callback_data="about")],
        [InlineKeyboardButton("💰 Цены",                 callback_data="prices")],
        [InlineKeyboardButton("🛒 Заказать книгу",       callback_data="order")],
        [InlineKeyboardButton("📞 Связаться с автором",  callback_data="contact")],
    ]
    await update.message.reply_text(
        f"👋 Привет! Добро пожаловать!\n\n"
        f"📗 *{BOOK['title']}*\n"
        f"✍️ Автор: {BOOK['author']}\n\n"
        f"Выбери что тебя интересует 👇",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )

async def about(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    kb = [
        [InlineKeyboardButton("🛒 Заказать", callback_data="order")],
        [InlineKeyboardButton("◀️ Назад",    callback_data="back")],
    ]
    await q.edit_message_text(
        BOOK["desc"],
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )

async def prices(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    kb = [
        [InlineKeyboardButton("🛒 Заказать", callback_data="order")],
        [InlineKeyboardButton("◀️ Назад",    callback_data="back")],
    ]
    await q.edit_message_text(
        f"💰 *Цены на книгу*\n\n"
        f"📱 *Электронная книга (PDF)*\n"
        f"   {BOOK['price_digital']}\n"
        f"   ✅ Мгновенная доставка на email\n\n"
        f"📗 *Печатная книга*\n"
        f"   {BOOK['price_print']}\n"
        f"   ✅ С иллюстрациями · Доставка по Узбекистану",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )

async def order_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    kb = [
        [InlineKeyboardButton(f"📱 Электронная — {BOOK['price_digital']}", callback_data="fmt_digital")],
        [InlineKeyboardButton(f"📗 Печатная — {BOOK['price_print']}",      callback_data="fmt_print")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back")],
    ]
    await q.edit_message_text(
        "🛒 *Оформление заказа*\n\nВыбери формат книги 👇",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )
    return ASK_FORMAT

async def ask_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    fmt = "📱 Электронная книга" if q.data == "fmt_digital" else "📗 Печатная книга"
    ctx.user_data["format"] = fmt
    await q.edit_message_text(
        f"✅ Выбрано: *{fmt}*\n\n✏️ Напиши своё *имя* 👇",
        parse_mode="Markdown"
    )
    return ASK_NAME

async def ask_address(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["name"] = update.message.text
    fmt = ctx.user_data.get("format", "")
    if "Электронная" in fmt:
        await update.message.reply_text(
            f"👋 Привет, *{update.message.text}*!\n\n📧 Напиши свой *email* — пришлю книгу туда:",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"👋 Привет, *{update.message.text}*!\n\n📦 Напиши *адрес доставки*\n_(город, улица, дом, квартира)_",
            parse_mode="Markdown"
        )
    return ASK_ADDRESS

async def finish_order(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    name    = ctx.user_data.get("name", "—")
    fmt     = ctx.user_data.get("format", "—")
    address = update.message.text
    user    = update.effective_user
    price   = BOOK["price_digital"] if "Электронная" in fmt else BOOK["price_print"]

    await update.message.reply_text(
        f"✅ *Заказ принят!*\n\n"
        f"📗 {BOOK['title']}\n"
        f"📦 Формат: {fmt}\n"
        f"💰 Сумма: {price}\n"
        f"👤 Имя: {name}\n"
        f"📍 Адрес/Email: {address}\n\n"
        f"⏳ Автор свяжется с тобой скоро!\n"
        f"Или напиши напрямую: @albert_457 💙",
        parse_mode="Markdown"
    )

    if ADMIN_ID:
        try:
            await ctx.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    f"🔔 *НОВЫЙ ЗАКАЗ!*\n\n"
                    f"👤 {user.full_name} (@{user.username or '—'})\n"
                    f"📗 Формат: {fmt}\n"
                    f"💰 Цена: {price}\n"
                    f"🏷 Имя: {name}\n"
                    f"📍 Адрес/Email: {address}\n\n"
                    f"👉 Написать покупателю: tg://user?id={user.id}"
                ),
                parse_mode="Markdown"
            )
        except Exception as e:
            logging.warning(f"Ошибка уведомления: {e}")

    return ConversationHandler.END

async def contact(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    kb = [[InlineKeyboardButton("◀️ Назад", callback_data="back")]]
    await q.edit_message_text(
        f"📞 *Связаться с автором*\n\n"
        f"✈️ Telegram: @albert_457\n\n"
        f"Пиши — отвечу быстро! 😊",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )

async def back(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    kb = [
        [InlineKeyboardButton("📖 О книге",             callback_data="about")],
        [InlineKeyboardButton("💰 Цены",                callback_data="prices")],
        [InlineKeyboardButton("🛒 Заказать книгу",      callback_data="order")],
        [InlineKeyboardButton("📞 Связаться с автором", callback_data="contact")],
    ]
    await q.edit_message_text(
        f"📗 *{BOOK['title']}*\n✍️ Автор: {BOOK['author']}\n\nВыбери что тебя интересует 👇",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )

async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Отменено. Напиши /start чтобы начать заново.")
    return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(order_start, pattern="^order$")],
        states={
            ASK_FORMAT:  [CallbackQueryHandler(ask_name, pattern="^fmt_")],
            ASK_NAME:    [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_address)],
            ASK_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, finish_order)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(about,   pattern="^about$"))
    app.add_handler(CallbackQueryHandler(prices,  pattern="^prices$"))
    app.add_handler(CallbackQueryHandler(contact, pattern="^contact$"))
    app.add_handler(CallbackQueryHandler(back,    pattern="^back$"))
    print("🤖 Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
