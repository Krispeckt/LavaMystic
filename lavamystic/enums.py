import enum

__all__ = (
    "NodeStatus",
    "TrackSource",
    "DisnakeVoiceCloseType",
    "AutoPlayMode",
    "QueueMode"
)

from typing import Any, Callable

from lavamystic.utils.decode import DataReader


class NodeStatus(enum.Enum):
    """Enum representing the connection status of a Node.

    Attributes
    ----------
    DISCONNECTED
        The Node has been disconnected or has never been connected previously.
    CONNECTING
        The Node is currently attempting to connect.
    CONNECTED
        The Node is currently connected.
    """

    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2


class TrackSource(enum.Enum):
    """Enum representing a :class:`Playable` source.
    """

    YouTube = "ytsearch"
    YouTubeMusic = "ytmsearch"
    SoundCloud = "scsearch"
    Spotify = "spsearch"
    YandexMusic = "ymsearch"
    VkMusic = "vksearch"
    AppleMusic = "amsearch"


class DisnakeVoiceCloseType(enum.Enum):
    """Enum representing the various Disnake Voice Websocket Close Codes.

    Attributes
    ----------
    CLOSE_NORMAL
        1000
    UNKNOWN_OPCODE
        4001
    FAILED_DECODE_PAYLOAD
        4002
    NOT_AUTHENTICATED
        4003
    AUTHENTICATION_FAILED
        4004
    ALREADY_AUTHENTICATED
        4005
    SESSION_INVALID
        4006
    SESSION_TIMEOUT
        4009
    SERVER_NOT_FOUND
        4011
    UNKNOWN_PROTOCOL
        4012
    DISCONNECTED
        4014
    VOICE_SERVER_CRASHED
        4015
    UNKNOWN_ENCRYPTION_MODE
        4016
    """

    CLOSE_NORMAL = 1000  # Not Disnake but standard websocket
    UNKNOWN_OPCODE = 4001
    FAILED_DECODE_PAYLOAD = 4002
    NOT_AUTHENTICATED = 4003
    AUTHENTICATION_FAILED = 4004
    ALREADY_AUTHENTICATED = 4005
    SESSION_INVALID = 4006
    SESSION_TIMEOUT = 4009
    SERVER_NOT_FOUND = 4011
    UNKNOWN_PROTOCOL = 4012
    DISCONNECTED = 4014
    VOICE_SERVER_CRASHED = 4015
    UNKNOWN_ENCRYPTION_MODE = 4016


class AutoPlayMode(enum.Enum):
    """Enum representing the various AutoPlay modes.

    Attributes
    ----------
    partial
        When partial, AutoPlay will work fully autonomously
    disabled
        When disabled, AutoPlay will not do anything automatically.
    """

    enabled = 0
    partial = 1
    disabled = 2


class QueueMode(enum.Enum):
    """Enum representing the various modes on :class:`wavelink.Queue`

    Attributes
    ----------
    normal
        When set, the queue will not loop either track or history. This is the default.
    loop
        When set, the track will continuously loop.
    loop_all
        When set, the queue will continuously loop through all tracks.
    """

    normal = 0
    loop = 1
    loop_all = 2


class DefaultDecode(enum.Enum):
    @staticmethod
    def _decode_probe_info(reader: DataReader) -> dict[str, Any]:
        probe_info = reader.read_utf().decode()
        return {'probeInfo': probe_info}

    @staticmethod
    def _decode_lavasrc_fields(reader: DataReader) -> dict[str, Any]:
        if reader.remaining <= 8:
            return {}

        album_name = reader.read_nullable_utf()
        album_url = reader.read_nullable_utf()
        artist_url = reader.read_nullable_utf()
        artist_artwork_url = reader.read_nullable_utf()
        preview_url = reader.read_nullable_utf()
        is_preview = reader.read_boolean()

        return {
            'albumName': album_name,
            'albumUrl': album_url,
            'artistUrl': artist_url,
            'artistArtworkUrl': artist_artwork_url,
            'previewUrl': preview_url,
            'isPreview': is_preview
        }

    @classmethod
    def get_decoder_mapping(cls) -> dict[str, Callable[[DataReader], dict[str, Any]]]:
        return {
            "http": cls._decode_probe_info,
            "local": cls._decode_probe_info,
            "deezer": cls._decode_lavasrc_fields,
            "spotify": cls._decode_lavasrc_fields,
            "applemusic": cls._decode_lavasrc_fields,
            "yandexmusic": cls._decode_lavasrc_fields,
            "vkmusic": cls._decode_lavasrc_fields,
        }.copy()
