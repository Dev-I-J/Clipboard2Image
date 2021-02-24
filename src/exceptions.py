from typing import Any


class NoImageInClipboard(Exception):
    def __init__(_, image: Any) -> None:
        super().__init__(f"{image} is not an image")
