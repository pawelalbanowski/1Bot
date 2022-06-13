from pprint import pprint
from checks import registration_check
from discord.utils import get
from json_util import json_read, json_write


async def register(msg, roles):  # .register nr, gt, car or #register @mention nr, gt, car
    # admin registering other user
    if len(msg.mentions) != 0:
        if 'Admin' in roles:
            raw_command = msg.content.split('>')[1].split(',')
            parameters = list(map((lambda a: a.strip()), raw_command))
            reg_data = json_read("drivers.json")
            check = await registration_check(msg, parameters, reg_data, msg.mentions[0].id)
            if check:
                driver = {
                    "id": msg.mentions[0].id,
                    "gt": parameters[1],
                    "nr": parameters[0],
                    "league": 0,
                    "car": parameters[2],
                    "swaps": 0
                }
                reg_data["drivers"].append(driver)
                # increase total on the chosen car
                for car in reg_data["cars"]:
                    if car["id"] == parameters[2]:
                        car["quantity"] += 1
                        chosen_car = car["name"]
                json_write("drivers.json", reg_data)
                # modify roles
                viewer_role = get(msg.guild.roles, name='Viewer')
                driver_role = get(msg.guild.roles, name='Driver')
                await msg.mentions[0].remove_roles(viewer_role)
                await msg.mentions[0].add_roles(driver_role)
                if msg.mentions[0].nick is None:
                    await msg.mentions[0].edit(nick=f'#{parameters[0]} {msg.mentions[0].name}')
                else:
                    await msg.mentions[0].edit(nick=f'#{parameters[0]} {msg.mentions[0].nick}')
                await msg.reply(f'Registered {msg.mentions[0].mention} with number {parameters[0]} and {chosen_car}')
        else:
            await msg.reply('Insufficient permissions')
            return False
    # user registering themselves
    elif 'Viewer' in roles:
        raw_command = (msg.content.split(' ', 1)[1]).split(',')
        parameters = list(map((lambda a: a.strip()), raw_command))
        reg_data = json_read("drivers.json")
        check = await registration_check(msg, parameters, reg_data, msg.author.id)
        if check:
            driver = {
                "id": msg.author.id,
                "gt": parameters[1],
                "nr": int(parameters[0]),
                "league": 0,
                "car": parameters[2],
                "swaps": 0
            }
            reg_data["drivers"].append(driver)
            # increase total on the chosen car
            for car in reg_data["cars"]:
                if car["id"] == parameters[2]:
                    car["quantity"] += 1
                    chosen_car = car["name"]
            json_write("drivers.json", reg_data)
            # modify roles
            viewer_role = get(msg.guild.roles, name='Viewer')
            driver_role = get(msg.guild.roles, name='Driver')
            await msg.author.remove_roles(viewer_role)
            await msg.author.add_roles(driver_role)
            if msg.author.nick is None:
                await msg.author.edit(nick=f'#{parameters[0]} {msg.author.name}')
            else:
                await msg.author.edit(nick=f'#{parameters[0]} {msg.author.nick}')
            await msg.reply(f'Registered {msg.author.mention} with number #{parameters[0]} and {chosen_car}')
    else:
        await msg.reply('Already registered')
        return False


async def unregister(msg, roles):  # .unregister @mention
    if 'Admin' in roles:
        reg_data = json_read("drivers.json")
        for member in msg.mentions:
            chosen_car = "0"
            for driver in reg_data["drivers"]:
                if driver["id"] == member.id:
                    chosen_car = driver["car"]
                    reg_data["drivers"].remove(driver)
            for car in reg_data["cars"]:
                if car["id"] == chosen_car:
                    car["quantity"] -= 1
            viewer_role = get(msg.guild.roles, name='Viewer')
            driver_role = get(msg.guild.roles, name='Driver')
            await member.remove_roles(driver_role)
            await member.add_roles(viewer_role)
            if member.nick is not None and member.nick.startswith('#'):
                await member.edit(nick=member.nick[4:])
            await msg.reply(f'Unregistered {member.mention}')
        json_write("drivers.json", reg_data)
    else:
        await msg.reply('Insufficient permissions')


