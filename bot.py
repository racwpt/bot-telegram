import sqlite3
import os
import pandas as pd
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = os.environ.get("TOKEN")

# ================= DATABASE =================
conn = sqlite3.connect("pelanggan.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS pelanggan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT,
    id_pelanggan TEXT,
    sn_modem TEXT,
    odc TEXT,
    odp TEXT,
    latitude TEXT,
    longitude TEXT
)
""")
conn.commit()

# ================= STATE =================
user_state = {}

# ================= MENU =================
menu = [
    ["➕ Tambah Data"],
    ["🔍 Cek Pelanggan"],
    ["📋 Data Pelanggan"],
    ["📥 Export Excel"]
]

# ================= START =================
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "📡 BOT MONITORING PELANGGAN\n\nSilakan pilih menu:",
        reply_markup=ReplyKeyboardMarkup(menu, resize_keyboard=True)
    )

# ================= HANDLE =================
def handle_all(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text

    # ===== MENU =====
    if text == "➕ Tambah Data":
        user_state[user_id] = "nama"
        update.message.reply_text("Masukkan Nama Pelanggan:")
        return

    elif text == "🔍 Cek Pelanggan":
        user_state[user_id] = "cek"
        update.message.reply_text("Masukkan ID Pelanggan:")
        return

    elif text == "📋 Data Pelanggan":
        cursor.execute("SELECT nama, id_pelanggan, sn_modem, odc, odp FROM pelanggan")
        data = cursor.fetchall()

        if not data:
            update.message.reply_text("❌ Data kosong")
            return

        hasil = "📋 DATA PELANGGAN:\n\n"
        for d in data:
            hasil += (
                f"👤 {d[0]}\n"
                f"🆔 {d[1]}\n"
                f"📡 {d[2]}\n"
                f"📍 ODC: {d[3]}\n"
                f"📍 ODP: {d[4]}\n\n"
            )

        update.message.reply_text(hasil)
        return

    elif text == "📥 Export Excel":
        df = pd.read_sql_query("SELECT * FROM pelanggan", conn)

        file_name = "data_pelanggan.xlsx"
        df.to_excel(file_name, index=False)

        update.message.reply_document(open(file_name, "rb"))
        return

    # ===== HANDLE LOKASI =====
    if update.message.location:
        if user_id in user_state and user_state[user_id] == "lokasi":
            lat = update.message.location.latitude
            lon = update.message.location.longitude

            data = context.user_data

            cursor.execute(
                "INSERT INTO pelanggan (nama, id_pelanggan, sn_modem, odc, odp, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (data["nama"], data["id"], data["sn"], data["odc"], data["odp"], lat, lon)
            )
            conn.commit()

            update.message.reply_text(
                "✅ Data + lokasi berhasil disimpan",
                reply_markup=ReplyKeyboardMarkup(menu, resize_keyboard=True)
            )

            user_state.pop(user_id)
            context.user_data.clear()
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
        context.user_data["sn"] = text
        user_state[user_id] = "odc"
        update.message.reply_text("Masukkan ODC:")

    elif state == "odc":
        context.user_data["odc"] = text
        user_state[user_id] = "odp"
        update.message.reply_text("Masukkan ID ODP:")

    elif state == "odp":
        context.user_data["odp"] = text
        user_state[user_id] = "lokasi"

        lokasi_button = [[KeyboardButton("📍 Share Lokasi", request_location=True)]]

        update.message.reply_text(
            "📍 Silakan kirim lokasi pemasangan:",
            reply_markup=ReplyKeyboardMarkup(lokasi_button, resize_keyboard=True)
        )

    elif state == "cek":
        cursor.execute(
            "SELECT nama, id_pelanggan, sn_modem, odc, odp, latitude, longitude FROM pelanggan WHERE id_pelanggan=?",
            (text,)
        )
        data = cursor.fetchone()

        if data:
            maps = f"https://maps.google.com/?q={data[5]},{data[6]}"

            update.message.reply_text(
                f"👤 Nama: {data[0]}\n"
                f"🆔 ID: {data[1]}\n"
                f"📡 SN: {data[2]}\n"
                f"📍 ODC: {data[3]}\n"
                f"📍 ODP: {data[4]}\n"
                f"🗺️ Lokasi: {maps}",
                reply_markup=ReplyKeyboardMarkup(menu, resize_keyboard=True)
            )
        else:
            update.message.reply_text("❌ Data tidak ditemukan")

        user_state.pop(user_id)

# ================= MAIN =================
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text | Filters.location, handle_all))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
