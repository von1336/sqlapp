import random
import os
import time
import threading
from telebot import types, TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup
from dotenv import load_dotenv
from database import DatabaseManager

load_dotenv()

user_data = {}
user_activity = {}
user_question_count = {}

print('Starting Telegram bot...')

state_storage = StateMemoryStorage()
token_bot = os.getenv('BOT_TOKEN', '')
bot = TeleBot(token_bot, state_storage=state_storage)

db = DatabaseManager()

class Command:
    ADD_WORD = 'добавить слово ➕'
    DELETE_WORD = 'удалить слово 🔙'
    NEXT = 'Следующее слово'
    STATS = 'Статистика'

class MyStates(StatesGroup):
    waiting_for_english = State()
    waiting_for_russian = State()
    waiting_for_delete_confirmation = State()

def show_hint(*lines):
    return '\n'.join(lines)

def show_target(data):
    return f"{data['target_word']} -> {data['translate_word']}"

def cleanup_inactive_users():
    import time
    current_time = time.time()
    inactive_threshold = 300
    
    users_to_remove = []
    for user_id, last_activity in user_activity.items():
        if current_time - last_activity > inactive_threshold:
            users_to_remove.append(user_id)
    
    for user_id in users_to_remove:
        if user_id in user_data:
            del user_data[user_id]
        if user_id in user_activity:
            del user_activity[user_id]
        print(f"Cleaned up inactive user: {user_id}")
    
    if users_to_remove:
        print(f"Cleaned up {len(users_to_remove)} inactive users")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    cid = message.chat.id
    user = message.from_user
    
    db.add_user(user.id, user.username, user.first_name, user.last_name)
    
    greeting = f"""Привет 👋
Давай попрактикуемся в английском языке. Тренировки можешь проходить в удобном для себя темпе. 

У тебя есть возможность использовать тренажёр, как конструктор, и собирать свою собственную базу для обучения. Для этого воспрользуйся инструментами:
- добавить слово ➕,
- удалить слово 🔙.

Ну что, начнём ⬇️"""
    
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    stats_btn = types.KeyboardButton(Command.STATS)
    
    markup.add(next_btn, add_word_btn, delete_word_btn, stats_btn)
    
    bot.send_message(cid, greeting, reply_markup=markup)

def create_cards(message):
    cid = message.chat.id
    
    try:
        word_data = db.get_random_word(cid)
        if not word_data:
            print(f"Warning: No word data returned for user {cid}")
            bot.send_message(cid, "К сожалению, не удалось получить слово для изучения. Попробуйте отправить /start")
            return
        
        if not word_data.get('english_word') or not word_data.get('translation_word'):
            print(f"Warning: Invalid word data for user {cid}: {word_data}")
            bot.send_message(cid, "Получены некорректные данные слова. Попробуйте отправить /start")
            return
            
    except Exception as e:
        print(f"Error getting random word: {e}")
        bot.send_message(cid, "Произошла ошибка при получении слова. Попробуйте отправить /start")
        return
    
    other_words_data = db.get_random_words_for_quiz(cid, word_data['english_word'], 3)
    
    if len(other_words_data) < 3:
        print(f"Warning: Only {len(other_words_data)} other words available for user {cid}")
    
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    all_options = [word_data['english_word']] + other_words_data
    if len(all_options) < 4:
        print(f"Warning: Not enough options for quiz. User {cid} has only {len(all_options)} options")
        bot.send_message(cid, "Недостаточно слов для создания викторины. Попробуйте добавить больше слов.")
        return
    
    random.shuffle(all_options)
    
    option_buttons = [types.KeyboardButton(word) for word in all_options]
    markup.add(*option_buttons)
    
    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    stats_btn = types.KeyboardButton(Command.STATS)
    markup.add(next_btn, add_word_btn, delete_word_btn, stats_btn)
    
    greeting = f"Выбери перевод слова: 🇷🇺 {word_data['translation_word']}"
    bot.send_message(cid, greeting, reply_markup=markup)
    
    user_id = message.from_user.id
    
    if user_id not in user_question_count:
        user_question_count[user_id] = 0
    user_question_count[user_id] += 1
    
    user_data[user_id] = {
        'target_word': word_data['english_word'],
        'translate_word': word_data['translation_word'],
        'word_type': word_data['word_type'],
        'word_id': word_data['word_id'],
        'other_words': other_words_data
    }
    
    print(f"Saved word data for user {user_id}: {user_data[user_id]}")
    print(f"Target word set to: {word_data['english_word']}")
    print(f"Question count for user {user_id}: {user_question_count[user_id]}")

