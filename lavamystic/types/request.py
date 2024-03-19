from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeAlias, TypedDict

if TYPE_CHECKING:
    from typing_extensions import NotRequired

    from .filters import FilterPayload


class VoiceRequest(TypedDict):
    token: str
    endpoint: str | None
    sessionId: str


class TrackRequest(TypedDict, total=False):
    encoded: str | None
    identifier: str
    userData: dict[str, Any]


class _BaseRequest(TypedDict, total=False):
    voice: VoiceRequest
    position: int
    endTime: int | None
    volume: int
    paused: bool
    filters: FilterPayload
    track: TrackRequest


class EncodedTrackRequest(_BaseRequest):
    encodedTrack: str | None


class IdentifierRequest(_BaseRequest):
    identifier: str


class UpdateSessionRequest(TypedDict):
    resuming: NotRequired[bool]
    timeout: NotRequired[int]


Request: TypeAlias = _BaseRequest | EncodedTrackRequest | IdentifierRequest
