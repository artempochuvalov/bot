import os
import sqlite3 as sql
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
token = os.environ['TOKEN']


def save_user_data(user_id: int, username: str, time: str) -> None:
    """
        Saves user's id, username and time of message sent, to SQL db.
    """
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
        # if id already in the table -> only change time of message and username
        else:
            cursor.execute(
                f"UPDATE users_data SET time = ?, username = ? WHERE id = {user_id}",
                [time, username]
            )


def get_users_data() -> list:
    """
        Fetches all users' data from SQL db.

        Returns
        -------
        users_data: list
            Array of users' data
    """
    with sql.connect("users.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM users_data")
        users_data = cursor.fetchall()

        return users_data


def draw_image(user_id: int, text: str) -> str:
    """
        Draws temporary image of a cat with text on the center

        Returns
        -------
        img_path: str
            Path to the image
    """
    img = Image.open('./static/sad_cat.jpg')
    draw = ImageDraw.Draw(img)

    # width and height of the original image
    W, H = img.size
    font = ImageFont.truetype("./fonts/Roboto-Bold.ttf", 32)
    # with and height of the text
    _, _, w, h = draw.textbbox(xy=(0, 0), text=text, font=font)

    draw.text(((W-w)/2, (H-h)/2), text, fill="blue", font=font)

    img_path = f"./static/sad_cat_{user_id}.jpg"
    img.save(img_path)

    return img_path


def delete_image(img_path: str) -> None:
    """
        Deletes temporary image
    """
    try:
        os.remove(img_path)
    except FileNotFoundError:
        pass


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
        Starts bot application with /start command and
        sending photo of a cat and time of message sent.
    """
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    time = str(update.message.date)

    image_path = draw_image(user_id, time)

    await update.message.reply_photo(image_path)

    save_user_data(user_id, username, time)
    # cleans temporary image
    delete_image(image_path)


async def users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
        Forces bot to send users' data from DB with /users command
    """
    users_data = get_users_data()
    if len(users_data) != 0:
        await update.message.reply_text(users_data)
    else:
        await update.message.reply_text("Пользователи ещё не отправляли сообщения.")


def main() -> None:
    """
        Main function that initialize bot application and set commands.
    """
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler(["start"], start))
    app.add_handler(CommandHandler(["users"], users))

    app.run_polling()


if __name__ == "__main__":
    main()
