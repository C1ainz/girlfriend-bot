import asyncio
import logging
import os
import json
from datetime import datetime, date
from pathlib import Path
from random import choice

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

# Планировщик задач
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ====== НАСТРОЙКИ / ENV ======
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
if not BOT_TOKEN or BOT_TOKEN.startswith("ВСТАВЬ"):
    raise SystemExit("❌ BOT_TOKEN не задан. Откройте .env и пропишите токен от @BotFather")

SECRET_CODE = os.getenv("SECRET_CODE", "ежевика").strip()  # Секретное слово
GF_NAME = os.getenv("GF_NAME", "Любимая").strip()
ANNIVERSARY = os.getenv("ANNIVERSARY", "2024-02-14").strip()  # формат YYYY-MM-DD

# файлы данных
DATA_DIR = Path("./data")
DATA_DIR.mkdir(exist_ok=True)
ALLOWED_FILE = DATA_DIR / "allowed.json"

# ====== СПИСКИ СООБЩЕНИЙ ======

# 20+ утренних напутствий
GOOD_MORNINGS = [
    "Доброе утро, {name}! ☀️ Пусть сегодняшний день будет лёгким и добрым.",
    "С добрым утром, {name}! 🌸 Верю в тебя — всё получится!",
    "Просыпайся, солнышко ☀️ Сегодня будет много поводов улыбаться.",
    "Новый день — новые победы, {name}! 💪 Я рядом мыслью.",
    "Пусть утро принесёт нежность, а день — маленькие чудеса ✨",
    "Обними этот день, {name}, он уже обнимает тебя в ответ 🤍",
    "Пусть сегодня всё складывается мягко и по-твоему ☕️",
    "Ты сильная и прекрасная. Этот день об этом узнает 😉",
    "Пусть усталость отступит, а вдохновение найдёт тебя первым 🌿",
    "С добрым утром! Пей водичку, дыши глубже — и вперёд к хорошему.",
    "Пусть каждый шаг сегодня будет спокойным и уверенным 👣",
    "Пусть удача сама найдёт тебя, а я — всегда буду рядом мыслями 💌",
    "Сегодня мир чуточку лучше, потому что в нём есть ты ✨",
    "Пусть твои глаза сегодня сияют чаще обычного ✨",
    "День будет добрым, потому что ты его такой сделаешь, {name} 🌼",
    "Пусть на всё важное найдутся силы и время, а на лишнее — нет 🙂",
    "Помни: ты достойна самого лучшего. И сегодняшний день это подтвердит 💖",
    "Если станет шумно — у тебя всегда есть мой тихий обниматель 🫶",
    "Пусть мечты подскажут маршрут, а сердце — правильный темп 💫",
    "Ты справишься со всем, что запланировала. И ещё останутся силы на чай 🍵",
    "Доброго утра, красавица! Пусть радости будет больше, чем поводов волноваться 🌷",
]

