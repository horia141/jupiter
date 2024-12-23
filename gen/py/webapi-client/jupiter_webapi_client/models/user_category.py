from enum import Enum


class UserCategory(str, Enum):
    APP_STORE_TEST = "app-store-test"
    STANDARD = "standard"

    def __str__(self) -> str:
        return str(self.value)
