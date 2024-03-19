from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

import aiohttp
from disnake.ext import tasks
from loguru import logger

from .enums import NodeStatus
from .exceptions import AuthorizationFailedException, NodeException
from .payloads import *
from .tracks import Playable

if TYPE_CHECKING:
    from .node import Node
    from .player import Player
    from .types.request import UpdateSessionRequest
    from .types.state import PlayerState
    from .types.websocket import (
        TrackExceptionPayload, 
        WebsocketOP, 
        ReadyOP, 
        PlayerUpdateOP, 
        TrackStartEvent,
        TrackEndEvent, 
        TrackExceptionEvent, 
        TrackStuckEvent, 
        WebsocketClosedEvent
    )


class Websocket:
    def __init__(self, *, node: Node) -> None:
        self.node: Node = node

        self._now_retries: int = 0
        self.retries: int = 10

        self.socket: aiohttp.ClientWebSocketResponse | None = None
        self.keep_alive_task: asyncio.Task[None] | None = None

    PATTERN = "v4/websocket"

    @property
    def headers(self) -> dict[str, str]:
        assert self.node.client is not None
        assert self.node.client.user is not None

        data = {
            "Authorization": self.node.password,
            "User-Id": str(self.node.client.user.id),
            "Client-Name": f"MysticLink/1.0.0",
        }

        if self.node.session_id:
            data["Session-Id"] = self.node.session_id

        return data

    def is_connected(self) -> bool:
        return self.socket is not None and not self.socket.closed

    async def _update_node(self) -> None:
        if self.node.resume_timeout > 0:
            udata: UpdateSessionRequest = {"resuming": True, "timeout": self.node.resume_timeout}
            await self.node.update_session(data=udata)

    @tasks.loop(seconds=30)
    async def _connect(self) -> None:
        uri: str = f"{self.node.uri.removesuffix('/')}/" + self.PATTERN
        try:
            self.socket = await self.node._session.ws_connect(
                url=uri, heartbeat=self.node.heartbeat, headers=self.headers
            )
        except Exception as e:
            if isinstance(e, aiohttp.WSServerHandshakeError) and e.status == 401:
                await self.cleanup()
                raise AuthorizationFailedException from e
            elif isinstance(e, aiohttp.WSServerHandshakeError) and e.status == 404:
                await self.cleanup()
                raise NodeException from e
            elif (
                    isinstance(e, aiohttp.ClientConnectorError)
                    or isinstance(e, ConnectionRefusedError)
                    or isinstance(e, aiohttp.ClientOSError)
            ):
                pass
            else:
                logger.warning(f"Node threw an error: {e} ({type(e).__name__})")

        if self.is_connected():
            logger.info(
                f"{self.node.identifier} "
                f"was success to successfully connect/reconnect to Lavalink after "
                f'"{self._now_retries + 1}" connection attempt.'
            )

            self._now_retries = 0
            self.keep_alive.start()
            return self._connect.cancel()

        if self._now_retries > self.retries:
            logger.debug(
                f"{self.node.identifier} was unable to successfully connect/reconnect to Lavalink after "
                f'"{self._now_retries}" connection attempt. This Node has exhausted the retry count.'
            )

            await self.cleanup()
            return self._connect.cancel()

        self._now_retries += 1
        logger.debug(f'{self.node!r} retrying websocket connection in "30" seconds.')

    def connect(self) -> None:
        self.node._status = NodeStatus.CONNECTING

        if self.keep_alive_task:
            try:
                self.keep_alive_task.cancel()
            except Exception as e:
                _ = e

        self._connect.start()

    @tasks.loop()
    async def keep_alive(self) -> None:
        message: aiohttp.WSMessage = await self.socket.receive()

        if message.type in (
                aiohttp.WSMsgType.CLOSED,
                aiohttp.WSMsgType.CLOSING,
        ):
            self.dispatch("connection_lost", self.node.client.voice_clients)
            self.connect()
            return self.keep_alive.cancel()

        if message.data:
            data: WebsocketOP = message.json()

            if data["op"] == "ready":
                data: ReadyOP
                resumed: bool = data["resumed"]
                session_id: str = data["sessionId"]

                self.node._status = NodeStatus.CONNECTED
                self.node._session_id = session_id

                await self._update_node()

                ready_payload: NodeReadyEventPayload = NodeReadyEventPayload(
                    node=self.node, resumed=resumed, session_id=session_id
                )
                self.dispatch("node_ready", ready_payload)

            elif data["op"] == "playerUpdate":
                data: PlayerUpdateOP
                player: Player | None = self.get_player(data["guildId"])
                state: PlayerState = data["state"]

                payload: PlayerUpdateEventPayload = PlayerUpdateEventPayload(player=player, state=state)
                self.dispatch("player_update", payload)

                if player:
                    asyncio.create_task(player.update_event(payload))

            elif data["op"] == "stats":
                payload: StatsEventPayload = StatsEventPayload(data=data)
                self.node._total_player_count = payload.players
                self.dispatch("stats_update", payload)

            elif data["op"] == "event":
                player: Player | None = self.get_player(data["guildId"])

                if data["type"] == "TrackStartEvent":
                    data: TrackStartEvent

                    track: Playable = Playable(data["track"])

                    payload: TrackStartEventPayload = TrackStartEventPayload(player=player, track=track)
                    self.dispatch("track_start", payload)

                    if player:
                        player.track_start()

                elif data["type"] == "TrackEndEvent":
                    data: TrackEndEvent

                    track: Playable = Playable(data["track"])
                    reason: str = data["reason"]

                    if player and reason != "replaced":
                        player._current = None

                    payload: TrackEndEventPayload = TrackEndEventPayload(player=player, track=track, reason=reason)
                    self.dispatch("track_end", payload)

                    if player:
                        asyncio.create_task(player.auto_play_event(payload))

                elif data["type"] == "TrackExceptionEvent":
                    data: TrackExceptionEvent

                    track: Playable = Playable(data["track"])
                    exception: TrackExceptionPayload = data["exception"]

                    payload: TrackExceptionEventPayload = TrackExceptionEventPayload(
                        player=player, track=track, exception=exception
                    )
                    self.dispatch("track_exception", payload)

                elif data["type"] == "TrackStuckEvent":
                    data: TrackStuckEvent

                    track: Playable = Playable(data["track"])
                    threshold: int = data["thresholdMs"]

                    payload: TrackStuckEventPayload = TrackStuckEventPayload(
                        player=player, track=track, threshold=threshold
                    )
                    self.dispatch("track_stuck", payload)

                elif data["type"] == "WebSocketClosedEvent":
                    data: WebsocketClosedEvent

                    code: int = data["code"]
                    reason: str = data["reason"]
                    by_remote: bool = data["byRemote"]

                    payload: WebsocketClosedEventPayload = WebsocketClosedEventPayload(
                        player=player, code=code, reason=reason, by_remote=by_remote
                    )
                    self.dispatch("websocket_closed", payload)

                else:
                    other_payload: ExtraEventPayload = ExtraEventPayload(node=self.node, player=player, data=data)
                    self.dispatch("extra_event", other_payload)
            else:
                logger.warning(
                    f"'Received an unknown OP from Lavalink '{data['op']}'. Disregarding."
                )

    def get_player(self, guild_id: str | int) -> Player | None:
        return self.node.get_player(int(guild_id))

    def dispatch(self, event: str, /, *args: Any, **kwargs: Any) -> None:
        assert self.node.client is not None

        self.node.client.dispatch(f"mystic_{event}", *args, **kwargs)

    async def cleanup(self) -> None:
        if self.socket:
            try:
                await self.socket.close()
            except Exception as e:
                _ = e

        if self.keep_alive_task:
            try:
                self.keep_alive_task.cancel()
            except Exception as e:
                _ = e

        self.node._status = NodeStatus.DISCONNECTED
        self.node._session_id = None
        self.node._players = {}

        self.node._websocket = None

        logger.info(f"Successfully cleaned up the websocket for {self.node!r}")
