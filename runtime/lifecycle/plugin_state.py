from enum import Enum, auto


class PluginState(Enum):

    DISCOVERED = auto()

    LOADED = auto()

    INITIALIZED = auto()

    STARTED = auto()

    RUNNING = auto()

    STOPPING = auto()

    STOPPED = auto()

    UNLOADED = auto()

    ERROR = auto()