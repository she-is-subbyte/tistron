print("ALPHA")
from hashlib import new
import discord, time, random, asyncio, json, pprint
from datetime import datetime

import numpy
intents = discord.Intents.default()
intents.reactions = True

from itertools import cycle
from discord import channel
from discord import *
from numpy.lib.function_base import delete
client = discord.Client(intents = intents)
loaded = False


# with open("C:/Users/embo/3D Objects/lol/discordBot/token.txt") as f:
#     token = f.readlines()[0].split(' , ')[0]
#     print(token)

token = "dm me!"

commandPrefix = "$"

class Command:
    def __init__(self, name, defaultWeight, weightOffset, totalWeight):
        self.name = name
        self.defaultWeight = defaultWeight
        self.weightOffset = weightOffset
        self.totalWeight = totalWeight


def jsonReload():
    print('jsonReload')
    commandList = []
    with open('orders - Backup.json') as f:
        data = json.load(f)
        commandJson = []
        commandJson = data['commands']
        for command in commandJson:
            print(str(command))
            # commandList.append(Command(command['name'], command['defaultWeight'], random.randrange(-100, 100), 0))
            commandList.append(Command(command['name'], command['defaultWeight'], command['weightOffset'], 0))

    print('')
    print('Getting attributes from parsed commands')
    print('commandCount:',len(commandList))
    print('')
    
    for cmd in commandList:
        print('---')
        print("name:",cmd.name)
        print("defaultWeight:",cmd.defaultWeight)
        print("weightOffset:",cmd.weightOffset)
        print("totalWeight:",cmd.totalWeight)
    
    return commandList

#############################################
# Takes an array of Command type variables. #
# returns : one command at random           #
#               Thanks Marie!               #
#############################################
def weightedChoice(comArray):
    # Takes the total weight
    total = 0
    for command in comArray:
        total += command.defaultWeight + command.weightOffset if command.defaultWeight + command.weightOffset > 0 else 0
    # Decides a random number between 0 and the total weight
    roll = random.uniform(0, total)
    # Determines on which command it fell
    cursor = 0
    for command in comArray:
        cursor += command.defaultWeight + command.weightOffset if command.defaultWeight + command.weightOffset > 0 else 0
        if cursor >= roll:
            return command
    print("ERROR : NO VALID COMMAND FOUND.")
    raise ValueError

#####

# def selectCommand(cmdList):
#     heaviestCmd = 0
#     print('selectCommand')
#     cmdWeights = []
#     for cmd in cmdList:
#         print('------')
#         print(cmd.name)
#         cmd.totalWeight = cmd.defaultWeight + cmd.weightOffset
#         print(cmd.totalWeight)
#         cmdWeights.append(cmd.totalWeight)
#         if(cmd.totalWeight < heaviestCmd):
#             print(cmd.name)

#     print("--chosen--")
#     samples = numpy.random.choice(cmdList, 1, True, cmdWeights)
#     print(samples)
#     print(type(samples))
#     print(samples[0].name)



commandTimeRangeMin = 10
commandTimeRangeMax = 50



botChannel = client.get_channel(873302790376669236)
print('just assigned botChannel, type is:',type(botChannel))
commandChannel = client.get_channel(873251206984790079)

lastMessagingUser = client.get_user(863593714600771605)
orderFile = "orders.txt"

jobs = jsonReload()

print(weightedChoice(jobs))    

# selectCommand(jobs)

async def sendCommand():

    botChannel = client.get_channel(873302790376669236)
    commandChannel = client.get_channel(873251206984790079)

    print("comamndMe")
    orders = jobs
    print("orders = cycle(jobs)")
    print(client.is_closed())

    # while(client.is_closed()):
    while(not client.is_closed()):
        if(len(orders) >= 10):
            inSendLoop = True
            # await reload()
            print("while not client.is_closed:")
            currentOrder = weightedChoice(orders)
            print("currentOrder = orders[random.randrange(0, orders.len())]")
            print(client.user)
            print(lastMessagingUser)
            if(lastMessagingUser is not client.user):
                print("await commandChannel.send(currentOrder)")
                await commandChannel.send(currentOrder.name)
            else:
                print("last messagign user was the bot, skipping rollout so as not to spam")
        else:
            inSendLoop = False
            await commandChannel.send("Not enough commands in list! There must be at least 10, and there is currently {0} commands.".format(len(orders)))
        sleepRange = random.randrange(commandTimeRangeMin, commandTimeRangeMax)
        print("sleeping for " + str(sleepRange))
        await asyncio.sleep(sleepRange)
        print("await asyncio.sleep(random.randrange(1,2))")

timedDrop = client.loop.create_task(sendCommand())

async def reload():
    botChannel = client.get_channel(873302790376669236)
    print('just fucking assigned botChannel, type is:',type(botChannel))
    commandChannel = client.get_channel(873251206984790079)

    orderFile = "orders.txt"


    with open(orderFile) as f:
        jobs = f.readlines()
        # you may also want to remove whitespace characters like `\n` at the end of each line
        jobs = [x.strip("\n") for x in jobs] 
        f.close()

    if(not True): # used for initial testing! if this is on, it will send each and every command to the bot channel
        print("jobs, type:",type(jobs))
        for order in jobs:
            print("order, type:",type(order))
            print("type(botChannel): ",type(botChannel))
            await botChannel.send(order)
            time.sleep(0.1)
    
    await botChannel.send("Loaded Assets, Ready to rule!")
    await botChannel.send("Command Count: " + str(len(jobs)))


