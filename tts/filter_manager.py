class FilterManager:

    def __init__(self):

        self.filters = []

        # Nombre del filtro que canceló el último mensaje procesado.
        self.last_blocked_by = None

    def add(self, filter_instance):

        self.filters.append(filter_instance)

    def process(self, message):

        self.last_blocked_by = None

        for filter_instance in self.filters:

            if message is None:
                return None

            message = filter_instance.process(message)

            if message is None:
                self.last_blocked_by = type(filter_instance).__name__

        return message

    def names(self):

        return [type(f).__name__ for f in self.filters]

    def clear(self):

        self.filters.clear()
