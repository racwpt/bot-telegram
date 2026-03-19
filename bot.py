import sqlite3
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = os.environ.get("TOKEN")

# DATABASE SQLITE
conn = sqlite3.connect("pelanggan.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS pelanggan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT,
    id_pelanggan TEXT,
    sn_modem TEXT
)
""")
conn.commit()

# STATE USER
user_state = {}

# MENU BUTTON
menu = [
    ["➕ Tambah Data"],
    ["📋 Data Pelanggan"],
    ["🔍 Cek Pelanggan"]
]

# START
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "📡 BOT MONITORING PELANGGAN\n\nSilakan pilih menu:",
        reply_markup=ReplyKeyboardMarkup(menu, resize_keyboard=True)
    )

def handle_all(update: Update, context: CallbackContext):
    text = update.message.text
    user_id = update.message.from_user.id

    # ===== MENU =====
    if text == "➕ Tambah Data":
        user_state[user_id] = "nama"
        update.message.reply_text("Masukkan Nama Pelanggan:")
        return

    elif text == "📋 Data Pelanggan":
        cursor.execute("SELECT nama, id_pelanggan, sn_modem FROM pelanggan")
        data = cursor.fetchall()

        if not data:
            update.message.reply_text("❌ Data masih kosong")
            return

        hasil = "📋 DATA PELANGGAN:\n\n"
        for d in data:
            hasil += f"👤 {d[0]}\n🆔 {d[1]}\n📡 {d[2]}\n\n"

        update.message.reply_text(hasil)
        return

    elif text == "🔍 Cek Pelanggan":
        user_state[user_id] = "cek"
        update.message.reply_text("Masukkan ID Pelanggan:")
        return

    # ===== INPUT STEP =====
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
        update.message.reply_text("Masukkan Serial Number Modem:")
    
    elif state == "sn":
        data = context.user_data

        cursor.execute(
            "INSERT INTO pelanggan (nama, id_pelanggan, sn_modem) VALUES (?, ?, ?)",
            (data["nama"], data["id"], text)
        )
        conn.commit()

        update.message.reply_text("✅ Data berhasil disimpan")

        user_state.pop(user_id)
        context.user_data.clear()

    elif state == "cek":
        cursor.execute(
            "SELECT nama, id_pelanggan, sn_modem FROM pelanggan WHERE id_pelanggan=?",
            (text,)
        )
        data = cursor.fetchone()

        if data:
            update.message.reply_text(
                f"👤 Nama: {data[0]}\n🆔 ID: {data[1]}\n📡 SN: {data[2]}"
            )
        else:
            update.message.reply_text("❌ Data tidak ditemukan")

        user_state.pop(user_id)
# MAIN
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_all))


    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