# 100 комплиментов по умолчанию (если нет файла compliments.txt)
COMPLIMENTS_DEFAULT = [
    "Ты — моё самое любимое чудо.",
    "С тобой даже будни похожи на праздник.",
    "С тобой я улыбаюсь даже мысленно.",
    "Ты — моё спокойствие и моя искра одновременно.",
    "Ты — лучшее решение всех моих задач.",
    "Твои глаза — мой дом.",
    "С тобой любое «потом» хочется превратить в «сейчас».",
    "Ты делаешь мои дни теплее и светлее.",
    "Ты прекрасна таким естественным образом — это магия.",
    "Мне нравится любоваться тобой, как любимой песней.",
    "Ты умеешь превращать тишину в уют.",
    "Твои мысли — как звёзды: яркие и добрые.",
    "С тобой даже кофе вкуснее.",
    "Ты — человек, с которым хочется делить каждое «смотри!»",
    "Твоё сердце — моя мягкая сила.",
    "Ты талантлива быть собой — и это бесценно.",
    "Твоя улыбка — мой персональный рассвет.",
    "Ты делаешь мир вокруг аккуратнее и теплее.",
    "Ты вдохновляешь просто существованием.",
    "С тобой хочется быть лучшей версией себя.",
    "Ты умеешь слышать по-настоящему.",
    "Ты — моё спокойное «всё хорошо».",
    "В твоих словах всегда много смысла и света.",
    "Ты — редкий человек «и красивый, и умный».",
    "Твой смех лечит лучше витаминов.",
    "Твоя забота — это уют в квадрате.",
    "Ты делаешь сложное проще одним взглядом.",
    "Ты — моё любимое случайно-не-случайное.",
    "Рядом с тобой у меня получаются добрые дни.",
    "Ты — доказательство, что нежность сильнее.",
    "Ты носишь красоту легко, как воздух.",
    "С тобой можно молчать — и это разговор.",
    "Ты — мой маленький космос.",
    "В тебе красиво даже упорство.",
    "Ты умеешь выбирать главное.",
    "Твоё «получится» действительно сбывается.",
    "Ты — человек, которому верят растения и коты.",
    "Ты умеешь бережно радоваться мелочам.",
    "Ты — редкая комбинация тепла и характера.",
    "Ты — мягкий якорь и лёгкий парус.",
    "Твои идеи пахнут свежестью.",
    "Ты — как утро после дождя.",
    "Ты из тех людей, с кем хорошо и тихо, и громко.",
    "В тебе удивительно ладно всё со всем.",
    "Ты — уют в человеческом виде.",
    "Твоя искренность обезоруживает.",
    "Ты — мой самый красивый аргумент за «чудеса есть».",
    "Ты светишься даже в серых днях.",
    "С тобой у мира правильная температура.",
    "Ты — нежность, которая умеет постоять за себя.",
    "Твоё «спасибо» звучит как музыка.",
    "Ты умеешь делать важное нестрашным.",
    "Ты — человек «давай попробуем».",
    "С тобой даже ожидание приятное.",
    "Ты — моя любимая привычка.",
    "Ты просто идёшь — и всё становится на свои места.",
    "Твои объятия — лучший перезапуск.",
    "Ты — пространство, где спокойно быть собой.",
    "Ты делаешь мир честнее.",
    "Ты — совпадение, о котором мечтали календари.",
    "Твоё настроение задаёт погоду в квартире.",
    "Ты — мой маленький домашний праздник.",
    "Твоя решительность — красиво.",
    "Ты видишь красоту там, где другие спешат.",
    "Ты — мой самый любимый голос.",
    "Твоё «доброе утро» лучше будильника.",
    "Ты умеешь хранить тишину и делиться светом.",
    "Ты — улыбка, которая остаётся дольше дня.",
    "С тобой легче верить в себя.",
    "Ты — мой спокойный берег.",
    "Ты красива в каждой своей «несовершенности».",
    "Ты — доброта, у которой есть характер.",
    "Ты — редкая ясность в шумном мире.",
    "Твои шаги звучат уверенностью.",
    "Ты — моё лучшее «да».",
    "Твоя нежность — не слабость, а сила.",
    "Ты умеешь согревать словом.",
    "Ты — человек, которого ищут стихи.",
    "Тебе идёт свет из окна и свет внутри.",
    "Ты — мой комплимент вселенной.",
    "Ты умеешь беречь важное.",
    "С тобой хочется строить планы и завтрак.",
    "Ты — любимая точка маршрута.",
    "Твои решения — про мудрость, а не про шум.",
    "Ты — мой любимый «домой».",
    "Ты делаешь фотографии добрее.",
    "Ты — человек, ради которого хочется быть внимательным.",
    "Ты умеешь красиво уставать и честно отдыхать.",
    "Ты — мой маленький талант радоваться.",
    "Твои вопросы умнее многих ответов.",
    "Ты — моя лучшая новость дня.",
    "Ты красивее любых фильтров.",
    "С тобой не страшно быть смешным.",
    "Ты — моя самая тёплая мысль.",
    "В тебе нежность не спорит с силой.",
    "Ты — человек, с которым хочется стареть, не взрослея.",
    "Ты — вдохновение в мягкой упаковке.",
    "Твоя улыбка умеет лечить усталость.",
    "Ты — мой любимый сюжет без финала.",
    "Ты делаешь паузы значимыми.",
    "Ты — гармония, которая дышит.",
    "С тобой мир не только крутится — он танцует.",
    "Ты — вкус утреннего света.",
    "Ты — лучший ответ на «зачем».",
    "Ты — человек, с которым всегда «вовремя».",
    "Ты — моё счастливое совпадение с реальностью.",
    "Ты — моя ежедневная благодарность.",
]

# ====== ЗАГРУЗКА КОМПЛИМЕНТОВ ИЗ ФАЙЛА (если есть) ======
def load_compliments():
    path = Path("./compliments.txt")
    if path.exists():
        txt = path.read_text(encoding="utf-8")
        items = [line.strip() for line in txt.splitlines() if line.strip()]
        # если в файле меньше 100 — докинем из дефолтов, чтобы пул был большим
        if len(items) < 100:
            need = 100 - len(items)
            items.extend(COMPLIMENTS_DEFAULT[:need])
        return items
    return COMPLIMENTS_DEFAULT

COMPLIMENTS = load_compliments()

# ====== ДОСТУП ТОЛЬКО ДЛЯ НЕЁ ======
def get_allowed_id() -> int | None:
    if ALLOWED_FILE.exists():
        try:
            data = json.loads(ALLOWED_FILE.read_text(encoding="utf-8"))
            return int(data.get("user_id"))
        except Exception:
            return None
    return None

