import json
import locale
import platform
import random
import sys
import time
from datetime import datetime, timedelta

import discord
import psutil
from discord.ext.commands import has_permissions, MissingPermissions, Bot, CommandInvokeError
from youtube_dl import YoutubeDL
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from discord.utils import get
from discord import FFmpegPCMAudio
import asyncio

user = []
musictitle = []
song_queue = []
musicnow = []

with open('../bot/config.json', encoding='UTF8') as json_file:
    json_data = json.load(json_file)

token = json_data["token"]
prefix = json_data["prefix"]
botver = json_data["version"]
wc = json_data["welcome_channel_name"]
bc = json_data["bye_channel_name"]
ownerid = json_data["owner_id"]
botname = json_data["bot_name"]
nc = json_data["notice_channel_name"]
lac = json_data["local_announcement_channel_name"]
gac = json_data["global_announcement_channel_name"]
clg = json_data["chat_log"]
client = Bot(command_prefix=prefix, intents=discord.Intents.all())
rp = discord.Activity(type=discord.ActivityType.listening, name=f"수달은 노래")

locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')


# 권한 부족할 경우 호출될 embed
# mper = None
# mp = discord.Embed(title="권한 부족 이벤트 발생!", color=0xfc7f03)
# mp.add_field(name="자세한 내용", value=f"당신은 `{mper}` 권한이 없어 해당 명령어 사용이 거부되었습니다. 자세한 내용은 관리자에게 문의해주세요.", inline=False)
# mp.set_footer(text="BY - Kill00#1100")


@client.event
# 봇 시작시 실행하는 스크립트
async def on_ready():
    print('------')
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print(str(len(client.guilds)) + " 개의 서버에서 봇이 동작중입니다.")
    print('------')
    print("Python Version :", sys.version, "|Recommend : 3.6.8|")
    print("Discord.py Version :", discord.__version__, "|Recommend : 1.4.1|")
    print(f"[{botname}] Bot Version :", botver)
    print('------')
    print('welcome channel name :', wc)
    print('bye channel name :', bc)
    print('notice channel name :', nc)
    print('local announcement channel name :', lac)
    print('global announcement channel name :', gac)
    print('chat log channel name :', clg)
    print('------')
    await client.change_presence(status=discord.Status.online, activity=rp)


# 명령어 'serverlist' [시작]
@client.command()
@has_permissions(administrator=True)
async def serverlist(ctx):
    get_msg1 = str(len(client.guilds)) + " 개의 서버에서 동작중입니다. \n\n `자세히 보기` :\n```" + str(client.guilds) + "```"
    await ctx.send(get_msg1)


@serverlist.error
async def serverlist_error(ctx, error):
    if isinstance(error, MissingPermissions):
        mper = "ADMINISTRATOR"
        mp = discord.Embed(title="권한 부족 이벤트 발생!", timestamp=datetime.utcnow(), color=0xfc7f03)
        mp.add_field(name="자세한 내용", value=f"당신은 `{mper}` 권한이 없어 해당 명령어 사용이 거부되었습니다. 자세한 내용은 관리자에게 문의해주세요.",
                     inline=True)
        mp.set_footer(text="BY - Kill00#1100")
        await ctx.send(ctx.message.author.mention, embed=mp)


# 명령어 'serverlist' [끝]

# 명령어 'ban' [시작]
@client.command()
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member = None, *, reason=None):
    if reason is None:
        reason = "관리자에게 문의하세요."
    # 서버내 설정된 채널 찿기
    channel = discord.utils.get(member.guild.text_channels, name=f"{nc}")
    if channel is None:
        channel = await member.guild.create_text_channel(f"{nc}")
        await channel.send("해당 채널이 없어 자동으로 생성되었습니다.")

    # reason 사유로 밴
    await member.ban(reason=reason)

    # 해당 서버에서 embed 출력
    bannedembed = discord.Embed(title="밴 이벤트 발생!", description=f"{member} [ID : {member.id}] 님이 영구밴 되었습니다.",
                                color=0xff0000)
    bannedembed.add_field(name="처리자", value=f"{ctx.message.author} {ctx.message.author.mention}", inline=False)
    bannedembed.add_field(name="사유", value=f"{reason}", inline=False)
    bannedembed.set_footer(text="BY - Kill00#1100")
    await ctx.send(embed=bannedembed)

    # 처벌기록에 embed 출력
    await channel.send(embed=bannedembed)

    # 밴 당한 유저의 DM 으로 embed 출력
    banusersend = discord.Embed(title="밴 이벤트 발생!", description=f"당신은 {ctx.guild.name}에서 영구밴 당했습니다.",
                                color=0xff0000)
    banusersend.add_field(name="처리자", value=f"{ctx.message.author} {ctx.message.author.mention}", inline=False)
    banusersend.add_field(name="사유", value=f"{reason}", inline=False)
    banusersend.set_footer(text="BY - Kill00#1100")
    await member.send(embed=banusersend)