@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    create_cards(message)

@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word_start(message):
    cid = message.chat.id
    bot.set_state(message.from_user.id, MyStates.waiting_for_english, cid)
    bot.send_message(cid, "Введите английское слово:")

@bot.message_handler(state=MyStates.waiting_for_english)
def add_word_english(message):
    cid = message.chat.id
    english_word = message.text.strip()
    
    if not english_word or len(english_word) < 2:
        bot.send_message(cid, "Пожалуйста, введите корректное английское слово (минимум 2 символа).")
        return
    
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]['new_english_word'] = english_word
    
    bot.set_state(message.from_user.id, MyStates.waiting_for_russian, cid)
    bot.send_message(cid, f"Теперь введите перевод для слова '{english_word}':")

@bot.message_handler(state=MyStates.waiting_for_russian)
def add_word_russian(message):
    cid = message.chat.id
    russian_word = message.text.strip()
    
    if not russian_word or len(russian_word) < 2:
        bot.send_message(cid, "Пожалуйста, введите корректный перевод (минимум 2 символа).")
        return
    
    user_id = message.from_user.id
    english_word = user_data.get(user_id, {}).get('new_english_word', '')
    
    if db.add_user_word(cid, english_word, russian_word):
        words_count = db.get_user_words_count(cid)
        bot.send_message(cid, f"Слово '{english_word}' успешно добавлено!\n\nТеперь у тебя {words_count} персональных слов для изучения.")
    else:
        bot.send_message(cid, "Произошла ошибка при добавлении слова. Попробуйте позже.")
    
    bot.delete_state(message.from_user.id, cid)
    
    create_cards(message)

