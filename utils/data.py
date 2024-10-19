import threading

class ImmutableDataChain:
    def __init__(self, value=None, tag=None, save_data=True, previous=None, index=None):
        """
        tag - ключ значения. Может быть None, но это означает, что данные будут потеряны после add_data.
        value - сохраняемое значение.
        previous - ссылка на предыдущий экземпляр данных.
        index - индекс экземпляра класса в цепочке экземпляров, созданных из того же экземпляра с помощью add_data.
        save_data - если False, предыдущие данные не будут доступны в новом экземпляре.
        """
        self._key = tag
        self._value = value
        self._previous = previous
        self.index = index
        self._counter = -1
        self._save_data = save_data
        self._lock = threading.Lock()  # Блокировка для синхронизации

    def add_data(self, value, tag, save_data=True):
        with self._lock:
            self._counter += 1
            if self._key is None or not self._save_data:
                return ImmutableDataChain(value, tag, save_data, self._previous, self._counter)
            else:
                return ImmutableDataChain(value, tag, save_data, self, self._counter)

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
