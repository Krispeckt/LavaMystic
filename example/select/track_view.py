from __future__ import annotations

from disnake import Interaction, SelectOption, MessageInteraction
from disnake.ext.commands import Bot
from disnake.ui import StringSelect, View, select, Select

from lavamystic import Playable


class SelectTrack(View):
    def __init__(self, interaction: Interaction, tracks: list[Playable]) -> None:
        self._bot: Bot = interaction.bot
        self._tracks: list[Playable] = tracks
        self._from_value: dict[str, Playable] = {}

        super().__init__(timeout=300)

    @classmethod
    async def generate(
            cls,
            interaction: Interaction,
            tracks: list[Playable]
    ) -> SelectTrack:
        self = cls(interaction, tracks)
        await self.load_tracks()

        return self

    async def load_tracks(self) -> None:
        if self._tracks:
            options = []
            self._from_value.clear()

            for i, track in enumerate(self._tracks):
                options.append(
                    SelectOption(
                        label=track.title[:10],
                        description=track.author[:20],
                        value=str(i)
                    )
                )
                self._from_value[str(i)] = track
        else:
            raise ValueError("Gave empty tracks")

    @select(
        placeholder="Выбери подходящий трэк",
        options=[
            SelectOption(
                label="Ничего не найдено"
            )
        ], custom_id="select.track.component"
    )
    async def select(self, base_select: Select, interaction: MessageInteraction) -> None:
        track = self._from_value[base_select.values[0]]

        # your logic...


