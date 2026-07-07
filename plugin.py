import discord
from discord.channel import TextChannel
from discord.ext import commands
from discord.commands import SlashCommandGroup

from resources.shared import CONTEXTS, INTEGRATION_TYPES
from scripts.tools import journal

from .config import LOG_COMPONENT
from .database import JoinLeaveLogDatabase

database = JoinLeaveLogDatabase()


class JoinLeaveLogView(discord.ui.DesignerView):
	def __init__(self, member: discord.Member, joined: bool):
		super().__init__(timeout=None)

		container = discord.ui.Container(colour=discord.Colour.green() if joined else discord.Colour.red())
		super().add_item(container)

		title_text = discord.ui.TextDisplay(f"### Member {'Joined' if joined else 'Left'}")
		container.add_item(title_text)

		body_text = discord.ui.TextDisplay(f"Member {member.mention} ({member.name}) {'joined' if joined else 'left'}")
		container.add_item(body_text)


class JoinLeaveLog(commands.Cog):
	command_group = SlashCommandGroup("joinleavelog", "Join/leave log", contexts=CONTEXTS, integration_types=INTEGRATION_TYPES)

	def __init__(self, bot: discord.Bot):
		self.bot = bot

	@command_group.command(name="set_channel", description="Set what channel join/leave log messages should be sent in for this server", contexts=CONTEXTS, integration_types=INTEGRATION_TYPES)
	@commands.has_permissions(administrator=True)
	async def set_channel(self, ctx, channel: TextChannel):
		database.set_channel(ctx.guild_id, channel.id)

		await ctx.respond(f"Set the join/leave log channel to {channel.jump_url}")

	@command_group.command(name="remove_channel", description="Removes the join/leave log channel for this server.", contexts=CONTEXTS, integration_types=INTEGRATION_TYPES)
	@commands.has_permissions(administrator=True)
	async def remove_channel(self, ctx):
		database.remove_channel(ctx.guild_id)

		await ctx.respond("Join/leave log channel removed")

	@commands.Cog.listener()
	async def on_member_join(self, member: discord.Member):
		await self.send_join_leave_message(member, True)

	@commands.Cog.listener()
	async def on_member_remove(self, member: discord.Member):
		await self.send_join_leave_message(member, False)

	async def send_join_leave_message(self, member: discord.Member, joined: bool):
		guild_id = member.guild.id
		forward_channel_id = database.get_channel(guild_id)

		if forward_channel_id:
			server = self.bot.get_guild(guild_id)

			forward_channel = server.get_channel(forward_channel_id)
			if forward_channel is None:
				journal.log(f"Couldn't find channel {forward_channel_id} in cache, fetching from Discord", 7, component=LOG_COMPONENT)
				forward_channel = await server.fetch_channel(forward_channel_id)

			await forward_channel.send(view=JoinLeaveLogView(member, joined), allowed_mentions=discord.AllowedMentions(users=False, roles=False))


def setup(bot):
	bot.add_cog(JoinLeaveLog(bot))


def teardown(bot):
	bot.remove_cog("JoinLeaveLog")
