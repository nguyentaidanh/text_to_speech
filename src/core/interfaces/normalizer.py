from abc import ABC, abstractmethod

class TextNormalizerInterface(ABC):
    @abstractmethod
    def normalize(self, text: str) -> str:
        """Transform raw text into fully spoken Vietnamese text."""
        pass