@ban.error
async def ban_error(ctx, error):
    if isinstance(error, MissingPermissions):
        mper = "BAN_MEMBERS"
        mp = discord.Embed(title="권한 부족 이벤트 발생!", timestamp=datetime.utcnow(), color=0xfc7f03)
        mp.add_field(name="자세한 내용", value=f"당신은 `{mper}` 권한이 없어 해당 명령어 사용이 거부되었습니다. 자세한 내용은 관리자에게 문의해주세요.",
                     inline=True)
        mp.set_footer(text="BY - Kill00#1100")
        await ctx.send(ctx.message.author.mention, embed=mp)
    else:
        if isinstance(error, CommandInvokeError):
            await ctx.send(f"{ctx.message.author.mention}님, 해당 유저는 DM Lock 상태입니다. DM 전송을 스킵하였습니다.")
        else:
            errorembed = discord.Embed(title="밴 에러 발생!", description=f"심각한 에러가 발생하였습니다 #404",
                                       color=0xff0000)
            errorembed.add_field(name="자세한 내용",
                                 value=f"밴 할 유저가 없습니다. '서버에 참가한 유저중 멘션/ID'을(를) 다시 입력해주세요. 혹은 이미 밴된 유저일수도 있습니다.",
                                 inline=False)
            errorembed.set_footer(text="BY - Kill00#1100")
            await ctx.send(embed=errorembed)
            print(error)
            await client.on_command_error(ctx, error)


# 명령어 'ban' [끝]

# 명령어 'unban' [시작]
@client.command()
@has_permissions(ban_members=True)
async def unban(ctx, member_id):
    # 언밴 명령어
    user = await client.fetch_user(member_id)
    await ctx.guild.unban(user)

    # 서버내 설정된 채널 찿기
    channel = discord.utils.get(ctx.guild.text_channels, name=f"{nc}")
    if channel is None:
        channel = await ctx.guild.create_text_channel(f"{nc}")
        await channel.send("해당 채널이 없어 자동으로 생성되었습니다.")

    # 해당 서버에서 embed 출력
    unbanembed = discord.Embed(title="언밴 이벤트 발생!", description=f"{user} [ID : {member_id}] 님이 언밴 되었습니다.",
                               color=0x00ff00)
    unbanembed.add_field(name="처리자", value=f"{ctx.message.author} {ctx.message.author.mention}", inline=False)
    unbanembed.set_footer(text="BY - Kill00#1100")
    await ctx.send(embed=unbanembed)

    # 처벌기록에 embed 출력
    await channel.send(embed=unbanembed)


@unban.error
async def unban_error(ctx, error):
    if isinstance(error, MissingPermissions):
        mper = "BAN_MEMBERS"
        mp = discord.Embed(title="권한 부족 이벤트 발생!", timestamp=datetime.utcnow(), color=0xfc7f03)
        mp.add_field(name="자세한 내용", value=f"당신은 `{mper}` 권한이 없어 해당 명령어 사용이 거부되었습니다. 자세한 내용은 관리자에게 문의해주세요.",
                     inline=True)
        mp.set_footer(text="BY - Kill00#1100")
        await ctx.send(ctx.message.author.mention, embed=mp)
    else:

        errorembed = discord.Embed(title="언밴 에러 발생!", description=f"심각한 에러가 발생하였습니다 #404",
                                   color=0xff0000)
        errorembed.add_field(name="자세한 내용",
                             value=f"언밴 할 유저가 없습니다. '밴된 유저 ID'을(를) 다시 입력해주세요. 혹은 이미 언밴된 유저일수도 있습니다.",
                             inline=False)
        errorembed.set_footer(text="BY - Kill00#1100")
        await ctx.send(embed=errorembed)
        print(error)
        await client.on_command_error(ctx, error)


