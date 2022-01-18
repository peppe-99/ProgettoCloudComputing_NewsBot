from typing import List


class RegisteredUser:
    def __init__(self, email: str, preferenze: List[str]):
        self.email = email
        self.preferenze = preferenze

    def set_email(self, email: str):
        self.email = email

    def set_preferenze(self, preferenze: List[str]):
        self.preferenze = preferenze

    def add_preferenza(self, preferenza: str):
        self.preferenze.append(preferenza)