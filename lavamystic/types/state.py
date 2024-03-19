from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from typing_extensions import NotRequired


class PlayerState(TypedDict):
    time: int
    position: int
    connected: bool
    ping: int


class VoiceState(TypedDict, total=False):
    token: str
    endpoint: str | None
    session_id: str


class PlayerVoiceState(TypedDict):
    voice: VoiceState
    channel_id: NotRequired[str]
    track: NotRequired[str]
    position: NotRequired[int]
