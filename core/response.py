#
# core/response.py
#
# Application Response
#
# 役割:
#   ・API / AppService 共通レスポンス
#   ・処理結果、メッセージ、データを統一する
#

class Response:

    OK = "OK"
    REJECTED = "REJECTED"
    ERROR = "ERROR"


    def __init__(
        self,
        result=OK,
        message="",
        data=None,
    ):

        self.result = result
        self.message = message
        self.data = data


    def to_dict(self):

        return {
            "result": self.result,
            "message": self.message,
            "data": self.data,
        }


    @classmethod
    def ok(cls, data=None, message=""):

        return cls(
            result=cls.OK,
            message=message,
            data=data,
        ).to_dict()


    @classmethod
    def rejected(cls, message):

        return cls(
            result=cls.REJECTED,
            message=message,
            data=None,
        ).to_dict()


    @classmethod
    def error(cls, message):

        return cls(
            result=cls.ERROR,
            message=message,
            data=None,
        ).to_dict()