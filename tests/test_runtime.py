import pytest
from app.runtime import ClientRunner


@pytest.mark.asyncio
async def test_runner_init():
    runner = ClientRunner()
    assert runner is not None