async def swap(msg, roles):  # .swap car or .swap car @mention
    if len(msg.mentions) != 0:
        if 'Admin' in roles:
            raw_command = msg.content.split('>')[1].split(',')
            parameters = list(map((lambda a: a.strip()), raw_command))
            reg_data = json_read("drivers.json")
            for driver in reg_data['drivers']:
                if driver["id"] == msg.mentions[0].id:
                    for car in reg_data["cars"]:
                        if car["id"] == parameters[0]:
                            car["quantity"] += 1
                        if car["id"] == driver["car"]:
                            car["quantity"] -= 1
                    driver["car"] = parameters[0]
                    await msg.reply(f"Car swap successful!")
                    json_write("drivers.json", reg_data)
                    return
    else:
        if 'Driver' in roles:
            parameter = (msg.content.split(' ', 1)[1]).strip()
            reg_data = json_read("drivers.json")
            if int(parameter) in list(range(1, 6)):
                for driver in reg_data['drivers']:
                    if driver["id"] == msg.author.id:
                        if driver["swaps"] == 0:
                            for car in reg_data["cars"]:
                                if car["id"] == parameter:
                                    car["quantity"] += 1
                                if car["id"] == driver["car"]:
                                    car["quantity"] -= 1
                            driver["car"] = parameter
                            driver["swaps"] = 1
                            await msg.reply(f"Car swap successful!")
                            json_write("drivers.json", reg_data)
                        else:
                            await msg.reply("Car swap already used")
            else:
                await msg.reply('Invalid car id')


async def pet(msg):  # .pet
    await msg.reply(f'Fuck you {msg.author.mention}')


async def gnfos(msg):  # .gnfos
    await msg.reply('Good neighbors from our server :pray:')


async def nickname(msg, roles):  # .nickname @mention nickname
    if 'Admin' in roles:
        member = msg.mentions[0]
        parameters = msg.content.split('>')
        if member.nick is None:
            await member.edit(nick=parameters[1].strip())
        elif member.nick.startswith('#'):
            await member.edit(nick=f'{member.nick[0:4]}{parameters[1].strip()}')
        else:
            await member.edit(nick=parameters[1].strip())
    else:
        await msg.reply('Insufficient permissions')


async def role(msg, roles):  # .role @mention role, role
    if 'Admin' in roles:
        parameters = msg.content.split('>')[1].split(',')
        parameters = list(map((lambda a: a.strip()), parameters))
        for param in parameters:
            if get(msg.mentions[0].roles, name=param) is None:
                try:
                    role_obj = get(msg.guild.roles, name=param)
                    await msg.mentions[0].add_roles(role_obj)
                except AttributeError:
                    await msg.reply(f'Role {param} doesnt exist')
            else:
                try:
                    role_obj = get(msg.guild.roles, name=param)
                    await msg.mentions[0].remove_roles(role_obj)
                except AttributeError:
                    await msg.reply(f'Role {param} doesnt exist')
        await msg.reply(f'Modified roles of {msg.mentions[0].mention}')
    else:
        await msg.reply('Insufficient permissions')


async def addrole(msg, roles):  # .addrole role @mention, @mention
    if 'Admin' in roles:
        role_to_add = get(msg.guild.roles, name=msg.content.split(' ')[1])
        for user in msg.mentions:
            await user.add_roles(role_to_add)
    else:
        await msg.reply('Insufficient permissions')


async def removerole(msg, roles):  # .removerole role @mention, @mention
    if 'Admin' in roles:
        role_to_remove = get(msg.guild.roles, name=msg.content.split(' ')[1])
        for user in msg.mentions:
            await user.remove_roles(role_to_remove)
    else:
        await msg.reply('Insufficient permissions')


async def nuke(msg, roles):  # .nuke role
    if 'Admin' in roles:
        role_to_remove = get(msg.guild.roles, name=msg.content.split(' ')[1])
        for user in msg.guild.members:
            await user.remove_roles(role_to_remove)
            await msg.reply('Nuked the server :albantler:')
