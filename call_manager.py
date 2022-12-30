import dataclasses
import requests
import logging
import re
import socket

log = logging.getLogger("SMS")
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)


@dataclasses.dataclass()
class CallResponse:
    result: str = ""
    id: int = 0
    code: int = 0
    price: float = 0
    error_code: str = ''


class CallTransport:
    _URL = "https://vp.voicepassword.ru/api/voice-password/send/"

    def __init__(self, api_id):
        self._api_id = api_id

    def send(self, phone: str) -> CallResponse:
        if not self.validate_phone(phone):
            log.error("Invalid phone number")
            return CallResponse()

        response = requests.post(self._URL, json=dict(
            security={"apiKey": self._api_id},
            number=phone,
        )).json()

        log.debug("Response %s", response)

        if response["result"] == "ok":
            return CallResponse(
                result='ok',
                code=response['code'],
                price=response['price'],
                id=response["id"]
            )

        log.debug("Error status %s", response)
        return CallResponse(
            error_code=response["error_code"],
            code=0
        )

    @classmethod
    def validate_phone(cls, phone):
        return re.match(r"^7[0-9]{10}$", phone)
