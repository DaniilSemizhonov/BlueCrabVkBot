from vkbottle.bot import Bot, Message
from vkbottle import GroupEventType, GroupTypes, VKAPIError
from vkbottle import Keyboard, KeyboardButtonColor, Text, OpenLink, Location, EMPTY_KEYBOARD
from config import vktoken
from config import mongoclient
from pymongo import MongoClient
from datetime import date

today = date.today()
cluster = MongoClient(mongoclient)
db = cluster["BlueCrabVkBotData"]
botsuserscoll = db["BotsUsers"]
foodmenucoll = db["FoodMenu"]
timetablecoll = db["Timetable"]
admincoll = db["BotsAdmins"]
bot = Bot(token=vktoken)
@bot.on.raw_event(GroupEventType.GROUP_JOIN, dataclass=GroupTypes.GroupJoin)
async def group_join(event: GroupTypes.GroupJoin):
    try:
        await bot.api.messages.send(
            peer_id=event.object.user_id,
            message="Привет, океанец",
            random_id=0
        )
    except VKAPIError(901):
        pass


@bot.on.message(text="userinfo")
async def message_handler(message = Message):
    user = await bot.api.users.get(message.from_id)
    #https://vk.com/id
    await message.answer(f"You {user[0].first_name} {user[0].last_name}, {user[0].id}, {today}")
@bot.on.private_message(text=["/food <item>", "/food"])
async def message_handler(message = Message, item=None):
    admin_list = admincoll.find()
    for b in admin_list:
        admins = b["admin"]
    user = await bot.api.users.get(message.from_id)
    first_name = user[0].first_name
    last_name = user[0].last_name
    id = user[0].id
    print(admins)
    if id == int(admins):
        if foodmenucoll.count_documents({"date": str(today)}) == 0:
            if item is not None:
                foodmenucoll.insert_one({"_id": id,"first_name": first_name,
                                    "last_name": last_name, "date": str(today), "food": item})
                await message.answer("Всё записал")
            else:
                await message.answer("Вы указали аргумент пустым...")
        else:
            await message.answer("На сегодня меню в столовой уже добавили")
    else:
        await message.answer("Я тебя не знаю")
@bot.on.private_message(text=["/timetable <item>", "/timetable"])
async def message_handler(message = Message, item=None):
    admins = admincoll.find_one()["admin"]
    user = await bot.api.users.get(message.from_id)
    first_name = user[0].first_name
    last_name = user[0].last_name
    id = user[0].id
    if id == admins:
        if timetablecoll.count_documents({"date": str(today)}) == 0:
            if item is not None:
                timetablecoll.insert_one({"_id": id, "first_name": first_name,
                                         "last_name": last_name, "date": str(today), "timetable": item})
                await message.answer("Всё записал")
            else:
                await message.answer("Вы указали аргумент пустым...")
        else:
            await message.answer("На сегодня расписание уже добавили")
    else:
        await message.answer("Я тебя не знаю")
@bot.on.private_message(text=["/op <item>", "/op"])
async def message_handler(message = Message, item=None):
    user = await bot.api.users.get(message.from_id)
    id = user[0].id
    if id == 598384785:
        if item is not None:
            admincoll.insert_one({"date": str(today), "admin": item})
            await message.answer("Всё записал")
        else:
            await message.answer("Вы указали аргумент пустым...")
    else:
        await message.answer("Команда доступна только галвному разработчику")
@bot.on.message(text="Начать")
async def message_handler(message = Message):
    user = await bot.api.users.get(message.from_id)
    id = user[0].id
    first_name = user[0].first_name
    last_name = user[0].last_name
    keyboard = Keyboard()

    keyboard.add(Text("Расписания дня на сегодня"), color=KeyboardButtonColor.NEGATIVE)
    keyboard.add(Text("Меню в столовой"), color=KeyboardButtonColor.POSITIVE)
    keyboard.row()

    keyboard.add(OpenLink("https://vk.com/bluecrabvkbot", "Наша группа вк"))
    keyboard.add(OpenLink("https://vk.com/daniil_semizhonov", "Разработчик бота"))
    if botsuserscoll.count_documents({"_id": id}) == 0:
        botsuserscoll.insert_one({"_id": id, "first_name": first_name,
                                  "last_name": last_name})
        keyboard = Keyboard()

        keyboard.add(Text("Расписания дня на сегодня"), color=KeyboardButtonColor.NEGATIVE)
        keyboard.add(Text("Меню в столовой"), color=KeyboardButtonColor.POSITIVE)
        keyboard.row()

        keyboard.add(OpenLink("https://vk.com/bluecrabvkbot", "Наша группа вк"))
        keyboard.add(OpenLink("https://vk.com/daniil_semizhonov", "Разработчик бота"))
        await message.answer("Привет", keyboard=keyboard)
    else:
        keyboard_ = Keyboard()

        keyboard_.add(Text("Расписания дня на сегодня"), color=KeyboardButtonColor.NEGATIVE)
        keyboard_.add(Text("Меню в столовой"), color=KeyboardButtonColor.POSITIVE)
        await message.answer("Я снова с вами", keyboard=keyboard_)
@bot.on.message(text="Меню в столовой")
async def message_handler(message = Message):
    if foodmenucoll.count_documents({"date": str(today)}) == 0:
        await message.answer("Админ пока не добавил сегодняшнее меню")
    else:
        food = foodmenucoll.find_one()["food"]
        await message.answer(food)

@bot.on.message(text="Расписания дня на сегодня")
async def message_handler(message = Message):
    if timetablecoll.count_documents({"date": str(today)}) == 0:
        await message.answer("Админ пока не добавил сегодняшнее расписание")
    else:
        food = timetablecoll.find_one()["timetable"]
        await message.answer(food)
bot.run_forever()
