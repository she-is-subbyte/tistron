print("ALPHA")
import discord, time, random, asyncio, json, pprint, os, emojis
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

path = str(os.getcwd() + '\\')

class Command:
    def __init__(self, name, defaultWeight, weightOffset):
        self.name = name
        self.defaultWeight = defaultWeight
        self.weightOffset = weightOffset
        self.timer = 0
        self.text = None
    
    def __str__(self):
        return self.parse()
    
    # Parses the name, replacing various key strings with others.
    # {%random(x,y)} is replaced by a random number between x and y inclusive
    # {%timer(x,y,text) makes it so that when a timer comprised between x and y inclusive ends, text is sent.}
    
    def parse(self):
        print(self.name)
        commands = self.name.split("{")
        ret = ""
        for command in commands:
            if command.startswith("%random"):
                dice1 = command.split("(")[1].split(",")[0]
                dice2 = command.split("(")[1].split(",")[1].split(")")[0]
                print("random dice1:" + dice1 + " isdigit : " + str(dice1.isdigit()))
                print("random dice2:" + dice2 + " isdigit : " + str(dice2.isdigit()))
                if dice1.isdigit() and dice2.isdigit():
                    dice1 = int(dice1)
                    dice2 = int(dice2)
                    ret += str(random.randint(dice1, dice2)) 
                    if len(command.split("}")) > 1:
                        ret += "}".join(command.split("}")[1:])
            elif command.startswith("%timer"):
                self.text = ",".join(command.split("%timer(")[1].split(",")[2:]).split(")")[0]
                timerMin = command.split("%timer(")[1].split(",")[0]
                timerMax = command.split("%timer(")[1].split(",")[1]
                print("timer timer1:" + timerMin + " isdigit : " + str(timerMin.isdigit()))
                print("timer timer2:" + timerMax + " isdigit : " + str(timerMax.isdigit()))
                if timerMin.isdigit() and timerMax.isdigit():
                    timerMin = int(timerMin)
                    timerMax = int(timerMax)
                    self.timer = random.randint(timerMin, timerMax)
                    ret += str(self.timer)
                ret += "}".join(command.split("}")[1:])
            else:
                ret += ("{" if not self.name.startswith(command) else "") + command
        return ret
    
    async def sendToChannel(self, channel):
        await channel.send(self.parse())
        if self.timer != 0 and self.text != None:
            await asyncio.sleep(self.timer)
            await channel.send(self.text)
    
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

async def sendCommand(once = False):

    global jobs
    global lastMessagingUser
    global activate
    global lastMessageIsCommand

    print("comamndMe")
    orders = jobs
    print("orders = cycle(jobs)")
    print(client.is_closed())
    if not once:
        await commandChannel.send("Starting Semi-Randomly Timed Dropping of Commands")

    # while(client.is_closed()):
    while(not client.is_closed()):
        print("activate" + str(activate))
        print("lastMessageIsCommand" + str(lastMessageIsCommand))
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
            # if not lastMessageIsCommand and activate:
            if activate:
                print("await commandChannel.send(currentOrder)")
                await currentOrder.sendToChannel(commandChannel)
            else:
                print("last messagign user was the bot, skipping rollout so as not to spam")
        else:
            await commandChannel.send("Not enough commands in list! There must be at least 10, and there is currently {0} commands.".format(len(orders)))
        sleepRange = random.randrange(COMMAND_TIME_RANGE_MIN, COMMAND_TIME_RANGE_MAX)
        if once or not activate:
            break
        lastMessageIsCommand = False
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

def generate_emote_text(dic):
    content = ""
    for reaction in dic:
        if type(reaction) is int: # If the key is an ID of a custom emoji...
            emote = client.get_emoji(reaction)
            role = botChannel.guild.get_role(dic[reaction])
            content += str(emote) + " : " + role.name + "\n"
        else:
            role = botChannel.guild.get_role(dic[reaction])
            content += emojis.encode(reaction) + " : " + role.name + "\n"
    return content

