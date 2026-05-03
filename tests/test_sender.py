import pytest


class FakeClient:
    def __init__(self):
        self.sent = None

    async def send_message(self, target, text):
        self.sent = (target, text)


@pytest.mark.asyncio
async def test_send_message_success():
    from app.sender import send_message_safe

    client = FakeClient()

    await send_message_safe(client, "me", "hello")

    assert client.sent == ("me", "hello")