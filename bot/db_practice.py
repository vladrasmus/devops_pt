import paramiko
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
import psycopg2
import logging
import subprocess
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

from dotenv import load_dotenv
import os

logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

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

# def check_and_create_database(host, port, dbname, user, password):
#     try:
#         # Устанавливаем соединение с базой данных
#         conn = psycopg2.connect(
#             host=host,
#             port=port,
#             dbname='postgres',
#             user=user,
#             password=password
#         )
#         cursor = conn.cursor()
#
#         # Проверяем существование базы данных
#         cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{dbname}'")
#         exists = cursor.fetchone()
#
#         if not exists:
#             # Если базы данных не существует, создаем ее
#             cursor.execute(f"CREATE DATABASE {dbname}")
#
#         conn.commit()
#         conn.close()
#
#         return True  # База данных существует или была создана успешно
#
#     except Exception as e:
#         print("Ошибка при проверке/создании базы данных:", e)
#         return False

# conn = psycopg2.connect(
#             host=host,
#             port=db_port,
#             dbname="postgres",
#             user=username,
#             password=password
#         )
# cursor = conn.cursor()
# # cursor.execute("SELECT * FROM postgres;")
# result = cursor.fetchall()
# conn.close()
# print(result)

def execute_ssh_command(host, port, username, password, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, port=port, username=username, password=password)
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    client.close()
    return output

def execute_sql_command(host, port, dbname, user, password, sql_command):
    # if not check_and_create_database(host, port, dbname, user, password):
    #     return None
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_database,
            user=db_username,
            password=db_password
        )
        cursor = conn.cursor()
        cursor.execute(sql_command)
        result = cursor.fetchall()
        conn.close()

        return result
    except Exception as e:
        return "Ошибка при выполнении SQL команды"

def get_replica(update: Update, context: CallbackContext):
    # result = execute_ssh_command("192.168.0.37", "22", "devops", "1", "echo 1 | sudo -S cat /var/log/postgresql/postgresql.log | grep repl | tail -n 15")
    result = execute_ssh_command("192.168.0.37", "22", "devops", "1", "whoami")

    # if result.returncode != 0 or result.stderr.decode() != "":
        #     result = subprocess.run("cat /var/log/postgresql/postgresql-14-main.log | grep repl | tail -n 15", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode != 0 or result.stderr.decode() != "":
        update.message.reply_text("Can not open log file!")
    else:
        update.message.reply_text(result.stdout.decode().strip('\n'))

# def get_replica(update: Update, context: CallbackContext):
#     result = subprocess.run("cat /var/log/postgresql/postgresql.log | grep repl | tail -n 15", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#
#     # if result.returncode != 0 or result.stderr.decode() != "":
#     #     result = subprocess.run("cat /var/log/postgresql/postgresql-14-main.log | grep repl | tail -n 15", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#
#     if result.returncode != 0 or result.stderr.decode() != "":
#         update.message.reply_text("Can not open log file!")
#     else:
#         update.message.reply_text(result.stdout.decode().strip('\n'))
#
#     # response = execute_sql_command(db_host, db_port, db_database, db_username, db_password, "SELECT * FROM pg_catalog.pg_log ORDER BY log_time DESC LIMIT 35;")
#     # update.message.reply_text(response)

