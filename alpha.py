print("ALPHA")
import discord, time, random, asyncio, json, pprint, os
import numpy, math
from constants import *
from datetime import datetime
from hashlib import new
from itertools import cycle
from numpy.lib.function_base import delete

intents = discord.Intents.default()
intents.reactions = True
intents.members = True
client = discord.Client(intents = intents)
loaded = False

path = str(os.getcwd() + '\\tistron\\')

class Command:
    def __init__(self, name, defaultWeight, weightOffset):
        self.name = name
        self.defaultWeight = defaultWeight
        self.weightOffset = weightOffset
    
    def __str__(self):
        return self.name
    
    async def sendToChannel(self, channel):
        await channel.send(self.name)
    
    def resetWeight(self):
        self.weightOffset = 0
    
    def increaseWeight(self):
        self.weightOffset += math.floor(self.defaultWeight/10)
        
    def saveToJSON(self, file, isLast):
        file.write("\t\t{\"name\": \"" + self.name + "\",\"defaultWeight\": " + str(self.defaultWeight) + ",\"weightOffset\": " + str(self.weightOffset) + "}")
        if not isLast:
            file.write(",")
        file.write("\n")

def saveCommands(comArray, filename):
    file = open(filename, "w")
    file.write("{\n")
    file.write("\t\"commands\": [\n")
    cursor = 0
    for command in comArray:
        cursor += 1
        command.saveToJSON(file, True if cursor == len(comArray) else False)
    file.write("\t]\n}")

def jsonReload():
    print('jsonReload')
    commandList = []
    with open(path + 'orders - Backup.json') as f:
        data = json.load(f)
        commandJson = []
        commandJson = data['commands']
        for command in commandJson:
            print(str(command))
            commandList.append(Command(command['name'], command['defaultWeight'], command['weightOffset']))

    print('')
    print('Getting attributes from parsed commands')
    print('commandCount:',len(commandList))
    print('')
    
    for cmd in commandList:
        print('---')
        print("name:",cmd.name)
        print("defaultWeight:",cmd.defaultWeight)
        print("weightOffset:",cmd.weightOffset)
    
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

###### OLD CODE FOR HISTORY PURPOSES. ################################
#
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
#
#     print("--chosen--")
#     samples = numpy.random.choice(cmdList, 1, True, cmdWeights)
#     print(samples)
#     print(type(samples))
#     print(samples[0].name)
#
######################################################################

async def sendCommand():

    global jobs
    global lastMessagingUser

    print("comamndMe")
    orders = jobs
    print("orders = cycle(jobs)")
    print(client.is_closed())

    # while(client.is_closed()):
    while(not client.is_closed()):
        if(len(orders) >= 10):
            # await reload()
            print("while not client.is_closed:")
            currentOrder = weightedChoice(orders)
            for order in orders:
                order.increaseWeight()
            currentOrder.resetWeight()
            print("currentOrder = orders[random.randrange(0, orders.len())]")
            print(client.user)
            print(lastMessagingUser)
            if(lastMessagingUser is not client.user):
                print("await commandChannel.send(currentOrder)")
                await currentOrder.sendToChannel(commandChannel)
            else:
                print("last messagign user was the bot, skipping rollout so as not to spam")
        else:
            await commandChannel.send("Not enough commands in list! There must be at least 10, and there is currently {0} commands.".format(len(orders)))
        sleepRange = random.randrange(COMMAND_TIME_RANGE_MIN, COMMAND_TIME_RANGE_MAX)
        print("sleeping for " + str(sleepRange))
        await asyncio.sleep(sleepRange)
        print("await asyncio.sleep(random.randrange(1,2))")

async def reload():
    botChannel = client.get_channel(BOT_CHANNEL_ID)
    print('just fucking assigned botChannel, type is:',type(botChannel))
    commandChannel = client.get_channel(COMMAND_CHANNEL_ID)

    orderFile = path+"orders.txt"

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
            await order.sendToChannel(botChannel)
            time.sleep(0.1)
    
    #await botChannel.send("Loaded Assets, Ready to rule!")
    #await botChannel.send("Command Count: " + str(len(jobs)))


##### ON READY #####
@client.event
async def on_ready():
    global lastMessagingUser
    global botChannel
    global commandChannel
    
    lastMessagingUser = client.get_user(BOT_USER_ID)
    print("lastMessagingUser.name : ",lastMessagingUser.name)
    
    botChannel = client.get_channel(BOT_CHANNEL_ID)
    print('just assigned botChannel, type is:',type(botChannel))
    commandChannel = client.get_channel(COMMAND_CHANNEL_ID)
    
    print("we have logged in as {0.user}".format(client))
    await reload()    
    print("ready")


#####   ON TYPING   #####
@client.event
async def on_typing(channel, user, when):
    print("     -     ",user,"is typing in",channel,"at",when)

#####   ON JOIN DM   #####
@client.event
async def on_member_join(member):
    if member.dm_channel == None:
        channel = await member.create_dm()
    else:
        channel = member.dm_channel
    await channel.send("HALLO! If you receive this message, well it means you arrived while someone was testing me. No problem though, have fun!")

