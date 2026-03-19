import os
import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = os.environ.get("TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")

conn = sqlite3.connect("pelanggan.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS pelanggan (
    id SERIAL PRIMARY KEY,
    nama TEXT,
    id_pelanggan TEXT,
    sn_modem TEXT
)
""")
conn.commit()

user_state = {}

menu = [["➕ Tambah Data", "🔍 Cek Pelanggan"], ["📋 List Data"]]

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 Selamat datang di BOT Monitoring Pelanggan",
        reply_markup=ReplyKeyboardMarkup(menu, resize_keyboard=True)
    )

def handle_menu(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text

    if text == "➕ Tambah Data":
        user_state[user_id] = "nama"
        update.message.reply_text("Masukkan Nama Pelanggan:")

    elif text == "🔍 Cek Pelanggan":
        user_state[user_id] = "cek"
        update.message.reply_text("Masukkan ID Pelanggan:")

    elif text == "📋 List Data":
        cursor.execute("SELECT nama, id_pelanggan FROM pelanggan")
        data = cursor.fetchall()

        hasil = "\n".join([f"{d[1]} - {d[0]}" for d in data])
        update.message.reply_text(hasil if hasil else "Data kosong")

def handle_text(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id not in user_state:
        return

    state = user_state[user_id]

    if state == "nama":
        context.user_data["nama"] = text
        user_state[user_id] = "id"
        update.message.reply_text("Masukkan ID Pelanggan:")

    elif state == "id":
        context.user_data["id"] = text
        user_state[user_id] = "sn"
        update.message.reply_text("Masukkan SN Modem:")

    elif state == "sn":
        data = context.user_data

        cursor.execute(
            "INSERT INTO pelanggan (nama, id_pelanggan, sn_modem) VALUES (%s, %s, %s)",
            (data["nama"], data["id"], text)
        )
        conn.commit()

        update.message.reply_text("✅ Data berhasil disimpan")
        user_state.pop(user_id)

    elif state == "cek":
        cursor.execute("SELECT * FROM pelanggan WHERE id_pelanggan=%s", (text,))
        data = cursor.fetchone()

        if data:
            update.message.reply_text(f"Nama: {data[1]}\nSN: {data[3]}")
        else:
            update.message.reply_text("❌ Data tidak ditemukan")

        user_state.pop(user_id)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_menu))
    dp.add_handler(MessageHandler(Filters.text, handle_text))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
