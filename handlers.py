# handlers.py
from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.filters import CommandStart
from aiogram.filters.command import Command
from questions import quiz_data
from db import *

router = Router()

def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()
    for option in answer_options:
        builder.add(
            types.InlineKeyboardButton(
                text=option,
                callback_data="right_answer" if option == right_answer else "wrong_answer"
            )
        )
    builder.adjust(1)
    return builder.as_markup()

@router.callback_query(F.data == "right_answer")
async def right_answer(callback: CallbackQuery):
    await callback.bot.edit_message_reply_markup(chat_id=callback.from_user.id, message_id=callback.message.message_id, reply_markup=None)
    await callback.message.answer("Верно!")

    # Увеличиваем счётчик правильных ответов
    await increment_correct_answers(callback.from_user.id)

    # Переходим к следующему вопросу
    current_question_index = await get_quiz_index(callback.from_user.id)
    next_question_index = current_question_index + 1
    await update_quiz_index(callback.from_user.id, next_question_index)

    # Проверяем наличие следующего вопроса
    if next_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Квиз завершён!")

@router.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: CallbackQuery):
    await callback.bot.edit_message_reply_markup(chat_id=callback.from_user.id, message_id=callback.message.message_id, reply_markup=None)

    # Получаем текущий индекс вопроса
    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']
    await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")

    # Переходим к следующему вопросу
    next_question_index = current_question_index + 1
    await update_quiz_index(callback.from_user.id, next_question_index)

    # Проверяем наличие следующего вопроса
    if next_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Квиз завершён!")

@router.message(Command("stats"))
async def stats_command(message: Message):
    user_id = message.from_user.id
    correct_answers = await get_stats(user_id)

    if correct_answers is None or correct_answers == 0:
        await message.answer("Вы еще не играли в квиз.")
    else:
        total_questions = len(quiz_data)
        await message.answer(f"Последняя игра: {correct_answers} из {total_questions}.")

@router.message(CommandStart())
async def start_command(message: Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз! Нажмите кнопку ниже, чтобы начать игру.", reply_markup=builder.as_markup(resize_keyboard=True))

async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    if current_question_index >= len(quiz_data):  # Проверяем выход за границы
        await message.answer("Все вопросы завершены!")
        return

    question = quiz_data[current_question_index]
    keyboard = generate_options_keyboard(question['options'], question['options'][question['correct_option']])
    await message.answer(question['question'], reply_markup=keyboard)

async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    await update_quiz_index(user_id, current_question_index)
    await get_question(message, user_id)

@router.message(lambda m: m.text == "Начать игру")
async def quiz_command(message: Message):
    await reset_progress(message.from_user.id)  # Сброс прогресса
    await message.answer("Начнём квиз!")
    await new_quiz(message)