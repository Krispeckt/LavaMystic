from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types.response import ErrorResponse, LoadedErrorPayload


__all__ = (
    "BaseMysticException",
    "NodeException",
    "InvalidClientException",
    "AuthorizationFailedException",
    "InvalidNodeException",
    "LavalinkException",
    "LavalinkLoadException",
    "InvalidChannelStateException",
    "ChannelTimeoutException",
    "QueueEmpty",
)


class BaseMysticException(Exception):
    """Base lavalink Exception class.

    All lavaMystic exceptions derive from this exception.
    """


class NodeException(BaseMysticException):
    """Error raised when an Unknown or Generic error occurs on a Node.

    This exception may be raised when an error occurs reaching your Node.

    Attributes
    ----------
    status: int | None
        The status code received when making a request. Could be None.
    """

    def __init__(self, msg: str | None = None, status: int | None = None) -> None:
        super().__init__(msg)

        self.status = status


class InvalidClientException(BaseMysticException):
    """Exception raised when an invalid :class:`discord.Client`
    is provided while connecting a :class:`Node`.
    """


class AuthorizationFailedException(BaseMysticException):
    """Exception raised when Lavalink fails to authenticate a :class:`~Node`, with the provided password."""


class InvalidNodeException(BaseMysticException):
    """Exception raised when a :class:`Node` is tried to be retrieved from the
    :class:`Pool` without existing, or the ``Pool`` is empty.
    """


class LavalinkException(BaseMysticException):
    def __init__(
            self, msg: str | None = None, /, *,
            data: ErrorResponse
    ) -> None:
        self.timestamp: int = data["timestamp"]
        self.status: int = data["status"]
        self.error: str = data["error"]
        self.trace: str | None = data.get("trace")
        self.path: str = data["path"]

        if not msg:
            msg = f"Failed to fulfill request to Lavalink: status={self.status}, reason={self.error}, path={self.path}"

        super().__init__(msg)


class LavalinkLoadException(BaseMysticException):
    """Exception raised when an error occurred loading tracks via Lavalink.

    Attributes
    ----------
    error: str
        The error message from Lavalink.
    severity: str
        The severity of this error sent via Lavalink.
    cause: str
        The cause of this error sent via Lavalink.
    """

    def __init__(
            self, msg: str | None = None, /, *,
            data: LoadedErrorPayload
    ) -> None:
        self.error: str = data["message"]
        self.severity: str = data["severity"]
        self.cause: str = data["cause"]

        if not msg:
            msg = f"Failed to Load Tracks: error={self.error}, severity={self.severity}, cause={self.cause}"

        super().__init__(msg)


class InvalidChannelStateException(BaseMysticException):
    """Exception raised when a :class:`~Player` tries to connect to an invalid channel or
    has invalid permissions to use this channel.
    """


class ChannelTimeoutException(BaseMysticException):
    """Exception raised when connecting to a voice channel times out."""


class QueueEmpty(BaseMysticException):
    """Exception raised when you try to retrieve from an empty queue."""
