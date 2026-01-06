"""Video plugin for Smotrim.ru portal."""

from smotrim.smotrim import Smotrim
from smotrim.users import User

if __name__ == "__main__":
    Smotrim = Smotrim()
    User = User()

    User.watch(Smotrim)
