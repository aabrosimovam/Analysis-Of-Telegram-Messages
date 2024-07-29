import json
import pandas as pd
from collections import Counter
import nltk
# nltk.download('stopwords')
from nltk.corpus import stopwords


# Загрузка данных из JSON файла
with open('result_svet.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Функция для преобразования текста в строку и приведения к нижнему регистру
def convert_to_string(text):
    if isinstance(text, list):
        return ' '.join([str(item) for item in text]).lower()
    return str(text).lower()

# Функция для подсчета упоминаний слова
def count_word_mentions(text, word):
    return text.split().count(word)

# Функция для определения времени суток
def get_time_of_day(hour):
    if 5 <= hour < 12:
        return 'утро'
    elif 12 <= hour < 17:
        return 'день'
    elif 17 <= hour < 21:
        return 'вечер'
    else:
        return 'ночь'

# Функция для получения самых часто используемых слов
def get_common_words(text):
    words = text.split()
    return Counter([word for word in words if word not in stop_words and len(word) > 4]).most_common(10)

# Преобразование данных в DataFrame и фильтрация текстовых сообщений
df = pd.DataFrame(data['messages'])
df = df[df['type'] == 'message']

# Убедимся, что работаем только с текстовыми сообщениями и убираем пустые сообщения
df = df.dropna(subset=['text'])
df = df[df['text'].apply(lambda x: isinstance(x, str) and x.strip() != '')]

df['text'] = df['text'].apply(convert_to_string)

# Количество сообщений от каждого участника
messages_per_user = df['from'].value_counts()

# Запрашиваем слово для поиска
word_to_search = input("Введите слово для поиска: ").lower()
df['word_mentions'] = df['text'].apply(lambda x: count_word_mentions(x, word_to_search))

# Суммирование упоминаний слова по участникам
word_mentions_per_user = df.groupby('from')['word_mentions'].sum()

# Добавление столбца с длиной каждого сообщения
df['message_length'] = df['text'].apply(len)
characters_per_user = df.groupby('from')['message_length'].sum()

# Анализ активности по времени суток
df['date'] = pd.to_datetime(df['date'])
df['hour'] = df['date'].dt.hour
df['time_of_day'] = df['hour'].apply(get_time_of_day)

# Считаем количество сообщений, отправленных утром, днем и вечером для каждого участника
messages_per_time_of_day = df.groupby(['from', 'time_of_day']).size().unstack(fill_value=0)
most_active_time_per_user = messages_per_time_of_day.idxmax(axis=1)

# Анализ общего списка самых часто используемых слов в переписке
stop_words = set(stopwords.words('russian'))
all_words = ' '.join(df['text']).split()
common_words = Counter([word for word in all_words if word not in stop_words and len(word) > 4]).most_common(20)

# Анализ часто используемых слов для каждого участника
common_words_per_user = df.groupby('from')['text'].apply(lambda x: get_common_words(' '.join(x)))

# Вывод результатов
print(f"Количество упоминаний слова '{word_to_search}' каждым участником:")
print(word_mentions_per_user)
print("\nКоличество сообщений от каждого участника:")
print(messages_per_user)
print("\nКоличество символов, написанных каждым участником:")
print(characters_per_user)
print("\nНаиболее активное время суток для каждого участника:")
print(most_active_time_per_user)

print("\nСамые часто используемые слова в переписке:")
for word, count in common_words:
    print(f"{word}: {count}")

print("\nЧасто используемые слова для каждого участника:")
for user, words_list in common_words_per_user.items():
    words_str = ', '.join([f"{word[0]} ({word[1]})" for word in words_list])
    print(f"{user}: {words_str}")
