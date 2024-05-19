import paramiko
from telegram import Update
from telegram.ext import CallbackContext
import logging
import re
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

host = os.getenv('RM_HOST')
port = os.getenv('RM_PORT')
username = os.getenv('RM_USER')
password = os.getenv('RM_PASSWORD')

db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_username = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_database = os.getenv('DB_DATABASE')

# Функция для выполнения команды на удаленном сервере
def execute_ssh_command(host, port, username, password, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, port=port, username=username, password=password)
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    client.close()
    return output

# Функции для получения различной информации

    # 3.1.1
def get_release(update: Update, context: CallbackContext):
    logger.info(f"/get_release command executed by")
    response = execute_ssh_command(host, port, username, password, "cat /etc/*-release")
    update.message.reply_text(response)

    # 3.1.2
def get_uname(update: Update, context: CallbackContext):
    response = execute_ssh_command(host, port, username, password, "uname -a")
    update.message.reply_text(response)

    # 3.1.3
def get_uptime(update: Update, context: CallbackContext):
    response = execute_ssh_command(host, port, username, password, "uptime")
    update.message.reply_text(response)

    # 3.2
def get_df(update: Update, context: CallbackContext):
    response = execute_ssh_command(host, port, username, password, "df -h")
    update.message.reply_text(response)

    # 3.3
def get_free(update: Update, context: CallbackContext):
    response = execute_ssh_command(host, port, username, password, "free -m")
    update.message.reply_text(response)

    # 3.4
def get_mpstat(update: Update, context: CallbackContext):
    response = execute_ssh_command(host, port, username, password, "mpstat")
    update.message.reply_text(response)

    # 3.5
def get_w(update: Update, context: CallbackContext):
    response = execute_ssh_command(host, port, username, password, "w")
    update.message.reply_text(response)

    # 3.6.1
def get_auths(update: Update, context: CallbackContext):
    response = execute_ssh_command(host, port, username, password, "last -n 10")
    update.message.reply_text(response)

    # 3.6.2
def get_critical(update: Update, context: CallbackContext):
    response = execute_ssh_command(host, port, username, password, "tail -n 5 /var/log/syslog")
    if response:
        update.message.reply_text(response)
    else:
        update.message.reply_text("Ничего не выявлено")

    # 3.7
def get_ps(update: Update, context: CallbackContext):
    response = execute_ssh_command(host, port, username, password, "ps")
    update.message.reply_text(response)

    # 3.8
def get_ss(update: Update, context: CallbackContext):
    response = execute_ssh_command(host, port, username, password, "ss -tuln")
    update.message.reply_text(response)

    # 3.9
def get_apt_list(update: Update, context: CallbackContext):
    args = context.args
    if len(args) == 0:
        # Если нет аргументов, выводим 20 пакетов
        response = execute_ssh_command(host, port, username, password, "apt list | tail -n 20")
    else:
        # Если есть аргументы, ищем информацию о пакете
        package_name = args[0]
        response = execute_ssh_command(host, port, username, password, f"apt list | grep {package_name}")
    update.message.reply_text(response)

    # 3.10
def get_services(update: Update, context: CallbackContext):
    response = execute_ssh_command(host, port, username, password, "service --status-all")
    update.message.reply_text(response)