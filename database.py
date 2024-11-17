import sqlite3


# Создание базы данных и таблицы
def initialize_database():
    """
    Создает базу данных mydatabase.db и таблицу с названием user_cryptos,
    если она еще не существует.
    """
    connection = sqlite3.connect("mydatabase.db")
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_cryptos (
            id INTEGER,
            crypta TEXT
        )
    ''')
    connection.commit()
    connection.close()


# Функция для вставки значений в таблицу
def insert_values(user_id: int, crypta: str):
    """
    Вставляет значения id и crypta в таблицу user_cryptos.

    :param user_id: Идентификатор пользователя (id).
    :param crypta: Название криптовалюты (crypta).
    """
    connection = sqlite3.connect("mydatabase.db")
    cursor = connection.cursor()
    cursor.execute('INSERT INTO user_cryptos (id, crypta) VALUES (?, ?)', (user_id, crypta))
    connection.commit()
    connection.close()


# Функция для получения значений из таблицы
def return_values(user_id: int):
    """
    Возвращает список всех значений crypta из таблицы user_cryptos
    для заданного id.

    :param user_id: Идентификатор пользователя (id).
    :return: Список всех значений crypta для заданного id.
    """
    connection = sqlite3.connect("mydatabase.db")
    cursor = connection.cursor()
    cursor.execute('SELECT crypta FROM user_cryptos WHERE id = ?', (user_id,))
    rows = cursor.fetchall()
    connection.close()

    # Извлечение значений crypta в список
    result = [row[0] for row in rows]
    return result

def return_user_id():
    connection = sqlite3.connect("mydatabase.db")
    cursor = connection.cursor()
    cursor.execute('SELECT id FROM user_cryptos')

    rows = cursor.fetchall()
    connection.close()

    # Извлечение значений crypta в список
    result = [row[0] for row in rows]

    # Преобразуем в set, чтобы избавиться от дубликатов
    result = list(set(result))
    return result

