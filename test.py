import logging
import concurrent.futures
import threading
from TTS.elevenlabs_tts_hendler import ElevenLabsTTSHandler
import torch

# Настройка логгирования до создания любого логгера
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,  # Установите уровень логгирования на DEBUG
)

# Настройка логгирования для библиотеки torch
torch._logging.set_logs(graph_breaks=True, recompiles=True, cudagraphs=True)

# Создаем глобальный логгер
logger = logging.getLogger(__name__)

# Допустим, у вас есть два разных текста для генерации
texts_to_process = ["Hello, how are you?", "Привет, как дела?", "Ты супер!", "Сколько килогам в граме?", "Ииииииихххааа...."]

def run_tts_process(handler, text):
    audio_chunks = []
    for audio_chunk in handler.process(text):
        audio_chunks.append(audio_chunk)
    return audio_chunks

if __name__ == "__main__":
    # Создание экземпляра вашего обработчика
    tts_handler = ElevenLabsTTSHandler()

    # Установка условий прослушивания (добавлено для примера)
    should_listen = threading.Event()
    tts_handler.setup(should_listen, proxy_url = "http://RGHu6U:WP6Z4s@168.80.200.166:8000", api_key = "sk_bfac76ea86730d4708bfc6d5b740084933672b2dd359ec1c")

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Запускаем метод process в двух потоках
        futures = [executor.submit(run_tts_process, tts_handler, text) for text in texts_to_process]

        # Ожидаем завершения всех потоков
        for future in concurrent.futures.as_completed(futures):
            try:
                audio_chunks = future.result()
                print(f"Processed audio chunks")
            except Exception as e:
                print(f"An error occurred: {e}")
