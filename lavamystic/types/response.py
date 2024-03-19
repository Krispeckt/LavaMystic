from typing import TYPE_CHECKING, Literal, TypedDict

if TYPE_CHECKING:
    from typing_extensions import Never, NotRequired

    from .filters import FilterPayload
    from .state import PlayerState
    from .stats import CPUStats, FrameStats, MemoryStats
    from .tracks import PlaylistPayload, TrackPayload


class ErrorResponse(TypedDict):
    timestamp: int
    status: int
    error: str
    trace: NotRequired[str]
    message: str
    path: str


class LoadedErrorPayload(TypedDict):
    message: str
    severity: str
    cause: str


class VoiceStateResponse(TypedDict, total=False):
    token: str
    endpoint: str | None
    sessionId: str


class PlayerResponse(TypedDict):
    guildId: str
    track: NotRequired[TrackPayload]
    volume: int
    paused: bool
    state: PlayerState
    voice: VoiceStateResponse
    filters: FilterPayload


class UpdateResponse(TypedDict):
    resuming: bool
    timeout: int


class TrackLoadedResponse(TypedDict):
    loadType: Literal["track"]
    data: TrackPayload


class PlaylistLoadedResponse(TypedDict):
    loadType: Literal["playlist"]
    data: PlaylistPayload


class SearchLoadedResponse(TypedDict):
    loadType: Literal["search"]
    data: list[TrackPayload]


class EmptyLoadedResponse(TypedDict):
    loadType: Literal["empty"]
    data: dict[Never, Never]


class ErrorLoadedResponse(TypedDict):
    loadType: Literal["error"]
    data: LoadedErrorPayload


class VersionPayload(TypedDict):
    semver: str
    major: int
    minor: int
    patch: int
    preRelease: NotRequired[str]
    build: NotRequired[str]


class GitPayload(TypedDict):
    branch: str
    commit: str
    commitTime: int


class PluginPayload(TypedDict):
    name: str
    version: str


class InfoResponse(TypedDict):
    version: VersionPayload
    buildTime: int
    git: GitPayload
    jvm: str
    lavaplayer: str
    sourceManagers: list[str]
    filters: list[str]
    plugins: list[PluginPayload]


class StatsResponse(TypedDict):
    players: int
    playingPlayers: int
    uptime: int
    memory: MemoryStats
    cpu: CPUStats
    frameStats: NotRequired[FrameStats]