# def get_replica(update: Update, context: CallbackContext):
#     user = update.message.from_user
#     logger.info(f"/get_repl_logs was executed by {user.full_name}")
#
#     try:
#         # Использование Popen для построения пайплайнов
#         cat_process = subprocess.Popen(["cat", "/var/log/postgresql/postgresql.log"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         grep_process = subprocess.Popen(["grep", "repl"], stdin=cat_process.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         tail_process = subprocess.Popen(["tail", "-n", "15"], stdin=grep_process.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#
#         cat_process.stdout.close()
#         grep_process.stdout.close()
#
#         stdout, stderr = tail_process.communicate()
#
#         # if tail_process.returncode != 0 or stderr:
#         #     # Если ошибка, пробуем альтернативный лог-файл
#         #     cat_process = subprocess.Popen(["cat", "/var/log/postgresql/postgresql-14-main.log"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         #     grep_process = subprocess.Popen(["grep", "repl"], stdin=cat_process.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         #     tail_process = subprocess.Popen(["tail", "-n", "15"], stdin=grep_process.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         #
#         #     cat_process.stdout.close()
#         #     grep_process.stdout.close()
#         #
#         #     stdout, stderr = tail_process.communicate()
#
#         if tail_process.returncode != 0 or stderr:
#             update.message.reply_text("Can not open log file!")
#         else:
#             output = stdout.decode().strip()
#             if output:
#                 update.message.reply_text(output)
#             else:
#                 update.message.reply_text("No relevant log entries found.")
#     except Exception as e:
#         logger.error(f"Error while executing command: {e}")
#         update.message.reply_text("An error occurred while retrieving log file!")


# Получить адреса из БД
def get_emails(update: Update, context: CallbackContext):
    response = execute_sql_command(db_host, db_port, db_database, db_username, db_password, "SELECT * FROM emails;")
    update.message.reply_text(response)

# Получить номера из БД
def get_phones(update: Update, context: CallbackContext):
    response = execute_sql_command(db_host, db_port, db_database, db_username, db_password, "SELECT * FROM phones;")
    update.message.reply_text(response)

# Сохранение emails
def save_emails(update: Update, context: CallbackContext):
    user_response = update.message.text.lower()
    if user_response not in ['да', 'нет']:
        update.message.reply_text('Пожалуйста, ответьте "да" или "нет".')
        return 'saveEmails'

    if user_response == 'да':
        # Получаем список emails
        emails_to_save = context.user_data.get('emails_to_save', [])
    # if phone_numbers_to_save:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_database,
            user=db_username,
            password=db_password
        )
        # Создаем курсор для выполнения операций с базой данных
        cursor = conn.cursor()
        try:
            # Вставляем номера телефонов в таблицу
            for email in emails_to_save:
                cursor.execute("INSERT INTO emails (email) VALUES (%s)",(email,))
            # Фиксируем изменения в базе данных
            conn.commit()
            update.message.reply_text('Emails успешно сохранены в базу данных.')

        except psycopg2.Error as e:
            update.message.reply_text('Ошибка при работе с базой данных: {}'.format(str(e)))

        finally:
            # Закрываем курсор и соединение с базой данных
            cursor.close()
            conn.close()
    # else:
    #     update.message.reply_text('Нет данных для сохранения.')
    else:
        update.message.reply_text('Emails не сохранены.')

    return ConversationHandler.END

# Сохранение номеров телефона
def save_phone_numbers(update: Update, context: CallbackContext):
    user_response = update.message.text.lower()
    if user_response not in ['да', 'нет']:
        update.message.reply_text('Пожалуйста, ответьте "да" или "нет".')
        return 'savePhoneNumbers'

    if user_response == 'да':
        # Получаем список номеров телефонов из user_data
        phone_numbers_to_save = context.user_data.get('phone_numbers_to_save', [])
    # if phone_numbers_to_save:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_database,
            user=db_username,
            password=db_password
        )
        # Создаем курсор для выполнения операций с базой данных
        cursor = conn.cursor()
        try:
            # Вставляем номера телефонов в таблицу
            for phone_number in phone_numbers_to_save:
                cursor.execute("INSERT INTO phones (phone_number) VALUES (%s)",(phone_number,))
            # Фиксируем изменения в базе данных
            conn.commit()
            update.message.reply_text('Номера телефонов успешно сохранены в базу данных.')

        except psycopg2.Error as e:
            update.message.reply_text('Ошибка при работе с базой данных: {}'.format(str(e)))

        finally:
            # Закрываем курсор и соединение с базой данных
            cursor.close()
            conn.close()
    # else:
    #     update.message.reply_text('Нет данных для сохранения.')
    else:
        update.message.reply_text('Номера телефонов не сохранены.')

    return ConversationHandler.END