import logging
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# === Конфигурация ===
TOKEN = "8413434299:AAHy9DsgSJQXI6v5Ga2IYMeXPe6Cub-c8hg"
SPREADSHEET_NAME = "for_an_interview"
SHEET_NAME = "Задача 3"

google_creds_json = os.getenv("GOOGLE_CREDENTIALS")
google_creds_dict = json.loads(google_creds_json)

# === Логирование ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# === Google Sheets подключение ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(google_creds_dict, scope)
client = gspread.authorize(creds)

# === Состояния для ConversationHandler ===
ASK_EMAIL = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне свой email, и я запишу его в таблицу.")
    return ASK_EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()

    try:
        # Открываем таблицу и лист
        sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)
        sheet.append_row([email])
        await update.message.reply_text(f"✅ Email {email} успешно добавлен в лист '{SHEET_NAME}'.")
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await update.message.reply_text("❌ Ошибка при добавлении email.")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменено.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