@client.event
async def on_ready():
    print("we have logged in as {0.user}".format(client))
    await reload()
    

@client.event
async def on_message(message):
    lastMessagingUser = message.author
    print("{1} : {0.channel} : {0.author.name}:  {0.content}".format(message,datetime.now().strftime("%H-%M-%S")))
    if(message.author == client.user):
        return # ignore bot's messages
    
    elif(message.content.startswith(commandPrefix + "hello")):
        await message.channel.send("yo yo yooo, hi there {0.author.name}".format(message))
    elif(message.content.startswith(commandPrefix + "reload")):

        print("reload")
        loaded = False
        print("we have logged in as {0.user}".format(client))
        await reload()
    elif(message.content.startswith(commandPrefix + "commandMe")):
        await sendCommand()
    elif(message.content.startswith(commandPrefix + "linkChannel")):
        if(message.content.split(' ')[1] == "bot"):
            botChannel = message.channel
            await botChannel.send("Linked botChannel to " + str(message.channel))
        elif(message.content.split(' ')[1] == "commands"):
            commandChannel = message.channel
            await commandChannel.send("Linked CommandChannel to " + str(message.channel))
    elif(message.content.startswith(commandPrefix + "commandCount")):
        await reload()
    elif(message.content.startswith(commandPrefix + "addCommand")):

        print("getting old jobs")
        with open(orderFile, "r") as f:
            jobs = f.readlines()
            # you may also want to remove whitespace characters like `\n` at the end of each line
            jobs = [x.strip("\n") for x in jobs] 
            f.close()
        print("got old jobs")
        with open(orderFile, "a") as f:
            newCommand = message.content.split(" ", 0)
            print("Sanitizing Command")
            print(newCommand)

            newCommand = newCommand[(len(newCommand)-1)]
            print("newCommand = newCommand[(len(newCommand)-1)]")
            print(newCommand)

            prefix = "$addCommand"
            print("before removing prefix")
            print(newCommand)
            newCommand = newCommand.split(" ", 1)
            newCommand = newCommand[1]
            print("after removing prefix")
            print(newCommand)
            print("command Data Sanitation Complete")
            f.write(str("\n" + str(newCommand)))
            f.close()
            await reload()
            await message.channel.send(str("Added Command \"") + str(newCommand) + str("\""))
    elif(message.content.startswith(commandPrefix + "listCommands")):
        with open(orderFile, "r") as f:
            jobs = f.readlines()
            # you may also want to remove whitespace characters like `\n` at the end of each line
            jobs = [x.strip("\n") for x in jobs] 
            f.close()

            jobList = ""
            for job in jobs:
                if(job != ""):
                    jobList = str(jobList) + str("\n") + str(job)
                else:
                    jobs.remove(job)

            # send
            print(jobList)
            if(jobList == ""):
                await message.channel.send("Command List Empty, Add commands with \"$addCommand {command to be obeyed!}\"")
            else:
                await message.channel.send(jobList)
                await message.channel.send("Command Count: " + str(len(jobs)))
    elif(message.content.startswith(commandPrefix + "clearCommands")):  
        if(message.content.endswith("LMAONADE")):
            msg = message.content
            await message.delete()
            print("get old jobs")
            with open(orderFile, "r") as f:
                jobs = f.readlines()
                f.close()
            print("save old jobs to backup")
            with open("BACKUP - " + str(datetime.date.today()) + " - " + orderFile, "x") as f:
                f.writelines(jobs)
                f.close
            print("clear jobs")
            with open(orderFile, "w") as f:
                f.write(str(""))
                f.close()
                await reload()
            print("Jobs Cleared...")
            await message.channel.send(str("Cleared All Commands"))
        else:
            await message.channel.send("Error: Incorrect Password, Admins Only...")
    elif(message.content.startswith(commandPrefix + "config")):
        sanTemp = message.content.split(' ')
        commandTimeRangeMin = int(sanTemp[1])
        commandTimeRangeMax = int(sanTemp[2])
        await message.channel.send("Set commandTimeRangeMin to {0}, commandTimeRangeMax to {1}".format(int(sanTemp[1]),int(sanTemp[2])))
        print(str(commandTimeRangeMin) + " - " + str(commandTimeRangeMax))

    elif(message.content.startswith(commandPrefix + "startLoop")):
        timedDrop = client.loop.create_task(sendCommand())
        await message.channel.send("Starting Semi-Randomly Timed Dropping of Commands")
    
    # elif(message.content.startswith(commandPrefix + "stopLoop")):
        
    #     # timedDrop.cancel()
    #     await message.channel.send("Stopped Semi-Randomly Timed Dropping of Commands")
    #     await message.channel.send("didn't actually, this is broken atm, @ emily so she can turn it off manually")

    elif(message.content.startswith(commandPrefix + "")):
        print("unknown command")
        await message.channel.send("Unknown BotCommand!")

@client.event
async def on_reaction_add(reaction, user):
    print(user.name + ": added reaction " + reaction + " to message " + reaction.message)



client.run(token)