# 명령어 'unban' [끝]

# 명령어 'hackban' [시작]
@client.command()
@has_permissions(ban_members=True)
async def hackban(ctx, member_id, *, reason=None):
    user = await client.fetch_user(member_id)
    if reason is None:
        reason = "관리자에게 문의하세요."
    # 서버내 설정된 채널 찿기
    channel = discord.utils.get(ctx.guild.text_channels, name=f"{nc}")
    if channel is None:
        channel = await ctx.guild.create_text_channel(f"{nc}")
        await channel.send("해당 채널이 없어 자동으로 생성되었습니다.")

    # reason 사유로 밴
    await ctx.guild.ban(discord.Object(id=member_id))

    # 해당 서버에서 embed 출력
    bannedembed = discord.Embed(title="밴 이벤트 발생!", description=f"{user} [ID : {user.id}] 님이 영구밴 되었습니다. (hackban)",
                                color=0xff0000)
    bannedembed.add_field(name="처리자", value=f"{ctx.message.author} {ctx.message.author.mention}", inline=False)
    bannedembed.add_field(name="사유", value=f"{reason}", inline=False)
    bannedembed.set_footer(text="BY - Kill00#1100")
    await ctx.send(embed=bannedembed)

    # 처벌기록에 embed 출력
    await channel.send(embed=bannedembed)


@hackban.error
async def hackban_error(ctx, error):
    if isinstance(error, MissingPermissions):
        mper = "BAN_MEMBERS"
        mp = discord.Embed(title="권한 부족 이벤트 발생!", timestamp=datetime.utcnow(), color=0xfc7f03)
        mp.add_field(name="자세한 내용", value=f"당신은 `{mper}` 권한이 없어 해당 명령어 사용이 거부되었습니다. 자세한 내용은 관리자에게 문의해주세요.",
                     inline=True)
        mp.set_footer(text="BY - Kill00#1100")
        await ctx.send(ctx.message.author.mention, embed=mp)
    else:
        errorembed = discord.Embed(title="밴 에러 발생!", description=f"심각한 에러가 발생하였습니다 #404",
                                   color=0xff0000)
        errorembed.add_field(name="자세한 내용",
                             value=f"밴 할 유저가 없습니다. '유저 ID'을(를) 다시 입력해주세요. 혹은 이미 밴된 유저일수도 있습니다.",
                             inline=False)
        errorembed.set_footer(text="BY - Kill00#1100")
        await ctx.send(embed=errorembed)
        print(error)
        await client.on_command_error(ctx, error)


# 명령어 'hackban' [끝]

# 명령어 'kick' [시작]
@client.command()
@has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member = None, *, reason=None):
    if reason is None:
        reason = "관리자에게 문의하세요."
    # 서버내 설정된 채널 찿기
    channel = discord.utils.get(member.guild.text_channels, name=f"{nc}")
    if channel is None:
        channel = await member.guild.create_text_channel(f"{nc}")
        await channel.send("해당 채널이 없어 자동으로 생성되었습니다.")

    # reason 사유로 추방
    await member.kick(reason=reason)

    # 해당 서버에서 embed 출력
    kickedembed = discord.Embed(title="추방 이벤트 발생!", description=f"{member} [ID : {member.id}] 님이 추방처리 되었습니다.",
                                color=0xff0000)
    kickedembed.add_field(name="처리자", value=f"{ctx.message.author} {ctx.message.author.mention}", inline=False)
    kickedembed.add_field(name="사유", value=f"{reason}", inline=False)
    kickedembed.set_footer(text="BY - Kill00#1100")
    await ctx.send(embed=kickedembed)

    # 처벌기록에 embed 출력
    await channel.send(embed=kickedembed)

    # 추방 당한 유저의 DM 으로 embed 출력
    kickusersend = discord.Embed(title="추방 이벤트 발생!", description=f"당신은 {ctx.guild.name}에서 추방 당했습니다.",
                                 color=0xff0000)
    kickusersend.add_field(name="처리자", value=f"{ctx.message.author} {ctx.message.author.mention}", inline=False)
    kickusersend.add_field(name="사유", value=f"{reason}", inline=False)
    kickusersend.set_footer(text="BY - Kill00#1100")
    await member.send(embed=kickusersend)


