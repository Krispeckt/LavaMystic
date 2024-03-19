import disnake
from disnake import Intents
from disnake.ext import commands

from lavamystic import Pool, Player, Node, Playable, TrackSource


class MusicCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self._bot = bot

    async def setup_book(self) -> None:
        await Pool.connect(
            nodes=[
                Node(
                    uri="http://localhost:2333",
                    password="youshallnotpass",
                    identifier="Epsilon"
                )
            ],
            client=self._bot,
            cache_capacity=1024
        )

    async def cog_load(self) -> None:
        await self._bot.wait_until_first_connect()
        await self.setup_book()

    @commands.slash_command(name="play")
    async def _play(self, inter: disnake.AppCmdInter) -> None:
        tracks = await Playable.search("Knight", source=TrackSource.Spotify)
        player = await Player.connect_to_channel(inter.author.voice.channel)

        await player.queue.put_wait(tracks[1:])
        if not hasattr(player.namespace, "home"):
            player.add_to_namespace({"home": inter.channel})

        await player.play(tracks[0])
        await inter.response.send_message(f"Added {tracks[0].title}")

    # For more information check wavelink.


bot = commands.Bot(command_prefix="+", intents=Intents.all())
bot.add_cog(MusicCog(bot))

bot.run()
