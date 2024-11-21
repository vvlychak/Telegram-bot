#pip install flask

from flask import Flask, render_template_string
import os
import chardet

app = Flask(__name__)

# Путь к файлу логов
LOG_FILE = "bot_logs.txt"


@app.route("/")
def show_logs():
    """
    Отображение логов в браузере.
    Логи читаются из файла bot_logs.txt.
    """
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "rb") as f:
            raw_data = f.read()
            encoding = chardet.detect(raw_data)["encoding"]
        with open(LOG_FILE, "r", encoding=encoding) as f:
            logs = f.readlines()
    else:
        logs = ["Файл логов не найден."]
    html_template = """
    <head>
        <meta http-equiv="refresh" content="5">
    </head>
    <h1>Логи Telegram-бота</h1>
    <ul>
        {% for log in logs %}
        <li>{{ log }}</li>
        {% endfor %}
    </ul>
    """
    return render_template_string(html_template, logs=logs)


if __name__ == "__main__":
    # Запуск веб-сервера Flask
    app.run(host="0.0.0.0", port=5000)