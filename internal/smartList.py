class SmartList(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._freedIndices = []

    def add(self, item) -> int:
        if len(self._freedIndices) > 0:
            index = self._freedIndices.pop(0)
            if self[index] is not None:
                raise ValueError("Index is freed but still occupied")
            self[index] = item
            return index
        else:
            self.append(item)
            return len(self) - 1
    
    def remove(self, index: int):
        if index == len(self) - 1:
            self.pop()
        elif 0 <= index < len(self) - 1:
            self._freedIndices.append(index)
            self[index] = None
        else:
            raise IndexError("Index out of bounds")