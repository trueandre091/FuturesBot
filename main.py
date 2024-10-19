import asyncio
import sqlite3
import os
from telethon import TelegramClient, events

from fun.tag import scaler, pattern
from fun.turn import get_turn_markers
from fun.extra import get_chat_title
from fun.stats import periodic_task, GRAPH_DIR

with open("const.txt") as file:
    api_id = file.readline()
    api_hash = file.readline()
    phone_number = file.readline()
    recipient_username = file.readline()

conn = sqlite3.connect('messages.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS special_words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT NOT NULL,
        sender INTEGER NOT NULL,
        turn_marker TEXT NOT NULL,
        turn INTEGER NOT NULL,
        cur_datetime DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()


client = TelegramClient('session_name', api_id, api_hash, system_version="4.16.30-vxCUSTOM")


@client.on(events.NewMessage())
async def handler(event):
    message_text = event.message.message

    special_words = list(map(scaler, pattern.findall(message_text)))
    turn = get_turn_markers(message_text)

    title, chat_type_id, chat_type = await get_chat_title(client, event.message.chat_id)
    chat_link = f"https://t.me/{title}" if chat_type_id == 1 else title

    if special_words:
        if not turn:
            return

        print(f'Найдены специальные слова: {special_words}')

        for word in special_words:
            message = f'Найдено {word} от <a href="{chat_link}">{title}</a> {chat_type}\n\n<b>{turn}</b>'

            await client.send_message(recipient_username, parse_mode="HTML", message=message)
            print(f'Отправлено сообщение: {word} - {title} {chat_type} - {turn}')

            cursor.execute(
                'INSERT INTO special_words (word, sender, turn_marker, turn) VALUES (?, ?, ?, ?)',
                (word, int(event.message.chat_id), turn, (1 if turn[-1] == "↑" else 0))
            )
        conn.commit()


@client.on(events.NewMessage(pattern='/graphs'))
async def show_graphs(event):
    sender = await event.get_sender()
    sender_username = sender.username

    if sender_username != recipient_username[1:]:
        await event.respond("У вас нет прав для использования этой команды.")
        return

    for filename in os.listdir(GRAPH_DIR):
        file_path = os.path.join(GRAPH_DIR, filename)
        if os.path.isfile(file_path):
            await client.send_file(event.chat_id, file_path, caption=f"График {filename}")


async def main():
    await client.start(phone=phone_number)
    print("Бот запущен и готов к работе...")
    await periodic_task(client, recipient_username)
    await client.run_until_disconnected()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    finally:
        conn.close()