##### ON MESSAGE #####
@client.event
async def on_message(message):
    global lastMessagingUser
    global jobs
    
    lastMessagingUser = message.author
    print("{1} : {0.channel} : {0.author.name}:  {0.content}".format(message,datetime.now().strftime("%H-%M-%S")))
    if(message.author == client.user):
        return # ignore bot's messages
    
    elif(message.content.startswith(COMMAND_PREFIX + "hello")):
        await message.channel.send("yo yo yooo, hi there {0.author.name}".format(message))
    elif(message.content.startswith(COMMAND_PREFIX + "reload")):

        print("reload")
        loaded = False
        print("we have logged in as {0.user}".format(client))
        await reload()
    elif(message.content.startswith(COMMAND_PREFIX + "commandMe")):
        await sendCommand()
    elif(message.content.startswith(COMMAND_PREFIX + "linkChannel")):
        if(message.content.split(' ')[1] == "bot"):
            botChannel = message.channel
            await botChannel.send("Linked botChannel to " + str(message.channel))
        elif(message.content.split(' ')[1] == "commands"):
            commandChannel = message.channel
            await commandChannel.send("Linked CommandChannel to " + str(message.channel))
    elif(message.content.startswith(COMMAND_PREFIX + "commandCount")):
        await reload()
    elif(message.content.startswith(COMMAND_PREFIX + "addCommand")):
        if message.author.id in ELEVATED_MEMBERS:
            args = message.content.split(" ")[1:]
            if args[0].isdecimal():
                jobs.append(Command(" ".join(args[1:]), int(args[0]), 0))
                saveCommands(jobs, ORDER_FILE)
                text = "Yay a new command!"
                embed = None
            else:
                text = None
                embed = discord.Embed(colour=discord.Colour.red())
                embed.add_field(name="Error", value="The first value needs to be the command's weight. In other words, a number.")
        await message.channel.send(content = text, embed = embed)
#############################################OLD CODE##############################################
#        print("getting old jobs")
#        with open(orderFile, "r") as f:
#            jobs = f.readlines()
#            # you may also want to remove whitespace characters like `\n` at the end of each line
#            jobs = [x.strip("\n") for x in jobs] 
#            f.close()
#        print("got old jobs")
#        
#        with open(orderFile, "a") as f:
#            newCommand = message.content.split(" ", 0)
#            print("Sanitizing Command")
#            print(newCommand)
#
#            newCommand = newCommand[(len(newCommand)-1)]
#            print("newCommand = newCommand[(len(newCommand)-1)]")
#            print(newCommand)
#
#            prefix = "$addCommand"
#            print("before removing prefix")
#            print(newCommand)
#            newCommand = newCommand.split(" ", 1)
#            newCommand = newCommand[1]
#            print("after removing prefix")
#            print(newCommand)
#            print("command Data Sanitation Complete")
#            f.write(str("\n" + str(newCommand)))
#            f.close()
#            await reload()
#            await message.channel.send(str("Added Command \"") + str(newCommand) + str("\""))
####################################################################################################

    elif(message.content.startswith(COMMAND_PREFIX + "listCommands")):
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
    elif(message.content.startswith(COMMAND_PREFIX + "clearCommands")):  
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
    elif(message.content.startswith(COMMAND_PREFIX + "config")):
        sanTemp = message.content.split(' ')
        COMMAND_TIME_RANGE_MIN = int(sanTemp[1])
        COMMAND_TIME_RANGE_MAX = int(sanTemp[2])
        await message.channel.send("Set COMMAND_TIME_RANGE_MIN to {0}, COMMAND_TIME_RANGE_MAX to {1}".format(int(sanTemp[1]),int(sanTemp[2])))
        print(str(COMMAND_TIME_RANGE_MIN) + " - " + str(COMMAND_TIME_RANGE_MAX))

    elif(message.content.startswith(COMMAND_PREFIX + "startLoop")):
        timedDrop = client.loop.create_task(sendCommand())
        await message.channel.send("Starting Semi-Randomly Timed Dropping of Commands")
    
    # elif(message.content.startswith(COMMAND_PREFIX + "stopLoop")):
        
    #     # timedDrop.cancel()
    #     await message.channel.send("Stopped Semi-Randomly Timed Dropping of Commands")
    #     await message.channel.send("didn't actually, this is broken atm, @ emily so she can turn it off manually")

    elif(message.content.startswith(COMMAND_PREFIX + "goodbye")):
        if message.author.id in ELEVATED_MEMBERS:
            saveCommands(jobs, ORDER_FILE)
            await client.close()
        else:
            message.channel.send("Error: Incorrect Password, Admins Only...")

    elif(message.content.startswith(COMMAND_PREFIX + "")):
        print("unknown command")
        await message.channel.send("Unknown BotCommand!")

@client.event
async def on_reaction_add(reaction, user):
    print(user.name + ": added reaction " + reaction.emoji + " to message " + reaction.message)


jobs = jsonReload()
orderFile = "orders.txt"
lastMessagingUser = None
botChannel = None
commandChannel = None

fd = open(path+"private/token.txt")
token = fd.readlines()[0]
print(token)
fd.close()
client.run(token)

print(weightedChoice(jobs))    

# selectCommand(jobs)

#timedDrop = client.loop.create_task(sendCommand())

