import asyncio
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import os

GRAPH_DIR = "graphs"


async def analyze_and_plot(client, recipient_username):
    conn = sqlite3.connect('messages.db')
    cursor = conn.cursor()

    now = datetime.now()
    past_24_hours = now - timedelta(hours=24)

    cursor.execute('''
        SELECT word, turn_marker, cur_datetime
        FROM special_words
        WHERE cur_datetime >= ?
    ''', (past_24_hours,))

    rows = cursor.fetchall()

    if rows:
        tag_turn_data = {}
        for row in rows:
            tag, turn_marker = row[0], row[1]
            if tag not in tag_turn_data:
                tag_turn_data[tag] = {}
            if turn_marker not in tag_turn_data[tag]:
                tag_turn_data[tag][turn_marker] = 0
            tag_turn_data[tag][turn_marker] += 1

        if not os.path.exists(GRAPH_DIR):
            os.makedirs(GRAPH_DIR)

        for tag, turn_counts in tag_turn_data.items():
            turns = list(turn_counts.keys())
            counts = list(turn_counts.values())

            plt.figure(figsize=(8, 6))
            plt.bar(turns, counts, color='skyblue')
            plt.title(f"Упоминания слова '{tag}' по Turn Markers за последние 24 часа")
            plt.xlabel('Turn Markers')
            plt.ylabel('Количество упоминаний')

            filename = f'{GRAPH_DIR}/{tag.replace("#", "")}_turn_marker_plot_{now.strftime("%Y-%m-%d")}.png'
            plt.savefig(filename)
            plt.close()

            print(f'График для слова "{tag}" сохранен как {filename}')
    else:
        print("Нет данных за последние 24 часа.")

    conn.close()


def clean_old_graphs():
    now = datetime.now()
    cutoff_time = now - timedelta(days=3)

    for filename in os.listdir(GRAPH_DIR):
        file_path = os.path.join(GRAPH_DIR, filename)
        if os.path.isfile(file_path):
            try:
                file_date_str = filename.split('_')[-1].replace('.png', '')
                file_date = datetime.strptime(file_date_str, "%Y-%m-%d")
                if file_date < cutoff_time:
                    os.remove(file_path)
                    print(f'Удален старый график: {filename}')
            except ValueError:
                continue


# Функция для периодического выполнения задачи каждые 24 часа
async def periodic_task(client, recipient_username):
    while True:
        await analyze_and_plot(client, recipient_username)  # Анализируем и строим графики
        clean_old_graphs()  # Удаляем старые графики
        await asyncio.sleep(86400)  # Ожидаем 24 часа (86400 секунд)

