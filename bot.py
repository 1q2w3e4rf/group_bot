import telebot
import time
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

words = ["плохое слово"]

chat_history = {}
@bot.message_handler(commands=['kick'])
def kick_user(message):
    if message.reply_to_message:
        chat_id = message.chat.id
        user_id = message.reply_to_message.from_user.id
        user_status = bot.get_chat_member(chat_id, user_id).status
        if user_status == 'administrator' or user_status == 'creator':
            bot.reply_to(message, "Нельзя кикнуть администратора.")
        else:
            bot.kick_chat_member(chat_id, user_id)
            bot.reply_to(message, f"Пользователь {message.reply_to_message.from_user.username} был кикнут.")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя, которого вы хотите кикнуть.")

@bot.message_handler(commands=['rank'])
def set_rank(message):
    if message.reply_to_message:
        chat_id = message.chat.id
        user_id = message.reply_to_message.from_user.id
        rank = message.text.split()[1:]
        
        if bot.get_chat_member(chat_id, message.from_user.id).status in ['administrator', 'creator']:
            if rank:
                rank = ' '.join(rank)
                if chat_id not in chat_history:
                    chat_history[chat_id] = {}
                if user_id not in chat_history[chat_id]:
                    chat_history[chat_id][user_id] = {}
                chat_history[chat_id][user_id]['rank'] = rank
                bot.reply_to(message, f"Ранг пользователя {message.reply_to_message.from_user.username} установлен как {rank}")
            else:
                bot.reply_to(message, "Укажите ранг")
        else:
            bot.reply_to(message, "Только администраторы могут присваивать ранги")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя, которому вы хотите присвоить ранг")
@bot.message_handler(commands=['mute'])
def mute_user(message):
    if message.reply_to_message:
        chat_id = message.chat.id
        user_id = message.reply_to_message.from_user.id
        user_status = bot.get_chat_member(chat_id, user_id).status
        if user_status == 'administrator' or user_status == 'creator':
            bot.reply_to(message, "Невозможно замутить администратора.")
        else:
            muttime = 60
            args = message.text.split()[1:]
            if args:
                try:
                    muttime = int(args[0])
                except ValueError:
                    bot.reply_to(message, "Неправильный формат времени.")
                    return
                if muttime < 1:
                    bot.reply_to(message, "Время должно быть положительным числом.")
                    return
                if muttime > 1440:
                    bot.reply_to(message, "Максимальное время - 1 день.")
                    return
            bot.restrict_chat_member(chat_id, user_id, until_date=time.time()+muttime*60)
            bot.reply_to(message, f"Пользователь {message.reply_to_message.from_user.username} замучен на {muttime} минут.")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя, которого вы хотите замутить.")

@bot.message_handler(commands=['unmute'])
def unmute_user(message):
    if message.reply_to_message:
        chat_id = message.chat.id
        user_id = message.reply_to_message.from_user.id
        bot.restrict_chat_member(chat_id, user_id, can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
        bot.reply_to(message, f"Пользователь {message.reply_to_message.from_user.username} размучен.")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя, которого вы хотите размутить.")

@bot.message_handler(commands=['stats'])
def stats(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if chat_id not in chat_history:
        chat_history[chat_id] = {}
    if user_id not in chat_history[chat_id]:
        chat_history[chat_id][user_id] = {'messages': 0, 'rank': 'Не установлен'}
    user_messages = chat_history[chat_id][user_id]['messages']
    rank = chat_history[chat_id][user_id]['rank']
    bot.reply_to(message, f"Всего сообщений в группе: {sum(user['messages'] for user in chat_history[chat_id].values())}\nСообщений от @{message.from_user.username}: {user_messages}\nРанг: {rank}")

def check_message(message):
    for word in words:
        if word in message.text.lower():
            return True
    return False

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if chat_id not in chat_history:
        chat_history[chat_id] = {}
    if user_id not in chat_history[chat_id]:
        chat_history[chat_id][user_id] = {'messages': 0, 'rank': 'Не установлен'}
    chat_history[chat_id][user_id]['messages'] += 1
    
    if check_message(message):
        bot.kick_chat_member(message.chat.id, message.from_user.id)
        bot.send_message(message.chat.id, f"Пользователь {message.from_user.username} был удален из чата за использование запрещенных слов")

bot.infinity_polling()