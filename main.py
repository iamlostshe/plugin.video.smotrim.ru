# Author: Alex Bratchik
# Created on: 03.04.2021
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
"""Video plugin for Smotrim.ru portal."""

from smotrim.smotrim import Smotrim
from smotrim.users import User

if __name__ == "__main__":
    Smotrim = Smotrim()
    User = User()

    User.watch(Smotrim)