@kick.error
async def kick_error(ctx, error):
    if isinstance(error, MissingPermissions):
        mper = "KICK_MEMBERS"
        mp = discord.Embed(title="권한 부족 이벤트 발생!", timestamp=datetime.utcnow(), color=0xfc7f03)
        mp.add_field(name="자세한 내용", value=f"당신은 `{mper}` 권한이 없어 해당 명령어 사용이 거부되었습니다. 자세한 내용은 관리자에게 문의해주세요.",
                     inline=True)
        mp.set_footer(text="BY - Kill00#1100")
        await ctx.send(ctx.message.author.mention, embed=mp)
    else:
        if isinstance(error, CommandInvokeError):
            await ctx.send(f"{ctx.message.author.mention}님, 해당 유저는 DM Lock 상태입니다. DM 전송을 스킵하였습니다.")
        else:
            errorembed = discord.Embed(title="추방 에러 발생!", description=f"심각한 에러가 발생하였습니다 #404",
                                       color=0xff0000)
            errorembed.add_field(name="자세한 내용",
                                 value=f"추방 할 유저가 없습니다. '서버에 참가한 유저중 멘션/ID'을(를) 다시 입력해주세요."
                                       f" 혹은 이미 추방 당했거나 밴된 유저일수도 있습니다.", inline=False)
            errorembed.set_footer(text="BY - Kill00#1100")
            await ctx.send(embed=errorembed)
            print(error)
            await client.on_command_error(ctx, error)


# 명령어 'kick' [끝]

# 명령어 'leave' [시작]

@client.command()
async def leave(ctx, *, reason=None):
    if reason is None:
        reason = "자세한 내용은 봇 관리자에게 문의 해주세요."

    mp = discord.Embed(title="권한 부족 이벤트 발생!", color=0xfc7f03)
    mp.add_field(name="자세한 내용", value=f"당신은 `{ownerid}` 권한이 없어 해당 명령어 사용이 거부되었습니다. 자세한 내용은 관리자에게 문의해주세요.",
                 inline=True)
    mp.set_footer(text="BY - Kill00#1100")
    if ctx.message.author.id != ownerid:
        await ctx.send(embed=mp)
    else:
        # 해당 서버에서 embed 출력
        leaveembed = discord.Embed(title="봇 퇴장안내", description=f"`{botname}` 봇이 퇴장하였습니다.",
                                   color=0xff0000)
        leaveembed.add_field(name="처리자", value=f"{ctx.message.author} {ctx.message.author.mention}", inline=False)
        leaveembed.add_field(name="사유", value=f"{reason}", inline=False)
        leaveembed.set_footer(text="BY - Kill00#1100")
        await ctx.send(embed=leaveembed)
        await ctx.guild.leave()


@leave.error
async def leave_error(ctx, error):
    print(error)
    await client.on_command_error(ctx, error)


# 명령어 'leave' [끝]

# 명령어 'shutdown' [시작]

@client.command()
async def shutdown(ctx):
    mp = discord.Embed(title="권한 부족 이벤트 발생!", color=0xfc7f03)
    mp.add_field(name="자세한 내용", value=f"당신은 `{ownerid}` 권한이 없어 해당 명령어 사용이 거부되었습니다. 자세한 내용은 관리자에게 문의해주세요.",
                 inline=True)
    mp.set_footer(text="BY - Kill00#1100")
    if ctx.message.author.id != ownerid:
        await ctx.send(embed=mp)
    else:
        before = time.monotonic()
        sd = await ctx.send(":arrows_counterclockwise: 종료 준비중...")
        ping = (time.monotonic() - before) * 1000
        # 해당 서버에서 embed 출력
        shutdownembed = discord.Embed(title=":white_check_mark: 봇이 종료되었습니다", description=f"`{botname}` 봇을 성공적으로"
                                                                                         f" 종료하였습니다.", color=0x00ff00)
        shutdownembed.add_field(name="처리자", value=f"{ctx.message.author} {ctx.message.author.mention}", inline=False)
        shutdownembed.add_field(name="자세한 정보", value=f"**작동 환경 : {platform.platform()} {platform.machine()}"
                                                     f"\n현재 CPU 사용량 : {psutil.cpu_percent()}%"
                                                     f"\n현재 램 사용량 : {psutil.virtual_memory().percent}% (_Null_MB)"
                                                     f"\n업타임 : NotSupport"
                                                     f"\n핑"
                                                     f"\n:table_tennis: 퐁!"
                                                     f"\n{client.latency}ms, _Null_ms, {int(ping)}ms, "
                                                     f"{round(client.latency, 1)}ms**")
        shutdownembed.set_footer(text="BY - Kill00#1100")
        await sd.edit(content="", embed=shutdownembed)
        await client.logout()