def set_allowed_id(user_id: int, name: str | None = None):
    ALLOWED_FILE.write_text(json.dumps({"user_id": user_id, "name": name}, ensure_ascii=False, indent=2), encoding="utf-8")

def access_granted(user_id: int) -> bool:
    allowed = get_allowed_id()
    return allowed is not None and allowed == user_id

# ====== БОТ ======
logging.basicConfig(level=logging.INFO)
bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💌 Люблю", callback_data="love")],
        [InlineKeyboardButton(text="✨ Комплимент", callback_data="compliment")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help")]
    ])

@dp.message(CommandStart())
async def cmd_start(msg: Message):
    allowed = access_granted(msg.from_user.id)
    if allowed:
        await msg.answer(
            f"Привет, {GF_NAME}! 🤍\n"
            "Я только для тебя. Жми на кнопки ниже:",
            reply_markup=main_keyboard(),
        )
    else:
        await msg.answer(
            "Привет! Это приватный бот. "
            "Если ты — та самая, отправь мне секретное слово 🌟"
        )

@dp.message(Command("help"))
async def cmd_help(msg: Message):
    if not access_granted(msg.from_user.id):
        await msg.answer("Это приватный бот. Введи секретное слово, если оно у тебя есть.")
        return
    await msg.answer("Команды:\n/start — приветствие\n/love — тёплое письмо\n/compliment — случайный комплимент")

@dp.callback_query(F.data == "help")
async def cb_help(cb: CallbackQuery):
    await cmd_help(cb.message)
    await cb.answer()

@dp.callback_query(F.data == "compliment")
async def cb_compliment(cb: CallbackQuery):
    if not access_granted(cb.from_user.id):
        await cb.answer("Только для одного человека 🌙", show_alert=True)
        return
    await cb.message.answer(choice(COMPLIMENTS))
    await cb.answer()

def days_since_anniversary() -> int:
    try:
        d = datetime.strptime(ANNIVERSARY, "%Y-%m-%d").date()
    except Exception:
        d = date.today()
    return (date.today() - d).days

def love_text() -> str:
    days = days_since_anniversary()
    return (
        f"<b>Моё письмо для {GF_NAME}</b> 💌\n\n"
        f"С тобой уже <b>{days} дн.</b> — и каждый из них делает меня счастливее.\n"
        "Ты — моё лучшее решение, моё спокойствие и моя искра.\n"
        "Спасибо за тепло, смех и вдохновение. Обнимаю тебя мыслями прямо сейчас. 🤍"
    )

@dp.message(Command("love"))
async def cmd_love(msg: Message):
    if not access_granted(msg.from_user.id):
        await msg.answer("Это письмо я бережно храню для одного человека 🌙")
        return
    await msg.answer(love_text())

@dp.callback_query(F.data == "love")
async def cb_love(cb: CallbackQuery):
    if not access_granted(cb.from_user.id):
        await cb.answer("Секретное письмо только для неё 💫", show_alert=True)
        return
    await cb.message.answer(love_text())
    await cb.answer()

# ====== СЕКРЕТНОЕ СЛОВО (привязка) ======
@dp.message(F.text)
async def on_text(msg: Message):
    if access_granted(msg.from_user.id):
        # Уже привязана — можно добавлять фразы командой !add
        text = msg.text.strip()
        if text.startswith("!add "):
            new_c = text[5:].strip()
            if len(new_c) > 3:
                path = Path("compliments.txt")
                current = path.read_text(encoding="utf-8") if path.exists() else ""
                path.write_text((current + ("\n" if current else "") + new_c), encoding="utf-8")
                await msg.answer("Добавила это в список комплиментов ✨")
                return
        await msg.answer("Я рядом 🤍 Нажми на кнопки выше.")
        return

    # Если ещё не привязана — ждём секретное слово
    if msg.text.strip().lower() == SECRET_CODE.lower():
        set_allowed_id(msg.from_user.id, msg.from_user.full_name)
        await msg.answer(
            f"Привет, {GF_NAME}! Теперь я только для тебя. Жми на кнопки ниже:",
            reply_markup=main_keyboard(),
        )
    else:
        await msg.answer("Это приватный бот. Если у тебя есть секретное слово — пришли его 🌟")

# ====== УТРЕННЯЯ РАССЫЛКА В 08:00 МСК ======
async def good_morning():
    user_id = get_allowed_id()
    if not user_id:
        return
    try:
        text = choice(GOOD_MORNINGS).format(name=GF_NAME)
        await bot.send_message(user_id, text)
    except Exception as e:
        logging.error(f"Не удалось отправить утреннее сообщение: {e}")

async def main():
    # Планировщик в часовом поясе Москвы
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    # Каждый день в 08:00 по Москве
    scheduler.add_job(good_morning, "cron", hour=8, minute=0)
    scheduler.start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
