from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update
import os
import logging
from dotenv import load_dotenv
import json
from datetime import datetime
import asyncio
import aiofiles

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load environment variables
TOKEN = input("token: ")

# Create necessary directories
os.makedirs("chat/message/video", exist_ok=True)
os.makedirs("chat/message/photo", exist_ok=True)
os.makedirs("chat/message/audio", exist_ok=True)

def get_user_identifier(user):
    """Get the best available user identifier"""
    if user.username:
        return user.username
    elif user.first_name:
        return user.first_name
    elif user.id:
        return f"user_{user.id}"
    return "unknown_user"

async def save_message_to_json(message_data):
    chat_history_file = "./chat_history.json"
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(chat_history_file), exist_ok=True)
    
    # Read existing history
    try:
        async with aiofiles.open(chat_history_file, 'r') as f:
            content = await f.read()
            history = json.loads(content) if content else []
    except FileNotFoundError:
        history = []
    
    # Append new message
    history.append(message_data)
    
    # Save updated history
    async with aiofiles.open(chat_history_file, 'w') as f:
        await f.write(json.dumps(history, indent=2))

async def store_bot_response(chat_id, response_text):
    """Store bot's response in chat history"""
    message_data = {
        "type": "text",
        "sender": "bot",
        "chat_id": chat_id,
        "timestamp": datetime.now().isoformat(),
        "content": response_text
    }
    await save_message_to_json(message_data)

async def download_file(file, file_type, context):
    new_file = await context.bot.get_file(file.file_id)
    file_ext = os.path.splitext(new_file.file_path)[1]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}{file_ext}"
    
    chat_path = f"chat/message/{file_type}/{filename}"
    await new_file.download_to_drive(chat_path)
    
    return filename

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    chat_id = update.message.chat_id
    user = get_user_identifier(update.message.from_user)
    timestamp = datetime.now().isoformat()
    
    if message.lower() == "read_chat_history":
        try:
            async with aiofiles.open("./message/chat_history.json", 'r') as f:
                content = await f.read()
                response_text = "Chat History:\n" + content
                await update.message.reply_text(response_text)
                await store_bot_response(chat_id, response_text)
        except FileNotFoundError:
            response_text = "No chat history found."
            await update.message.reply_text(response_text)
            await store_bot_response(chat_id, response_text)
        return

    # Store user message data
    message_data = {
        "type": "text",
        "sender": "user",
        "username": user,
        "chat_id": chat_id,
        "timestamp": timestamp,
        "content": message
    }
    await save_message_to_json(message_data)
    
    # Send and store bot's response
    response_text = f"Received your text message: {message}"
    await update.message.reply_text(response_text)
    await store_bot_response(chat_id, response_text)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    chat_id = update.message.chat_id
    user = get_user_identifier(update.message.from_user)
    timestamp = datetime.now().isoformat()
    
    filename = await download_file(photo, "photo", context)
    
    message_data = {
        "type": "photo",
        "sender": "user",
        "username": user,
        "chat_id": chat_id,
        "timestamp": timestamp,
        "file_path": f"./photo/{filename}",
        "caption": update.message.caption if update.message.caption else ""
    }
    await save_message_to_json(message_data)
    
    # Send and store bot's response
    response_text = f"Received your photo! Saved as {filename}"
    await update.message.reply_text(response_text)
    await store_bot_response(chat_id, response_text)

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video
    chat_id = update.message.chat_id
    user = get_user_identifier(update.message.from_user)
    timestamp = datetime.now().isoformat()
    
    filename = await download_file(video, "video", context)
    
    message_data = {
        "type": "video",
        "sender": "user",
        "username": user,
        "chat_id": chat_id,
        "timestamp": timestamp,
        "file_path": f"./video/{filename}",
        "caption": update.message.caption if update.message.caption else ""
    }
    await save_message_to_json(message_data)
    
    # Send and store bot's response
    response_text = f"Received your video! Saved as {filename}"
    await update.message.reply_text(response_text)
    await store_bot_response(chat_id, response_text)

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    audio = update.message.audio
    chat_id = update.message.chat_id
    user = get_user_identifier(update.message.from_user)
    timestamp = datetime.now().isoformat()
    
    filename = await download_file(audio, "audio", context)
    
    message_data = {
        "type": "audio",
        "sender": "user",
        "username": user,
        "chat_id": chat_id,
        "timestamp": timestamp,
        "file_path": f"./audio/{filename}",
        "caption": update.message.caption if update.message.caption else ""
    }
    await save_message_to_json(message_data)
    
    # Send and store bot's response
    response_text = f"Received your audio! Saved as {filename}"
    await update.message.reply_text(response_text)
    await store_bot_response(chat_id, response_text)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user = get_user_identifier(update.message.from_user)
    response_text = (
        "👋 Hello! I'm your chat bot. I can:\n"
        "1. Store all messages and media\n"
        "2. Show chat history (type 'read_chat_history')\n"
        "3. Handle text, photos, videos, and audio"
    )
    
    # Store user's /start command
    await save_message_to_json({
        "type": "command",
        "sender": "user",
        "username": user,
        "chat_id": chat_id,
        "timestamp": datetime.now().isoformat(),
        "content": "/start"
    })
    
    # Send and store bot's response
    await update.message.reply_text(response_text)
    await store_bot_response(chat_id, response_text)

def main():
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    
    # Add message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.AUDIO, handle_audio))

    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()