#
# core/response.py
#
# Application Response
#
# 役割:
#   ・API / Service 共通レスポンス
#   ・処理結果、Response ID、メッセージ、データを統一する
#
# Response構造:
#   ・result      : 処理結果
#   ・response_id : Response / Notify / Voice 共通の意味ID
#   ・message     : 表示・通知するメッセージ
#   ・data        : APIで返す業務データ
#
# response_idについて:
#   ・Trade IDなどの業務IDとは別物
#   ・「このResponseが何を意味するか」を識別するID
#   ・Notifyでメッセージ種別を識別するために使用する
#   ・VoiceManagerで音声を識別するために使用する
#   ・WAVファイル名にも使用するため、意味のある文字列を指定する
#
# 例:
#   response_id="TRADE_REGISTERED"
#   response_id="TRADE_PAUSED"
#   response_id="ENGINE_STARTED"
#
# Result:
#   OK       : 処理成功
#   REJECTED : Serviceによる業務上の拒否
#   ERROR    : Engine / 内部処理によるエラー
#

class Response:

    # ---------------------
    # Result
    # ---------------------

    OK = "OK"
    REJECTED = "REJECTED"
    ERROR = "ERROR"


    # ---------------------
    # Constructor
    # ---------------------

    def __init__(
        self,
        result=OK,
        response_id=None,
        message="",
        data=None,
    ):

        self.result = result
        self.response_id = response_id
        self.message = message
        self.data = data


    # ---------------------
    # Dictionary
    # ---------------------

    def to_dict(self):

        return {
            "result": self.result,
            "response_id": self.response_id,
            "message": self.message,
            "data": self.data,
        }


    # ---------------------
    # OK Response
    # ---------------------

    @classmethod
    def ok(
        cls,
        response_id=None,
        message="",
        data=None,
    ):

        return cls(
            result=cls.OK,
            response_id=response_id,
            message=message,
            data=data,
        ).to_dict()


    # ---------------------
    # Rejected Response
    # ---------------------

    @classmethod
    def rejected(
        cls,
        response_id=None,
        message="",
    ):

        return cls(
            result=cls.REJECTED,
            response_id=response_id,
            message=message,
            data=None,
        ).to_dict()


    # ---------------------
    # Error Response
    # ---------------------

    @classmethod
    def error(
        cls,
        response_id=None,
        message="",
    ):

        return cls(
            result=cls.ERROR,
            response_id=response_id,
            message=message,
            data=None,
        ).to_dict()