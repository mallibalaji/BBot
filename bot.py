import os
import re
import gdown
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a Google Drive link to convert the video to AC3 audio.")

def extract_drive_id(url):
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if not match:
        match = re.search(r'id=([a-zA-Z0-9_-]+)', url)
    return match.group(1) if match else None

async def handle_drive_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    file_id = extract_drive_id(url)
    if not file_id:
        await update.message.reply_text("Invalid Google Drive link. Please make sure it contains a file ID.")
        return

    download_url = f"https://drive.google.com/uc?id={file_id}"
    input_path = "input_video.mp4"
    output_path = "output_video_ac3.mp4"

    try:
        gdown.download(download_url, input_path, quiet=False)

        # Extract original bitrate
        probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0",
                                "-show_entries", "stream=bit_rate",
                                "-of", "default=noprint_wrappers=1:nokey=1", input_path],
                                capture_output=True, text=True)
        bitrate = probe.stdout.strip() or "192000"

        # Convert video audio to AC3
        subprocess.run([
            "ffmpeg", "-i", input_path,
            "-c:v", "copy", "-c:a", "ac3", "-b:a", f"{bitrate}", output_path
        ], check=True)

        await update.message.reply_document(document=open(output_path, "rb"))

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

    finally:
        for f in [input_path, output_path]:
            if os.path.exists(f):
                os.remove(f)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_drive_link))

if __name__ == "__main__":
    app.run_polling()