async def generate_role_reactions(message, dic):
    for reaction in dic:
        if type(reaction) is int:
            emote = client.get_emoji(reaction)
            await message.add_reaction(emote)
        else:
            await message.add_reaction(emojis.encode(reaction))

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
    # If the role channels doesn't have any messages yet, create them.
    roleChannel = client.get_channel(ROLE_CHANNEL_ID)
    history = await roleChannel.history(limit=3).flatten()
    if len(history) == 0:
        await roleChannel.send("Heyyy all! Here in Tistron Hub, we use an automated system for role attribution! You just need to react using the corresponding emoji and if I'm available (I'm busy you know!), I'll add the role for you.\n\n**I REPEAT : IF I AM DISCONNECTED, THIS WILL NOT WORK. CHECK THE SIDEBAR TO SEE IF I'M CONNECTED OR NOT.**\n\nOr better yet, just say " + COMMAND_PREFIX + "hello and I'll confirm you I'm here! If you accidentaly react while I'm not here, no problem! Just remove the reaction, and set it again when I'm available!\n\nOf course, all of this is perfectly optionnal, it is just so we can get to know each other better, but don't feel obligated to add yourself any role you don't want to!")
        with open("constants.py", "a") as f:
            await asyncio.sleep(1)
            content = "**Gender**\n\nThis one is to add a role representing your gender(s).\n\n"
            content += generate_emote_text(ROLE_REACTIONS_GENDER)
            message = await roleChannel.send(content)
            f.write("\nROLE_GENDER_MESSAGE_ID = " + str(message.id) + "\n")
            await generate_role_reactions(message, ROLE_REACTIONS_GENDER)
            
            await asyncio.sleep(1)
            content = "**Pronouns**\n\nThese are the pronouns you want us to use for you! If you use multiple pronouns don't hesitate to add multiple roles\n\n*Small rule reminder : Misgendering on purpose is NOT OKAY.*\n\n"
            content += generate_emote_text(ROLE_REACTIONS_PRONOUNS)
            message = await roleChannel.send(content)
            f.write("\nROLE_PRONOUNS_MESSAGE_ID = " + str(message.id) + "\n")
            await generate_role_reactions(message, ROLE_REACTIONS_PRONOUNS)
            
            await asyncio.sleep(1)
            content = "**Localization**\n\nThis one has a more technical purpose, it's always useful to know someone's approximate timezone so we know wether it's night or work time for them.\n\n"
            content += generate_emote_text(ROLE_REACTIONS_LOCALIZATION)
            message = await roleChannel.send(content)
            f.write("\nROLE_LOCALIZATION_MESSAGE_ID = " + str(message.id) + "\n")
            await generate_role_reactions(message, ROLE_REACTIONS_LOCALIZATION)
            
            await asyncio.sleep(1)
            content = "**Hypnosis status**\n\nThis one has roles related to either the roles you want to play, or your experience with hypnosis\n\n"
            content += generate_emote_text(ROLE_REACTIONS_HYPNOSIS)
            message = await roleChannel.send(content)
            f.write("\nROLE_HYPNOSIS_MESSAGE_ID = " + str(message.id) + "\n")
            await generate_role_reactions(message, ROLE_REACTIONS_HYPNOSIS)
            
            await asyncio.sleep(1)
            content = "**DMs**\n\nDo you want others to know they can DM you whenever? Or that you'd rather not be spammed? Or only for roleplay maybe?\n\n"
            content += generate_emote_text(ROLE_REACTIONS_DMS)
            message = await roleChannel.send(content)
            f.write("\nROLE_DMS_MESSAGE_ID = " + str(message.id) + "\n")
            await generate_role_reactions(message, ROLE_REACTIONS_DMS)
            
            await asyncio.sleep(1)
            content = "**Relationship status**\n\nTell the world how desperately you need someone in your life, or how you have a partner (or multiple partners!) you love very very much!\n\n"
            content += generate_emote_text(ROLE_REACTIONS_RELATIONSHIPS)
            message = await roleChannel.send(content)
            f.write("\nROLE_RELATIONSHIP_MESSAGE_ID = " + str(message.id) + "\n")
            await generate_role_reactions(message, ROLE_REACTIONS_RELATIONSHIPS)
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
    global activate
    global lastMessageIsCommand
    
    lastMessagingUser = message.author
    lastMessageIsCommand = False
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
        await sendCommand(True)
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
        activate = True
        await sendCommand()
        
    
    elif(message.content.startswith(COMMAND_PREFIX + "stopLoop")):
        activate = False
        await message.channel.send("Stopped Semi-Randomly Timed Dropping of Commands")

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
    print(user.name + ": added reaction " + reaction.emoji + " to message " + reaction.message.content)