@shutdown.error
async def shutdown_error(ctx, error):
    print(error)
    await client.on_command_error(ctx, error)


# 명령어 'shutdown' [끝]

# 명령어 'cc' [시작]

@client.command()
@has_permissions(manage_messages=True)
async def cc(ctx, limit: int):
    await ctx.channel.purge(limit=limit + 1)
    localcc = discord.Embed(title="정보", description=f"{limit + 1}개의 채팅이 삭제되었습니다", timestamp=datetime.utcnow(),
                            color=0x00ff00)
    await ctx.send(ctx.message.author.mention, embed=localcc)


@cc.error
async def cc_error(ctx, error):
    if isinstance(error, MissingPermissions):
        mper = "MANAGE_MESSAGES"
        mp = discord.Embed(title="권한 부족 이벤트 발생!", timestamp=datetime.utcnow(), color=0xfc7f03)
        mp.add_field(name="자세한 내용", value=f"당신은 `{mper}` 권한이 없어 해당 명령어 사용이 거부되었습니다. 자세한 내용은 관리자에게 문의해주세요.",
                     inline=True)
        mp.set_footer(text="BY - Kill00#1100")
        await ctx.send(ctx.message.author.mention, embed=mp)
    else:
        print(error)
        await client.on_command_error(ctx, error)


# 명령어 'cc' [끝]

# 명령어 '공지' [시작]

@client.command()
@has_permissions(manage_channels=True)
async def 공지(ctx, *args):
    # 서버내 설정된 채널 찿기
    channel = discord.utils.get(ctx.guild.text_channels, name=f"{lac}")
    if channel is None:
        channel = await ctx.guild.create_text_channel(f"{lac}")
        await channel.send("해당 채널이 없어 자동으로 생성되었습니다.")

    # Embed 호출
    localaceb = discord.Embed(timestamp=datetime.utcnow(), color=0x00ff00)
    localaceb.set_author(name="공지사항", icon_url=ctx.guild.icon_url)
    localaceb.add_field(name="공지 내용", value=f"{' '.join(args)}")
    localaceb.set_footer(text=f"작성자 : {ctx.message.author}" + f" [BY - Kill00#1100, {botname}]",
                         icon_url=ctx.message.author.avatar_url)
    await ctx.message.delete()
    await channel.send(content="@everyone", embed=localaceb)


@공지.error
async def 공지_error(ctx, error):
    if isinstance(error, MissingPermissions):
        mper = "MANAGE_CHANNELS"
        mp = discord.Embed(title="권한 부족 이벤트 발생!", timestamp=datetime.utcnow(), color=0xfc7f03)
        mp.add_field(name="자세한 내용", value=f"당신은 `{mper}` 권한이 없어 해당 명령어 사용이 거부되었습니다. 자세한 내용은 관리자에게 문의해주세요.",
                     inline=True)
        mp.set_footer(text="BY - Kill00#1100")
        await ctx.send(ctx.message.author.mention, embed=mp)
    else:
        print(error)
        await client.on_command_error(ctx, error)


# 명령어 '공지' [끝]

