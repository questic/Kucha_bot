import os
import discord
import random
import asyncio
from os import system
from os.path import join, dirname
from dotenv import load_dotenv
from keep_alive import keep_alive


def load_environment_variables():
    dotenv_path = join(dirname(__file__), '../.env')
    load_dotenv(dotenv_path)
    return os.getenv('TOKEN')


def create_client():
    intents = discord.Intents.all()
    return discord.Client(intents=intents)


async def handle_rps_game(message, d_bot):
    await message.channel.send('Начинаем новую игру! Ваш ход: камень, ножницы или бумага?')

    def check(m):
        return m.content in ['камень', 'ножницы', 'бумага'] and m.channel == message.channel and m.author != d_bot.user

    try:
        user_choice_message = await d_bot.wait_for('message', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        return await message.channel.send('Игра прервана, так как никто не выбрал ход в течение 30 секунд.')

    user_choice = user_choice_message.content
    bot_choice = random.choice(['камень', 'ножницы', 'бумага'])
    result_message = get_rps_result_message(user_choice, bot_choice)
    await message.channel.send(result_message)


def get_rps_result_message(user_choice, bot_choice):
    if user_choice == bot_choice:
        return f'Вы выбрали {user_choice}, а я выбрал {bot_choice}. Ничья!'
    elif (user_choice == 'камень' and bot_choice == 'ножницы') or (
            user_choice == 'ножницы' and bot_choice == 'бумага') or (
            user_choice == 'бумага' and bot_choice == 'камень'):
        return f'Вы выбрали {user_choice}, а я выбрал {bot_choice}. Поздравляем, вы победили!'
    else:
        return f'Вы выбрали {user_choice}, а я выбрал {bot_choice}. К сожалению, вы проиграли.'


async def handle_roll_command(message):
    try:
        _, start, end = message.content.split()
        start, end = int(start), int(end)
        if start >= end:
            raise ValueError
    except ValueError:
        await message.channel.send(
            'Неправильный формат команды. Правильный формат: !roll [начало] [конец] (начало < конец)')
        return

    result = random.randint(start, end)
    await message.channel.send(f'Выпало число {result} (диапазон [{start}, {end}])')


async def handle_voice_channel(member, before, after):
    CHANNEL_ID = 1098328023129931796
    if after.channel and after.channel.id == CHANNEL_ID:
        guild = member.guild
        new_channel = await guild.create_voice_channel(f"{member.display_name} Channel",
                                                       category=after.channel.category)
        await member.move_to(new_channel)

        while True:
            await asyncio.sleep(30)
            if len(new_channel.members) == 0:
                await new_channel.delete()
                break


d_bot = create_client()


@d_bot.event
async def on_ready():
    await d_bot.change_presence(activity=discord.Game(name="КУЧА"))
    print(f'Logged {d_bot.user}')


@d_bot.event
async def on_message(message):
    if message.author == d_bot.user:
        return
    if message.content.startswith('!rps start'):
        await handle_rps_game(message, d_bot)
    elif message.content.startswith('!roll'):
        await handle_roll_command(message)


@d_bot.event
async def on_voice_state_update(member, before, after):
    await handle_voice_channel(member, before, after)


keep_alive()
DISCORD_TOKEN = load_environment_variables()

try:
    d_bot.run(DISCORD_TOKEN)
except discord.errors.HTTPException:
    print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
    system("python restarter.py")
    system('kill 1')
