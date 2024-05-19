import logging
import re
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

from dotenv import load_dotenv
import os

import monitoring
import db_practice

# Загружаем .env и токены
load_dotenv()

BOT_TOKEN = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

host = os.getenv('RM_HOST')
port = os.getenv('RM_PORT')
username = os.getenv('RM_USER')
password = os.getenv('RM_PASSWORD')

db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_username = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_database = os.getenv('DB_DATABASE')

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')
    update.message.reply_text(f'Команды: /help')

def helpСommand(update: Update, context: CallbackContext):
    help_text = """
    (Написать текст = получить эхо)
        Список доступных команд:
    /start - Начать использование бота
        Мониторинг:
    /get_release - Получить информацию о релизе
    /get_uname - Получить информацию об архитектуре процессора, имени хоста и версии ядра
    /get_uptime - Получить информацию о времени работы системы
    /get_df - Получить информацию о состоянии файловой системы
    /get_free - Получить информацию о состоянии оперативной памяти
    /get_mpstat - Получить информацию о производительности системы
    /get_w - Получить информацию о работающих пользователях
    /get_auths - Получить последние 10 входов в систему
    /get_critical - Получить последние 5 критических событий
    /get_ps - Получить информацию о запущенных процессах
    /get_ss - Получить информацию об используемых портах
    /get_apt_list - Получить информацию об установленных пакетах
    /get_services - Получить информацию о запущенных сервисах
    /get_repl_logs - логи
        Password:
    /verify_password - Проверить пароль
        Вывод из БД:
    /get_emails - Вывести email из БД
    /get_phone_numbers - Вывести номера из БД
        Поиск номеров и запись в БД:
    /find_email - Найти email и записать в БД
    /find_phone_number - Найти номер телефона и записать в БД
    """
    update.message.reply_text(help_text)

def echo(update: Update, context):
    update.message.reply_text(update.message.text)

def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'findPhoneNumbers'

def findEmailsCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска email')

    return 'findEmails'

def verifyPassCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки сложности')

    return 'verifyPass'

# Здесь сами функции поиска
# Нахождение номеров телефона
def findPhoneNumbers(update: Update, context):
    user_input = update.message.text  # Получаем текст, содержащий(или нет) номера телефонов

    phoneNumRegex = re.compile(r'((?:\+7|8)[\s\(\-]?\d{3}[\)\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?[0-9]{2})')

    phoneNumberList = phoneNumRegex.findall(user_input)  # Ищем номера телефонов

    if not phoneNumberList:  # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return  # Завершаем выполнение функции

    phoneNumberList_filtered = []
  # Создаем массив номерами телефонов
    for i, phoneNumber in enumerate(phoneNumberList, 1):
        phoneNumberList_filtered.append(f'{i}. {phoneNumber}')

    phoneNumbersText = '\n'.join(phoneNumberList_filtered)

    # Сохраняем список номеров телефонов
    context.user_data['phone_numbers_to_save'] = phoneNumberList

    update.message.reply_text(phoneNumbersText)  # Отправляем сообщение с номерами телефонов
    update.message.reply_text("Сохранить номера в базу данных?")

    return 'savePhoneNumbers' # Переходим в следующий стейт

# Нахождение emails
def findEmails(update: Update, context):
    user_input = update.message.text  # Получаем текст, содержащий(или нет) emails

    emailRegex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

    emailsList = emailRegex.findall(user_input)  # Ищем emails

    if not emailsList:  # Обрабатываем случай, когда emails нет
        update.message.reply_text('Emails не найдены')
        return  # Завершаем выполнение функции

    emailsList_filtered = []
  # Создаем массив номерами телефонов
    for i, phoneNumber in enumerate(emailsList, 1):
        emailsList_filtered.append(f'{i}. {phoneNumber}')

    response_text = '\n'.join(emailsList_filtered)

    # Сохраняем список emails
    context.user_data['emails_to_save'] = emailsList

    update.message.reply_text(response_text)  # Отправляем сообщение с emails
    update.message.reply_text("Сохранить номера в базу данных?")

    return 'saveEmails' # Переходим в следующий стейт

def verifyPass(update: Update, context):
    user_input = update.message.text

    passRegex = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()]).{8,}$')

    passList = passRegex.findall(user_input)  # если найдем, то пароль сложный

    if passList:  # Обрабатываем случай, когда пароль сложный
        update.message.reply_text('Пароль достаточно сложный')
        return ConversationHandler.END  # Завершаем работу обработчика диалога
    else:
        update.message.reply_text('Пароль слишком легкий')
        return ConversationHandler.END  # Завершаем работу обработчика диалога

    # Отмена операции
def cancel(update: Update, context: CallbackContext):
    update.message.reply_text('Операция отменена.')
    return ConversationHandler.END

def main():
    # Создайте программу обновлений и передайте ей токен вашего бота
    updater = Updater(BOT_TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'savePhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, db_practice.save_phone_numbers)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailsCommand)],
        states={
            'findEmails': [MessageHandler(Filters.text & ~Filters.command, findEmails)],
            'saveEmails': [MessageHandler(Filters.text & ~Filters.command, db_practice.save_emails)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    convHandlerVerifyPass = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPassCommand)],
        states={
            'verifyPass': [MessageHandler(Filters.text & ~Filters.command, verifyPass)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpСommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)

    # Проверка пароля
    dp.add_handler(convHandlerVerifyPass)

    # МОНИТОРИНГ
    dp.add_handler(CommandHandler("get_release", monitoring.get_release))
    dp.add_handler(CommandHandler("get_uname", monitoring.get_uname))
    dp.add_handler(CommandHandler("get_uptime", monitoring.get_uptime))
    dp.add_handler(CommandHandler("get_df", monitoring.get_df))
    dp.add_handler(CommandHandler("get_free", monitoring.get_free))
    dp.add_handler(CommandHandler("get_mpstat", monitoring.get_mpstat))
    dp.add_handler(CommandHandler("get_w", monitoring.get_w))
    dp.add_handler(CommandHandler("get_auths", monitoring.get_auths))
    # вот тут вопрос
    dp.add_handler(CommandHandler("get_critical", monitoring.get_critical))
    dp.add_handler(CommandHandler("get_ps", monitoring.get_ps))
    dp.add_handler(CommandHandler("get_ss", monitoring.get_ss))
    dp.add_handler(CommandHandler("get_apt_list", monitoring.get_apt_list))
    dp.add_handler(CommandHandler("get_services", monitoring.get_services))
    # Практика БД
    dp.add_handler(CommandHandler("get_repl_logs", db_practice.get_replica))
    dp.add_handler(CommandHandler("get_emails", db_practice.get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", db_practice.get_phones))

    # Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()

if __name__ == '__main__':
    main()
