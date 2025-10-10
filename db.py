# db.py
import aiosqlite
import logging
from config import DB_NAME

async def create_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS quiz_state (
                user_id INTEGER PRIMARY KEY,
                question_index INTEGER DEFAULT 0,
                correct_answers INTEGER DEFAULT 0
            )
        ''')
        await db.commit()

async def get_quiz_index(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def update_quiz_index(user_id, index):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE quiz_state SET question_index = ? WHERE user_id = ?', (index, user_id))
        await db.commit()

        # Проверяем результат запроса
        result = await db.execute('SELECT question_index FROM quiz_state WHERE user_id = ?', (user_id,))
        row = await result.fetchone()

        if row is not None:
            logging.info(f"Updated quiz index for user {user_id}: {row[0]}")
        else:
            logging.warning(f"No record found for user {user_id} after updating quiz index.")

async def get_stats(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT correct_answers FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else None

async def increment_correct_answers(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE quiz_state SET correct_answers = correct_answers + 1 WHERE user_id = ?', (user_id,))
        await db.commit()

async def reset_progress(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM quiz_state WHERE user_id = ?', (user_id,))
        await db.commit()

async def initialize_user(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR IGNORE INTO quiz_state (user_id) VALUES (?)', (user_id,))
        await db.commit()

async def reset_progress(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE quiz_state SET correct_answers = 0 WHERE user_id = ?', (user_id,))
        await db.commit()