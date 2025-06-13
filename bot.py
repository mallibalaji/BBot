import os
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def convert_video_to_ac3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video or update.message.document
    if not video:
        await update.message.reply_text("Send a valid video file.")
        return

    await update.message.reply_text("Downloading video...")

    file = await context.bot.get_file(video.file_id)
    input_path = f"input_{file.file_unique_id}.mp4"
    output_path = f"output_{file.file_unique_id}.mp4"

    await file.download_to_drive(input_path)

    await update.message.reply_text("Converting audio to AC3...")

    ffmpeg_command = [
        "ffmpeg", "-i", input_path,
        "-c:v", "copy",
        "-c:a", "ac3",
        "-q:a", "0",
        output_path
    ]

    try:
        subprocess.run(ffmpeg_command, check=True)
        await update.message.reply_text("Uploading converted video...")
        await update.message.reply_video(video=open(output_path, "rb"))
    except subprocess.CalledProcessError as e:
        await update.message.reply_text(f"Conversion failed: {e}")
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, convert_video_to_ac3))

print("🤖 Bot is running...")
app.run_polling()