# 명령어 'getinvite' [시작]
@client.command()
async def getinvite(ctx, args):
    mp = discord.Embed(title="권한 부족 이벤트 발생!", color=0xfc7f03)
    mp.add_field(name="자세한 내용", value=f"당신은 `{ownerid}` 권한이 없어 해당 명령어 사용이 거부되었습니다. 자세한 내용은 관리자에게 문의해주세요.",
                 inline=True)
    mp.set_footer(text="BY - Kill00#1100")
    if ctx.message.author.id != ownerid:
        await ctx.send(embed=mp)
    else:
        guild = client.get_guild(int(args))
        getrandomchannel = random.choice(guild.text_channels)
        invite = await getrandomchannel.create_invite(max_age=0, max_uses=1, unique=True)
        inv = discord.Embed(title="정보", description=f"{invite}", timestamp=datetime.utcnow(),
                            color=0x00ff00)
        await ctx.message.delete()
        await ctx.author.send(embed=inv)


@getinvite.error
async def getinvite_error(ctx, error):
    if isinstance(error, CommandInvokeError):
        await ctx.send(f"{ctx.message.author.mention}님, DM Lock 상태입니다. 해제후 다시 시도해주세요.")
    else:
        await ctx.send(f"{ctx.message.author.mention}, {error}")
        await client.on_command_error(ctx, error)


# 명령어 'getinvite' [끝]

# 입장 [시작]

@client.event
async def on_member_join(member):
    # 서버내 설정된 채널 찿기
    channel = discord.utils.get(member.guild.text_channels, name=f"{wc}")
    if channel is None:
        channel = await member.guild.create_text_channel(f"{wc}")
        await channel.send("해당 채널이 없어 자동으로 생성되었습니다.")

    # Embed 호출
    welcomech = discord.Embed(title=f"ID : {member.id}",
                              description=f"{member.display_name} | {member} | {member.mention}님이 ['{member.guild.name}"
                                          f"'] 에 입장하셨습니다!", timestamp=datetime.utcnow(), color=0x00ff00)
    welcomech.set_author(name=f"{member} 님이 서버에서 입장하셨습니다!", icon_url=member.avatar_url_as(static_format="png"))
    welcomech.add_field(name="자세한 정보",
                        value=f"계정을 가입한 시간 : "
                              f"`{(member.created_at + timedelta(hours=9)).strftime('%Y년 %m월 %d일 %A %p %I시 %M분 %S초')}`"

                              f"\n서버에 가입한 시간 : "
                              f"`{(member.joined_at + timedelta(hours=9)).strftime('%Y년 %m월 %d일 %A %p %I시 %M분 %S초')}`",
                        inline=False)
    welcomech.set_footer(text="서버 인원 : " + str(channel.guild.member_count) + f"명 [BY - Kill00#1100, {botname}]")
    await channel.send(embed=welcomech)


# 입장 [끝]

# 퇴장 [시작]

@client.event
async def on_member_remove(member):
    # 서버내 설정된 채널 찿기
    channel = discord.utils.get(member.guild.text_channels, name=f"{bc}")
    if channel is None:
        channel = await member.guild.create_text_channel(f"{bc}")
        await channel.send("해당 채널이 없어 자동으로 생성되었습니다.")

    # Embed 호출
    byech = discord.Embed(title=f"ID : {member.id}",
                          description=f"{member.display_name} | {member} | {member.mention}님이 ['{member.guild.name}'] "
                                      f"에서 퇴장하셨습니다!", timestamp=datetime.utcnow(), color=0xff0000)
    byech.set_author(name=f"{member} 님이 서버에서 퇴장하셨습니다!", icon_url=member.avatar_url_as(static_format="png"))
    byech.add_field(name="자세한 정보",
                    value=f"계정을 가입한 시간 : "
                          f"`{(member.created_at + timedelta(hours=9)).strftime('%Y년 %m월 %d일 %A %p %I시 %M분 %S초')}`"

                          f"\n서버에 가입한 시간 : "
                          f"`{(member.joined_at + timedelta(hours=9)).strftime('%Y년 %m월 %d일 %A %p %I시 %M분 %S초')}`"

                          f"\n서버를 떠난 시각 : `" + datetime.now().strftime("%Y년 %m월 %d일 %A %p %I시 %M분 %S초") + "`",
                    inline=False)
    byech.set_footer(text="서버 인원 : " + str(channel.guild.member_count) + f"명 [BY - Kill00#1100, {botname}]")
    await channel.send(embed=byech)


# 퇴장 [끝]

