import sqlite3
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

TOKEN = "8753247084:AAGuH86dlvnYRNRCI-uHqethhXGVJu3mpO0"

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

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Gunakan:\n/tambah nama id sn\n/cek id"
    )

def tambah(update: Update, context: CallbackContext):
    nama = context.args[0]
    id_pelanggan = context.args[1]
    sn = context.args[2]

    cursor.execute("INSERT INTO pelanggan (nama, id_pelanggan, sn_modem) VALUES (?, ?, ?)",
                   (nama, id_pelanggan, sn))
    conn.commit()

    update.message.reply_text("Data tersimpan ✅")

def cek(update: Update, context: CallbackContext):
    id_pelanggan = context.args[0]

    cursor.execute("SELECT * FROM pelanggan WHERE id_pelanggan=?", (id_pelanggan,))
    data = cursor.fetchone()

    if data:
        update.message.reply_text(f"Nama: {data[1]}\nSN: {data[3]}")
    else:
        update.message.reply_text("Tidak ditemukan")

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("tambah", tambah))
    dp.add_handler(CommandHandler("cek", cek))

    updater.start_polling()
    updater.idle()

main()