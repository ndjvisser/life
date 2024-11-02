"""
File contains the BaseStat class which is used to create the base stats for the user.
"""


class BaseStat:
    def __init__(self, name, value=0):
        self.name = name
        self.value = value

    def increase(self, amount):
        self.value += amount

    def decrease(self, amount):
        self.value = max(0, self.value - amount)
