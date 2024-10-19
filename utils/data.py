import threading

class ImmutableDataChain:
    def __init__(self, value=None, key=None, save_data=True, previous=None, index=None):
        """
        key - ключ значения. Может быть None, но это означает, что данные будут потеряны после add_data.
        value - сохраняемое значение.
        previous - ссылка на предыдущий экземпляр данных.
        index - индекс экземпляра класса в цепочке экземпляров, созданных из того же экземпляра с помощью add_data.
        save_data - если False, предыдущие данные не будут доступны в новом экземпляре.
        """
        self._key = key
        self._value = value
        self._previous = previous
        self.index = index
        self._counter = -1
        self._save_data = save_data
        self._lock = threading.Lock()  # Блокировка для синхронизации

    def add_data(self, value, key=None, save_data=True):
        with self._lock:
            self._counter += 1
            if self._key is None or not self._save_data:
                return ImmutableDataChain(value, key, save_data, self._previous, self._counter)
            else:
                return ImmutableDataChain(value, key, save_data, self, self._counter)

    def get_data(self, key=None):
        with self._lock:
            # Рекурсивно ищем значение по ключу
            if key is None or self._key == key:
                return self._value
            elif self._previous is not None:
                return self._previous.get_data(key)
            else:
                return None

    def to_dict(self):
        with self._lock:
            data_dict = {}
            current = self
            while current is not None:
                if current._key is not None and current._key not in data_dict:
                    data_dict[current._key] = current._value
                current = current._previous
            return data_dict

    def get(self, key, default=None):
        value = self.get_data(key)
        return value if value is not None else default

    def __getitem__(self, key):
        value = self.get_data(key)
        if value is None:
            raise KeyError(f"Ключ '{key}' не найден")
        return value

    def __setitem__(self, key, value):
        return self.add_data(value, key)

example_data = {
    "user_audio":None,
    "text":None,
    "language_code":None,
    "start_phrase":None,
    "llm_sentence":None,
    "output_audio_iterator": None,
    "output_audio_chunk":None
}