@client.event
async def on_raw_reaction_add(payload):
    reacManager = {ROLE_GENDER_MESSAGE_ID: ROLE_REACTIONS_GENDER, ROLE_PRONOUNS_MESSAGE_ID: ROLE_REACTIONS_PRONOUNS, ROLE_LOCALIZATION_MESSAGE_ID: ROLE_REACTIONS_LOCALIZATION, ROLE_HYPNOSIS_MESSAGE_ID: ROLE_REACTIONS_HYPNOSIS, ROLE_DMS_MESSAGE_ID: ROLE_REACTIONS_DMS, ROLE_RELATIONSHIP_MESSAGE_ID: ROLE_REACTIONS_RELATIONSHIPS}
    if payload.message_id in reacManager.keys():
        reactions = reacManager[payload.message_id]
        for emote in reactions:
            if type(emote) is int:
                if payload.emoji.id == emote:
                    sender = client.get_user(payload.user_id)
                    server = client.get_guild(payload.guild_id)
                    member = server.get_member(sender.id)
                    await member.add_roles(client.get_guild(payload.guild_id).get_role(reactions[emote]))
                    print("Added role " + client.get_guild(payload.guild_id).get_role(reactions[emote]).name)
            elif payload.emoji.name == emojis.encode(emote):
                sender = client.get_user(payload.user_id)
                server = client.get_guild(payload.guild_id)
                member = server.get_member(sender.id)
                await member.add_roles(client.get_guild(payload.guild_id).get_role(reactions[emote]))
                print("Added role " + client.get_guild(payload.guild_id).get_role(reactions[emote]).name)
  

@client.event
async def on_raw_reaction_remove(payload):
    reacManager = {ROLE_GENDER_MESSAGE_ID: ROLE_REACTIONS_GENDER, ROLE_PRONOUNS_MESSAGE_ID: ROLE_REACTIONS_PRONOUNS, ROLE_LOCALIZATION_MESSAGE_ID: ROLE_REACTIONS_LOCALIZATION, ROLE_HYPNOSIS_MESSAGE_ID: ROLE_REACTIONS_HYPNOSIS, ROLE_DMS_MESSAGE_ID: ROLE_REACTIONS_DMS, ROLE_RELATIONSHIP_MESSAGE_ID: ROLE_REACTIONS_RELATIONSHIPS}
    if payload.message_id in reacManager.keys():
        reactions = reacManager[payload.message_id]
        for emote in reactions:
            if type(emote) is int:
                if payload.emoji.id == emote:
                    sender = client.get_user(payload.user_id)
                    server = client.get_guild(payload.guild_id)
                    member = server.get_member(sender.id)
                    await member.remove_roles(client.get_guild(payload.guild_id).get_role(reactions[emote]))
                    print("Removed role " + client.get_guild(payload.guild_id).get_role(reactions[emote]).name)
            elif payload.emoji.name == emojis.encode(emote):
                sender = client.get_user(payload.user_id)
                server = client.get_guild(payload.guild_id)
                member = server.get_member(sender.id)
                await member.remove_roles(client.get_guild(payload.guild_id).get_role(reactions[emote]))
                print("Removed role " + client.get_guild(payload.guild_id).get_role(reactions[emote]).name)
  
jobs = jsonReload()
orderFile = "orders.txt"
lastMessagingUser = None
botChannel = None
commandChannel = None
activate = True
lastMessageIsCommand = False

fd = open(path+"private/token.txt")
token = fd.readlines()[0]
print(token)
fd.close()
client.run(token)

print(weightedChoice(jobs))