from typing import TYPE_CHECKING, Any, TypedDict

if TYPE_CHECKING:
    from typing_extensions import NotRequired


class TrackInfoPayload(TypedDict):
    identifier: str
    isSeekable: bool
    author: str
    length: int
    isStream: bool
    position: int
    title: str
    uri: NotRequired[str]
    artworkUrl: NotRequired[str]
    isrc: NotRequired[str]
    sourceName: str


class PlaylistInfoPayload(TypedDict):
    name: str
    selectedTrack: int


class TrackPayload(TypedDict):
    encoded: str
    info: TrackInfoPayload
    pluginInfo: dict[Any, Any]
    userData: dict[str, Any]


class PlaylistPayload(TypedDict):
    info: PlaylistInfoPayload
    tracks: list[TrackPayload]
    pluginInfo: dict[Any, Any]
