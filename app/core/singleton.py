import threading
from typing import Any


class SingletonMeta(type):
    """
    A thread-safe metaclass that ensures only one instance of a class exists.
    """

    _instances = {}
    _lock = threading.Lock()  # Lock for thread safety during first instantiation

    def __call__(cls, *args, **kwargs) -> Any:  # type: ignore[reportUnknownParameterType]
        """
        This method is called when the class is instantiated (e.g., MyClass()).
            It ensures that only one instance is created.
        """
        # Double-checked locking for thread safety
        if cls not in cls._instances:  # First check (avoids locking if instance exists)
            with cls._lock:
                # Second check (inside lock) to prevent race condition
                if cls not in cls._instances:
                    # Call the default __call__ behavior (runs __new__ and __init__)
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]
