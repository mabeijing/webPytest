from typing import Any


class DataBase:
    def __init__(self, data: Any):
        self.data = data

    def closed(self):
        print("优雅退出数据库")
