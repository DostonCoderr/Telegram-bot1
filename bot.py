import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TELEGRAM_TOKEN = "7565266404:AAFKzQAe5kfSIklO7ixGoKKbWQ7DhtRukXI"
OPENROUTER_API_KEY = "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"


API_URL = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}


current_model = "openai/gpt-3.5-turbo"


users_data = {} 


available_models = {
    "GPT-3.5": "openai/gpt-3.5-turbo",
    "GPT-4": "openai/gpt-4",
    "Mixtral": "mistralai/mixtral-8x7b-instruct"
}

async def ask_ai(question: str, user_id: int) -> str:
    """OpenRouter API orqali AI javobi olish"""
    try:
        model_to_use = current_model
        payload = {
            "model": model_to_use,
            "messages": [{"role": "user", "content": question}],
            "max_tokens": 200,
            "temperature": 0.7
        }
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        else:
            return "😅 Javob topilmadi."
    except Exception as e:
        return f"❌ Xatolik: {e}"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id


    keyboard = [
        [InlineKeyboardButton("🇺🇿 O‘zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🌐 Iltimos, tilni tanlang:", reply_markup=reply_markup)


async def lang_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    lang = query.data.split("_")[1] 


    users_data[user_id] = {"lang": lang, "name": None}

    await query.edit_message_text("📛 Iltimos, ismingizni kiriting:")

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_text = update.message.text

    # Faqat agar user til tanlagan bo‘lsa
    if user_id in users_data and users_data[user_id]["name"] is None:
        users_data[user_id]["name"] = user_text
        await update.message.reply_text(
            f"✅ Salom, {user_text}! Endi savol berishingiz mumkin."
        )
    else:

        answer = await ask_ai(user_text, user_id)
        await update.message.reply_text(answer)
async def choose_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🤖 GPT-3.5", callback_data="openai/gpt-3.5-turbo")],
        [InlineKeyboardButton("🚀 GPT-4", callback_data="openai/gpt-4")],
        [InlineKeyboardButton("⚡ Mixtral", callback_data="mistralai/mixtral-8x7b-instruct")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📌 Iltimos, modelni tanla:", reply_markup=reply_markup)

# Model callback
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_model
    query = update.callback_query
    await query.answer()

    if query.data.startswith("openai") or query.data.startswith("mistralai"):
        current_model = query.data
        await query.edit_message_text(text=f"✅ Model tanlandi: {current_model}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(lang_button, pattern="^lang_")) 
    app.add_handler(CallbackQueryHandler(button_handler))  
    app.add_handler(CommandHandler("model", choose_model))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_name))

    app.run_polling()

if __name__ == "__main__":
    main()
