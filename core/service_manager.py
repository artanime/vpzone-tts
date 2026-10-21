class ServiceManager:

    def __init__(self):

        self.services = []

    def register(self, service):

        self.services.append(service)

    def start(self):

        for service in self.services:

            if hasattr(service, "start"):

                service.start()

    def stop(self):

        for service in self.services:

            if hasattr(service, "stop"):

                service.stop()