def title(msg):
    global music

    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    options = webdriver.ChromeOptions()
    options.add_argument("headless")

    chromedriver_dir = r"D:\Discord_Bot\chromedriver.exe"
    driver = webdriver.Chrome(chromedriver_dir, options = options)
    driver.get("https://www.youtube.com/results?search_query="+msg+"+lyrics")
    source = driver.page_source
    bs = bs4.BeautifulSoup(source, 'lxml')
    entire = bs.find_all('a', {'id': 'video-title'})
    entireNum = entire[0]
    music = entireNum.text.strip()
    
    musictitle.append(music)
    musicnow.append(music)
    test1 = entireNum.get('href')
    url = 'https://www.youtube.com'+test1
    with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
    URL = info['formats'][0]['url']

    driver.quit()
    
    return music, URL

def play(ctx):
    global vc
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    URL = song_queue[0]
    del user[0]
    del musictitle[0]
    del song_queue[0]
    vc = get(client.voice_clients, guild=ctx.guild)
    if not vc.is_playing():
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: play_next(ctx)) 

def play_next(ctx):
    if len(musicnow) - len(user) >= 2:
        for i in range(len(musicnow) - len(user) - 1):
            del musicnow[0]
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    if len(user) >= 1:
        if not vc.is_playing():
            del musicnow[0]
            URL = song_queue[0]
            del user[0]
            del musictitle[0]
            del song_queue[0]
            vc.play(discord.FFmpegPCMAudio(URL,**FFMPEG_OPTIONS), after=lambda e: play_next(ctx))

@client.command()
async def 노래(ctx, text):
    if text == "들려줘":
        try:
            global vc
            vc = await ctx.message.author.voice.channel.connect()
            await ctx.send("무슨 노래 들려줄까?")
        except:
            try:
                await vc.move_to(ctx.message.author.voice.channel)
            except:
                await ctx.send("채널에 너가 없는데..?")
    elif text == "그만":
        try:
            await vc.disconnect()
            await ctx.send("다음에 또 들려줄게")
        except:
            await ctx.send("난 이미 그 채널에 없어..!")

@client.command()
async def URL재생(ctx, *, url):

    try:
        global vc
        vc = await ctx.message.author. voice.channel.connect()
    except:
        try:
            await vc.move_to(ctx.message.author.voice.channel)
        except:
            await ctx.send("채널에 너가 없는데..?")
            
    YDL_OPTIONS = {'format':'bestaudio','noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    if not vc.is_playing():
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        await ctx.send(embed = discord.Embed(title= "노래 재생", description = "지금은 " + url + "을(를) 재생하고 있어.", color = 0x00ff00))
    else:
        await ctx.send("노래가 이미 재생되고 있어!")

@client.command()
async def 재생(ctx, *, msg):

    try:
        global vc
        vc = await ctx.message.author. voice.channel.connect()
    except:
        try:
            await vc.move_to(ctx.message.author.voice.channel)
        except:
            await ctx.send("채널에 너가 없는데..?")

    if not vc.is_playing():

        options = webdriver.ChromeOptions()
        options.add_argument("headless")

        global entireText
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            
        chromedriver_dir = "/home/sudal/chromedriver"
        driver = webdriver.Chrome(chromedriver_dir, options = options)
        driver.get("https://www.youtube.com/results?search_query="+msg+"+lyrics")
        source = driver.page_source
        bs = bs4.BeautifulSoup(source, 'lxml')
        entire = bs.find_all('a', {'id': 'video-title'})
        entireNum = entire[0]
        entireText = entireNum.text.strip()
        musicurl = entireNum.get('href')
        url = 'https://www.youtube.com'+musicurl 

        driver.quit()

        musicnow.insert(0, entireText)
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        await ctx.send(embed = discord.Embed(title= "노래 재생", description = "지금은 " + musicnow[0] + "을(를) 재생하고 있어.", color = 0x00ff00))
        vc.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after = lambda e: play_next(ctx))
    else:
        await ctx.send("이미 노래가 재생 중이야!")

@client.command()
async def 리스트추가(ctx, *, msg):
    user.append(msg)
    result, URLTEST = title(msg)
    song_queue.append(URLTEST)
    await ctx.send(result + "을(를) 재생목록에 추가했어!")

