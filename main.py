import os
import sqlite3 as sql
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
token = os.environ['TOKEN']


def save_user_data(user_id: int, username: str, time: str) -> None:
    with sql.connect("users.db") as db:
        cursor = db.cursor()

        cursor.execute("""CREATE TABLE IF NOT EXISTS users_data(
            id INTEGER,
            username TEXT,
            time TEXT
        )""")

        db.commit()

        cursor.execute(f"SELECT id FROM users_data WHERE id = {user_id}")
        user_data = cursor.fetchone()
        if user_data is None:
            cursor.execute("INSERT INTO users_data VALUES(?, ?, ?);", [user_id, username, time])
            db.commit()
        else:
            cursor.execute(
                f"UPDATE users_data SET time = ?, username = ? WHERE id = {user_id}",
                [time, username]
            )


def get_users_data() -> list:
    with sql.connect("users.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM users_data")
        users_data = cursor.fetchmany()

        return users_data


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    time = str(update.message.date)

    await update.message.reply_photo("./static/sad_cat.jpg", time)

    save_user_data(user_id, username, time)


async def users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    users_data = get_users_data()
    if len(users_data) != 0:
        await update.message.reply_text(users_data)
    else:
        await update.message.reply_text("Пользователи ещё не отправляли сообщения.")


def main() -> None:
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler(["start"], start))
    app.add_handler(CommandHandler(["users"], get_users_data))

    app.run_polling()


if __name__ == "__main__":
    main()