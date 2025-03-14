from flask import Flask, request, render_template_string, jsonify
import re

app = Flask(__name__)

# Список для хранения последних трёх корректных email
saved_emails = []

# Регулярное выражение для проверки email
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

# HTML-шаблон страницы
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Введите Email</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #f4f4f4;
        }
        .container {
            text-align: center;
        }
        input[type="email"] {
            padding: 10px;
            font-size: 16px;
            width: 300px;
            margin-bottom: 10px;
            border: 1px solid #ccc;
            border-radius: 50px;
        }
        button {
            padding: 10px 20px;
            font-size: 16px;
            background-color: #007BFF;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        button:disabled {
            background-color: #cccccc;
            cursor: not-allowed;
        }
        .help-icon {
            position: absolute;
            top: 20px;
            right: 20px;
            font-size: 24px;
            cursor: pointer;
            color: #007BFF;
        }
        .error {
            color: red;
            margin-top: 10px;
            display: none; /* Скрываем ошибку по умолчанию */
        }
        .success-message {
            color: black; /* Чёрный цвет текста */
            margin-top: 10px;
            display: none; /* Скрываем успешное сообщение по умолчанию */
        }
        .success-green {
            color: green; /* Зелёный цвет текста */
            margin-top: 10px;
            display: none; /* Скрываем успешное сообщение по умолчанию */
        }
    </style>
</head>
<body>
    <div class="container">
        <input type="email" id="email" placeholder="Введите ваш email" required>
        <br>
        <button id="submitButton" onclick="submitEmail()" title="Нажмите отправить данные">ОК</button>
        <div id="error" class="error"></div>
        <div id="success-message" class="success-message"></div>
        <div id="success-green" class="success-green"></div>
    </div>
    <div class="help-icon" title="Это справочная информация" onclick="submitEmailFromIcon()">?</div>

    <script>
        let clickCount = 0; // Счётчик нажатий кнопки "ОК"
        const maxClicks = 5; // Максимальное количество нажатий

        // Обработчик нажатия клавиши Enter в поле ввода
        document.getElementById('email').addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                submitEmail();
            }
        });

        function submitEmail() {
            const email = document.getElementById('email').value;
            const errorElement = document.getElementById('error');
            const successMessageElement = document.getElementById('success-message');
            const successGreenElement = document.getElementById('success-green');

            // Увеличиваем счётчик нажатий при любом нажатии
            clickCount++;
            if (clickCount >= maxClicks) {
                // Блокируем кнопку после 5 нажатий
                document.getElementById('submitButton').disabled = true;
                errorElement.textContent = "Ошибка при отправке запроса.";
                errorElement.style.display = 'block'; // Показываем ошибку
                successMessageElement.style.display = 'none'; // Скрываем успешное сообщение
                successGreenElement.style.display = 'none'; // Скрываем зелёное сообщение
                return;
            }

            // Отправка данных методом PUT
            sendEmail(email, 'PUT');
        }

        function submitEmailFromIcon() {
            const email = document.getElementById('email').value;

            // Сбрасываем счётчик и разблокируем кнопку
            clickCount = 0;
            document.getElementById('submitButton').disabled = false;

            // Отправка данных методом GET
            sendEmail(email, 'GET');
        }

        function sendEmail(email, method) {
            const errorElement = document.getElementById('error');
            const successMessageElement = document.getElementById('success-message');
            const successGreenElement = document.getElementById('success-green');

            const url = method === 'GET' ? `/?email=${encodeURIComponent(email)}` : '/';
            fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: method === 'PUT' ? JSON.stringify({ email: email }) : null,
            })
            .then(response => {
                if (!response.ok) {
                    // Если статус ответа не 200, обрабатываем ошибку
                    return response.json().then(errorData => {
                        // Если статус 418, отображаем сообщение зелёным цветом
                        if (response.status === 418) {
                            throw { ...errorData, is418: true }; // Добавляем флаг is418
                        }
                        throw errorData; // Передаём данные об ошибке в блок catch
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Успешный ответ
                    successMessageElement.textContent = "Email принят: " + email;
                    successMessageElement.style.display = 'block'; // Показываем успешное сообщение
                    successGreenElement.style.display = 'none'; // Скрываем зелёное сообщение
                    errorElement.style.display = 'none'; // Скрываем ошибку
                } else if (data.message === "email уже запомнен") {
                    // Сообщение "email уже запомнен"
                    successGreenElement.textContent = data.message;
                    successGreenElement.style.display = 'block'; // Показываем зелёное сообщение
                    successMessageElement.style.display = 'none'; // Скрываем успешное сообщение
                    errorElement.style.display = 'none'; // Скрываем ошибку
                } else {
                    // Ошибка (например, некорректный email)
                    errorElement.textContent = data.message || "Ошибка при отправке email.";
                    errorElement.style.display = 'block'; // Показываем ошибку
                    successMessageElement.style.display = 'none'; // Скрываем успешное сообщение
                    successGreenElement.style.display = 'none'; // Скрываем зелёное сообщение
                }
            })
            .catch(errorData => {
                if (errorData.is418) {
                    // Обработка статуса 418 (зелёный цвет)
                    successGreenElement.textContent = errorData.message || "Ошибка 418.";
                    successGreenElement.style.display = 'block'; // Показываем зелёное сообщение
                    successMessageElement.style.display = 'none'; // Скрываем успешное сообщение
                    errorElement.style.display = 'none'; // Скрываем ошибку
                } else {
                    // Обработка других ошибок (красный цвет)
                    errorElement.textContent = errorData.message || "Ошибка при отправке запроса.";
                    errorElement.style.display = 'block'; // Показываем ошибку
                    successMessageElement.style.display = 'none'; // Скрываем успешное сообщение
                    successGreenElement.style.display = 'none'; // Скрываем зелёное сообщение
                }
            });
        }
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'PUT'])
def index():
    global saved_emails

    if request.method == 'PUT':
        data = request.get_json()
        email = data.get('email')

        # Проверка формата email с использованием регулярного выражения
        if not email or not EMAIL_REGEX.match(email):
            return jsonify({
                "success": False,
                "message": "Пожалуйста, введите корректный email.",
                "email": email  # Добавляем email в ответ
            }), 400  # Возвращаем статус 400

        # Проверка, был ли email уже запомнен
        if email in saved_emails:
            return jsonify({
                "success": False,
                "message": "email уже запомнен",
                "email": email  # Добавляем email в ответ
            }), 418  # Возвращаем статус 418

        # Добавляем email в список
        saved_emails.append(email)

        # Ограничиваем список последними тремя email
        if len(saved_emails) > 3:
            saved_emails = saved_emails[-3:]

        return jsonify({
            "success": True,
            "message": "Email принят.",
            "email": email  # Добавляем email в ответ
        }), 200  # Возвращаем статус 200

    if request.method == 'GET':
        email = request.args.get('email')

        # Принимаем любое значение email для метода GET
        if email:
            return jsonify({
                "success": True,
                "message": "Email принят: " + email,
                "email": email  # Добавляем email в ответ
            }), 201  # Возвращаем статус 200
        else:
            # Если это просто загрузка страницы, возвращаем HTML
            return render_template_string(HTML_TEMPLATE)

    # Если метод не GET или PUT, возвращаем ошибку
    return jsonify({
        "success": False,
        "message": "Метод не поддерживается",
        "email": None  # Email отсутствует
    }), 405  # Возвращаем статус 405

if __name__ == '__main__':
    app.run(debug=True)