@client.command()
async def 리스트삭제(ctx, *, number):
    try:
        ex = len(musicnow) - len(user)
        del user[int(number) - 1]
        del musictitle[int(number) - 1]
        del song_queue[int(number)-1]
        del musicnow[int(number)-1+ex]
            
        await ctx.send("대기열이 삭제되었어!")
    except:
        if len(list) == 0:
            await ctx.send("대기열에 노래가 없어!")
        else:
            if len(list) < int(number):
                await ctx.send("숫자의 범위가 목록개수를 벗어났어!")
            else:
                await ctx.send("숫자를 입력해!")

@client.command()
async def 리스트(ctx, text):
    if text == "목록":
        if len(musictitle) == 0:
            await ctx.send("아직 아무노래도 등록하지 않았어..ㅠ")
        else:
            global Text
            Text = ""
            for i in range(len(musictitle)):
                Text = Text + "\n" + str(i + 1) + ". " + str(musictitle[i])

            await ctx.send(embed = discord.Embed(title= "리스트", description = Text.strip(), color = 0x00ff00))

    elif text == "초기화":
        try:
            ex = len(musicnow) - len(user)
            del user[:]
            del musictitle[:]
            del song_queue[:]
            while True:
                try:
                    del musicnow[ex]
                except:
                    break
            await ctx.send(embed = discord.Embed(title= "리스트초기화", description = """리스트가 정상적으로 초기화되었어!""", color = 0x00ff00))
        except:
            await ctx.send("아직 아무노래도 등록하지 않았어..ㅠ")

    elif text == "재생":
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        if len(user) == 0:
            await ctx.send("아직 아무노래도 등록하지 않았어..ㅠ")
        else:
            if len(musicnow) - len(user) >= 1:
                for i in range(len(musicnow) - len(user)):
                    del musicnow[0]
            if not vc.is_playing():
                play(ctx)
            else:
                await ctx.send("노래가 이미 재생되고 있어!")

@client.command()
async def 일시정지(ctx):
    if vc.is_playing():
        vc.pause()
        await ctx.send(embed = discord.Embed(title= "일시정지", description = musicnow[0] + "을(를) 일시정지 했어!", color = 0x00ff00))
    else:
        await ctx.send("지금은 노래가 재생되지 않고 있어!")

@client.command()
async def 다시재생(ctx):
    try:
        vc.resume()
    except:
        await ctx.send("지금은 노래가 재생되지 않고 있어!")
    else:
        await ctx.send(embed = discord.Embed(title= "다시재생", description = musicnow[0]  + "을(를) 다시 재생했어!", color = 0x00ff00))

@client.command()
async def 노래끄기(ctx):
    if vc.is_playing():
        vc.stop()
        await ctx.send(embed = discord.Embed(title= "노래끄기", description = musicnow[0]  + "을(를) 종료할게!", color = 0x00ff00))
    else:
        await ctx.send("지금은 노래가 재생되지 않고 있어!")

@client.command()
async def 명령어(ctx):
    await ctx.send(embed = discord.Embed(title='도움말',description="""
\n!도움말 -> 노래봇의 모든 명령어를 볼 수 있습니다.
\n!노래 들려줘 -> 노래봇을 자신이 속한 음성채널로 부릅니다.
\n!노래 그만 -> 노래봇을 자신이 속한 음성채널에서 내보냅니다.
\n!URL재생 [노래링크] -> 유튜브URL를 입력하면 뮤직봇이 노래를 틀어줍니다.
(리스트재생에서는 사용할 수 없습니다.)
\n!재생 [노래이름] -> 노래봇이 노래를 검색해 틀어줍니다.
\n!노래끄기 -> 현재 재생중인 노래를 끕니다.
!일시정지 -> 현재 재생중인 노래를 일시정지시킵니다.
!다시재생 -> 일시정지시킨 노래를 다시 재생합니다.
\n!리스트 목록-> 이어서 재생할 노래목록을 보여줍니다.
!리스트 재생 -> 리스트에 추가된 노래를 재생합니다.
!리스트 초기화 -> 리스트에 추가된 모든 노래를 지웁니다.
\n!리스트추가 [노래] -> 노래를 대기열에 추가합니다.
!리스트삭제 [숫자] -> 대기열에서 입력한 숫자에 해당하는 노래를 지웁니다.""", color = 0x00ff00))

client.run(token)
