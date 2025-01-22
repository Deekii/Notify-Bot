from discord.ext import commands, tasks
import discord
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

# Add after imports
def create_embed(title, description):
    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.red()
    )
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar.url if bot.user.avatar else None)
    embed.set_footer(text="Bot by Deki")
    return embed

# Global settings for the bot
settings = {
    "welcome_channel": None,
    "welcome_role": None,
    "audit_log_channel": None,
    "youtube_channel": None,
    "tiktok_channel": None
}

# Ensure commands are restricted to administrators
def admin_only(ctx):
    return ctx.author.guild_permissions.administrator

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    
    # Start background tasks
    youtube_notifications.start()
    tiktok_notifications.start()

# Event: Member joins the server
@bot.event
async def on_member_join(member):
    if settings["welcome_channel"]:
        channel = bot.get_channel(settings["welcome_channel"])
        if channel:
            await channel.send(f"Welcome {member.mention} to the server!")
    if settings["welcome_role"]:
        role = member.guild.get_role(settings["welcome_role"])
        if role:
            await member.add_roles(role)

# Event: Audit log tracker
@bot.event
async def on_guild_channel_create(channel):
    if settings["audit_log_channel"]:
        log_channel = bot.get_channel(settings["audit_log_channel"])
        embed = discord.Embed(
            title="Channel Created",
            description=f"A new channel was created: {channel.name}",
            color=discord.Color.green()
        )
        await log_channel.send(embed=embed)

# Command: Setup welcome channel
@bot.command(name='setupwelcomer')
@commands.check(admin_only)
async def setup_welcomer(ctx, channel: discord.TextChannel):
    settings["welcome_channel"] = channel.id
    await ctx.send(f"Welcome channel set to {channel.mention}")

# Command: Setup welcome role
@bot.command(name='setupwelcomerole')
@commands.check(admin_only)
async def setup_welcome_role(ctx, role: discord.Role):
    settings["welcome_role"] = role.id
    await ctx.send(f"Welcome role set to {role.name}")

# Command: Setup audit log channel
@bot.command(name='setupauditlog')
@commands.check(admin_only)
async def setup_audit_log(ctx, channel: discord.TextChannel):
    settings["audit_log_channel"] = channel.id
    await ctx.send(f"Audit log channel set to {channel.mention}")

# Command: Kick user
@bot.command(name='kick')
@commands.check(admin_only)
async def kick_user(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"{member} has been kicked. Reason: {reason}")

# Command: Ban user
@bot.command(name='ban')
@commands.check(admin_only)
async def ban_user(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"{member} has been banned. Reason: {reason}")

# Command: Setup YouTube notifications
@bot.command(name='setupyoutube')
@commands.check(admin_only)
async def setup_youtube(ctx, channel_url: str):
    settings["youtube_channel"] = channel_url
    await ctx.send(f"YouTube channel set to {channel_url}")

# Command: Setup TikTok notifications
@bot.command(name='setuptiktok')
@commands.check(admin_only)
async def setup_tiktok(ctx, username: str):
    settings["tiktok_channel"] = username
    await ctx.send(f"TikTok channel set to {username}")

# Task: Notify YouTube uploads
@tasks.loop(minutes=5)
async def youtube_notifications():
    if settings["youtube_channel"] and settings["welcome_channel"]:
        channel = bot.get_channel(settings["welcome_channel"])
        await channel.send(f"New YouTube video uploaded! Check it out: {settings['youtube_channel']}")

# Task: Notify TikTok uploads
@tasks.loop(minutes=5)
async def tiktok_notifications():
    if settings["tiktok_channel"] and settings["welcome_channel"]:
        channel = bot.get_channel(settings["welcome_channel"])
        await channel.send(f"New TikTok video from {settings['tiktok_channel']}!")

# Run the bot
if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN'))