@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word_start(message):
    cid = message.chat.id
    
    words_count = db.get_user_words_count(cid)
    
    if words_count == 0:
        bot.send_message(cid, "У тебя пока нет персональных слов для удаления.")
        return
    
    user_words = db.get_user_words(cid)
    
    if not user_words:
        bot.send_message(cid, "Не удалось получить список слов для удаления.")
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for english_word, translation_word in user_words:
        delete_btn = types.InlineKeyboardButton(
            f"🗑️ {english_word} -> {translation_word}", 
            callback_data=f"delete_{english_word}"
        )
        markup.add(delete_btn)
    
    bot.send_message(cid, f"Выбери слово для удаления (у тебя {words_count} персональных слов):", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
def delete_word_confirmation(call):
    cid = call.message.chat.id
    english_word = call.data.replace('delete_', '')
    
    if db.delete_user_word(cid, english_word):
        remaining_count = db.get_user_words_count(cid)
        bot.edit_message_text(
            f"✅ Слово '{english_word}' успешно удалено!\n\nОсталось персональных слов: {remaining_count}",
            cid, 
            call.message.message_id
        )
        
        if remaining_count > 0:
            markup = types.InlineKeyboardMarkup()
            continue_btn = types.InlineKeyboardButton("Продолжить изучение", callback_data="continue_learning")
            markup.add(continue_btn)
            bot.send_message(cid, "Что делаем дальше?", reply_markup=markup)
        else:
            create_cards(call.message)
    else:
        bot.edit_message_text(
            f"❌ Ошибка при удалении слова '{english_word}'.",
            cid, 
            call.message.message_id
        )

@bot.callback_query_handler(func=lambda call: call.data == "continue_learning")
def continue_learning_handler(call):
    cid = call.message.chat.id
    bot.edit_message_text("Продолжаем изучение!", cid, call.message.message_id)
    create_cards(call.message)

@bot.message_handler(func=lambda message: message.text == Command.STATS)
def show_stats(message):
    cid = message.chat.id
    
    personal_words = db.get_user_words_count(cid)
    db_stats = db.get_database_stats()
    
    if db_stats:
        stats_text = f"""Твоя статистика:

Персональных слов: {personal_words}
Общих слов: {db_stats['common_words']}
Всего пользователей: {db_stats['users']}
Всего персональных слов: {db_stats['user_words']}

Совет: Добавляй новые слова для расширения словарного запаса!"""
    else:
        stats_text = f"""Твоя статистика:

Персональных слов: {personal_words}
Общих слов: 15 (базовый набор)

Совет: Добавляй новые слова для расширения словарного запаса!"""
    
    bot.send_message(cid, stats_text)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    text = message.text
    cid = message.chat.id
    user_id = message.from_user.id
    
    user_activity[user_id] = time.time()
    
    if text in [Command.NEXT, Command.ADD_WORD, Command.DELETE_WORD, Command.STATS]:
        return
    
    data = user_data.get(user_id, {})
    print(f"User {user_id} data: {data}")
    print(f"Text received: '{text}'")
    
    if 'target_word' not in data:
        print(f"No target_word found for user {user_id}, creating new cards")
        try:
            bot.send_message(cid, "Создаю новое слово для изучения...")
            create_cards(message)
        except Exception as e:
            print(f"Error creating cards: {e}")
            bot.send_message(cid, "Произошла ошибка. Попробуйте отправить /start")
        return
    
    if not text or len(text.strip()) < 1:
        bot.send_message(cid, "❌ Пожалуйста, введите корректный ответ!")
        return
    
    target_word = data['target_word']
    translate_word = data['translate_word']
    word_type = data.get('word_type', 'common')
    word_id = data.get('word_id')
    
    print(f"Checking answer: '{text}' against target: '{target_word}'")
    
    valid_options = [target_word] + data.get('other_words', [])
    if text not in valid_options:
        bot.send_message(cid, f"❌ Пожалуйста, выберите один из предложенных вариантов ответа!")
        return
    
    if text == target_word:
        bot.send_message(cid, f"Отлично! ❤️ {target_word} -> {translate_word}")
        
        if word_id and word_type:
            db.update_learning_stats(cid, word_id, word_type, True)
        
        user_data[user_id] = {}
        
        time.sleep(1)
        create_cards(message)
    
    else:
        bot.send_message(cid, f"❌ Неправильно! Твой ответ: '{text}'\n\nПравильный ответ: '{target_word}' -> '{translate_word}'\n\nПопробуй еще раз! 💪")
        
        if word_id and word_type:
            db.update_learning_stats(cid, word_id, word_type, False)
        
        print(f"Wrong answer for user {user_id} - keeping word data: {data}")
        
        bot.send_message(cid, f"Выбери перевод слова: 🇷🇺 {translate_word}")
        
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        all_options = [target_word] + data.get('other_words', [])
        random.shuffle(all_options)
        option_buttons = [types.KeyboardButton(word) for word in all_options]
        markup.add(*option_buttons)
        
        next_btn = types.KeyboardButton(Command.NEXT)
        add_word_btn = types.KeyboardButton(Command.ADD_WORD)
        delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
        stats_btn = types.KeyboardButton(Command.STATS)
        markup.add(next_btn, add_word_btn, delete_word_btn, stats_btn)
        
        bot.send_message(cid, "Выбери правильный ответ:", reply_markup=markup)

bot.add_custom_filter(custom_filters.StateFilter(bot))

if __name__ == '__main__':
    try:
        print("Bot started. Press Ctrl+C to stop.")
        
        def periodic_cleanup():
            while True:
                try:
                    cleanup_inactive_users()
                    time.sleep(60)
                except Exception as e:
                    print(f"Cleanup error: {e}")
                    time.sleep(60)
        
        cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
        cleanup_thread.start()
        
        bot.infinity_polling(skip_pending=True)
    except KeyboardInterrupt:
        print("\nBot stopped.")
        db.close()
    except Exception as e:
        print(f"Error: {e}")
        db.close() 