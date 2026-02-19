import requests
import json
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ---------- НАСТРОЙКИ ----------
TELEGRAM_TOKEN = "8527747303:AAFBqfIptwci2CDaB-tT8eJq_XTymRzqjwg"
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzJZo-z_RghykX9z-F-XxYd2lL-yxDsEF_7Ya72kuzAmUT7uwrSRKVyLu_rGaIoBc1Thg/exec"  # из шага 2

# ---------- ФОРМАТ СООБЩЕНИЯ ----------
# Пример: ангел + слеза богов + титаниум = крылья
# или: ангел + слеза богов = ❌
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # Парсим
    try:
        if '=' not in text:
            await update.message.reply_text("❌ Формат: основа + ингр1 + ингр2 ... = результат (или ❌)")
            return
        
        left, right = text.split('=', 1)
        result = right.strip()
        success = result != '❌'
        
        parts = left.split('+')
        base = parts[0].strip()
        ingredients = [p.strip() for p in parts[1:]] if len(parts) > 1 else []
        
        if not base or not ingredients:
            await update.message.reply_text("❌ Нужна хотя бы основа и один ингредиент")
            return
        
        # Отправляем в Google Sheets
        payload = {
            "base": base,
            "ingredients": ingredients,
            "result": result if success else "",
            "success": success
        }
        
        response = requests.post(GOOGLE_SCRIPT_URL, json=payload)
        if response.status_code == 200 and response.text == "OK":
            await update.message.reply_text("✅ Записано!")
        else:
            await update.message.reply_text("⚠️ Ошибка при записи в таблицу")
            
    except Exception as e:
        await update.message.reply_text(f"🔥 Ошибка: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот для крафтов.\n"
        "Присылай результаты в формате:\n"
        "ангел + слеза богов + титаниум = крылья\n"
        "или\n"
        "ангел + слеза богов = ❌ (если провал)"
    )

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
