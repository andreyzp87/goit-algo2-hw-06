import string
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import requests
import matplotlib.pyplot as plt


def get_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Помилка при завантаженні тексту: {str(e)}")
        return None


def remove_punctuation(text):
    return text.translate(str.maketrans("", "", string.punctuation))


def map_function(word):
    return word.lower(), 1


def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()


def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)


def map_reduce(text):
    text = remove_punctuation(text)
    words = text.split()

    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    shuffled_values = shuffle_function(mapped_values)

    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    return dict(reduced_values)


def get_top_n_words(word_frequencies, n):
    return sorted(word_frequencies.items(), key=lambda x: x[1], reverse=True)[:n]


def visualize_top_words(word_frequencies, top_n = 10):
    top_words = get_top_n_words(word_frequencies, top_n)
    words, frequencies = zip(*top_words)

    plt.figure(figsize=(12, 6))

    colors = [plt.cm.viridis(i / top_n) for i in range(top_n)]
    bars = plt.barh(range(len(words)), frequencies, color=colors)

    plt.yticks(range(len(words)), words)
    plt.xlabel('Частота')
    plt.ylabel('Слова')
    plt.title(f'Топ-{top_n} найчастіше вживаних слів')

    for i, bar in enumerate(bars):
        width = bar.get_width()
        plt.text(width, bar.get_y() + bar.get_height() / 2,
                 f'{width:,}',
                 ha='left', va='center', fontweight='bold')

    plt.grid(True, axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()


def main():
    url = input("Введіть URL-адресу тексту для аналізу: ")
    top_n = int(input("Скільки топ-слів відобразити? (за замовчуванням 10): ") or 10)

    text = get_text(url)
    if text:
        word_frequencies = map_reduce(text)

        if word_frequencies:
            visualize_top_words(word_frequencies, top_n)
        else:
            print("Не знайдено слів для аналізу.")
    else:
        print("Помилка: Не вдалося отримати вхідний текст.")


if __name__ == "__main__":
    main()