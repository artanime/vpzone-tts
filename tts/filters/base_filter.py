from abc import ABC, abstractmethod


class BaseFilter(ABC):

    @abstractmethod
    def process(self, message):
        """
        Recibe un TTSMessage.

        Devuelve:
            TTSMessage -> continúa
            None -> cancelar mensaje
        """
        pass