from typing import Final

from environs import env

FLOAT_TEST_DELAY: Final[float] = 1.0
STRING_URL_WEBHOOK: Final[str] = env.url("TESTS_WEBHOOK_URL").geturl()
STRING_URL_DISCORD: Final[str] = "https://discord.com/"
STRING_URL_GITHUB: Final[str] = "https://github.com/EthanC/Clyde"
STRING_URL_IMAGE_1: Final[str] = "https://i.imgur.com/QUootDB.png"
STRING_URL_IMAGE_2: Final[str] = "https://i.imgur.com/kVsDPWa.png"
STRING_URL_IMAGE_3: Final[str] = "https://i.imgur.com/XQ5r65a.png"
STRING_URL_IMAGE_4: Final[str] = "https://i.imgur.com/NaljlbX.png"
STRING_URL_ICON_1: Final[str] = "https://i.imgur.com/hO7apmW.png"
STRING_URL_ICON_2: Final[str] = "https://i.imgur.com/D07XMMQ.png"
STRING_URL_ICON_3: Final[str] = "https://i.imgur.com/CtdvS5v.png"
STRING_URL_ICON_4: Final[str] = "https://i.imgur.com/hPX7hn9.png"
STRING_COLOR_WHITE: Final[str] = "#FFFFFF"
STRING_COLOR_BLACK: Final[str] = "000000"
STRING_EMPTY: Final[str] = ""
STRING_WORD: Final[str] = "Lorem"
STRING_EXTRA_SHORT: Final[str] = "Lorem ipsum"
STRING_SHORT: Final[str] = "Lorem ipsum dolor sit amet."
STRING_MEDIUM: Final[str] = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
)
STRING_LONG: Final[str] = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
)
STRING_LONG_MARKDOWN: Final[str] = (
    "Lorem ipsum dolor sit amet, **consectetur adipiscing elit**, sed do eiusmod tempor ||incididunt|| ut labore et dolore _magna aliqua_.\nUt enim ad minim veniam, quis `nostrud` exercitation ullamco laboris nisi ut aliquip ex ea commodo `consequat`.\n\nDuis aute irure dolor in :smiling_face_with_tear: reprehenderit **in** voluptate velit esse cillum dolore eu fugiat nulla pariatur. *Excepteur sint* occaecat __cupidatat__ non proident, sunt in culpa __**qui**__ officia deserunt mollit anim id est laborum."
)
STRING_EXTRA_LONG: Final[str] = STRING_LONG * 10
STRING_ID_USER: Final[str] = "264915286962995210"
STRING_ID_ROLE: Final[str] = "409995554248982528"
STRING_ID_THREAD: Final[str] = "1371232563271696456"
STRING_LIST_SHORT: Final[list[str]] = ["Lorem", "Ipsum", "Dolor"]
STRING_LIST_MEDIUM: Final[list[str]] = ["Lorem", "Ipsum", "Dolor", "Sit", "Amet"]
INT_TIMESTAMP: Final[int] = 1516514400
INT_EXTRA_SHORT: Final[int] = 7
INT_SHORT: Final[int] = 128
INT_MEDIUM: Final[int] = 1337
INT_LONG: Final[int] = 69420999
