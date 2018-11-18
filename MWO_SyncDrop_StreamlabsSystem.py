#---------------------------------------
# Import Libraries
#---------------------------------------
import sys
import os
import codecs
import clr
import time
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#---------------------------------------
# Script Information
#---------------------------------------
ScriptName = "Sync-Drop Countdown Script"
Website = "https://www.dimensionv.de, https://www.twitch.tv/surn"
Description = "Initiates a countdown on chat for sync-dropping, using the !syncdrop command"
Creator = "Karubian"
Contributor = "Surn"
Version = "1.4"
"""
1.4 integrated with Castor Lazy Pack to allow the addition of a video upon sync drop
    to implement use castors latest lazy pack 1.4 or above overlay 
	if you do not have that installed, we included:
	index.html, client.js and API_Key.js is required
	you right click the script in chatbot scripts window - this creates API_KEY.js
"""
#---------------------------------------
# Set Variables
#---------------------------------------
command = "!syncdrop"
HELP = "help?"
commandPermission = "caster"
commandInfo = "Initiates a sync-drop countdown for MWO"

launchText = "CLICK!"
countDownTime = 5
useNA = True
useEU = True
useOC = True

useSubMode = True

effectiveLaunchText = launchText
effectiveTime = countDownTime
effectiveUseNA = useNA
effectiveUseEU = useEU
effectiveUseOC = useOC

coolDownTime = countDownTime * 10

useBoth = True
isFromTwitch = True
isFromDiscord = True

showHelpAndQuit = False

#---------------------------------------
# Intialize Data (Only called on Load)
#---------------------------------------
def Init():
    loadSettingsFile(__file__, filename='settings.json')
    return
 
#---------------------------------------
# Execute Data / Process Messages
#---------------------------------------
def Execute(data):
    global isFromTwitch
    global isFromDiscord

    if (data.IsChatMessage()):
        if (checkPermissionToRun(data)):
            if(not useBoth):
                isFromTwitch = data.IsFromTwitch()
                isFromDiscord = data.IsFromDiscord()
            else:
                isFromTwitch = useBoth
                isFromDiscord = useBoth
            parseParameters(data)
            if(showHelpAndQuit):
                showHelp()
            else:
                runCountDown(effectiveTime, effectiveUseEU, effectiveUseNA, effectiveUseOC)
    return
 
#---------------------------------------
# [Required] Tick Function
#---------------------------------------
def Tick():
    return
	
#---------------------------------------
# Load the settings from JSON
#---------------------------------------
def ReloadSettings(jsonData):
    global launchText
    global useSubMode
    global useBoth
    global countDownTime
    global useNA
    global useEU
    global useOC
    global coolDownTime

    Parent.Log(ScriptName, "Reloading settings")

    parsedData = json.loads(jsonData)

    if("launchText" in parsedData):
      launchText = parsedData["launchText"]
    if("useSubMode" in parsedData):
      useSubMode = parsedData["useSubMode"]
    if("useBoth" in parsedData):
      useBoth = parsedData["useBoth"]
    if("countDownTime" in parsedData):
      countDownTime = int(parsedData["countDownTime"])
    if("useNA" in parsedData):
      useNA = parsedData["useNA"]
    if("useEU" in parsedData):
      useEU = parsedData["useEU"]
    if("useOC" in parsedData):
      useOC = parsedData["useOC"]

    coolDownTime = countDownTime * 10

    Parent.Log(ScriptName, "Reloading finished")
    return

def parseParameters(data):
    global effectiveTime
    global effectiveUseNA
    global effectiveUseEU
    global effectiveUseOC
    global showHelpAndQuit

    paramCount = data.GetParamCount()

    if(paramCount < 2):
        effectiveTime = countDownTime
        effectiveUseNA = useNA
        effectiveUseEU = useEU
        effectiveUseOC = useOC
    elif(paramCount == 2):
        if(data.GetParam(1) in HELP):
            showHelpAndQuit = True
            return
        effectiveTime = int(data.GetParam(1))
        effectiveUseNA = useNA
        effectiveUseEU = useEU
        effectiveUseOC = useOC
    elif(paramCount == 3):
        effectiveTime = int(data.GetParam(1))
        useRegions = data.GetParam(2)
        effectiveUseNA = "NA" in useRegions
        effectiveUseEU = "EU" in useRegions
        effectiveUseOC = "OC" in useRegions

    return

def checkPermissionToRun(data):
    result = data.GetParam(0).lower() == command
    result = result and not Parent.IsOnCooldown(ScriptName, command)
    result = result and Parent.HasPermission(data.User, commandPermission, commandInfo)
    return result
 
def runCountDown(count, includeEU, includeNA, includeOC):
    if(useSubMode and isFromTwitch):
        Parent.SendTwitchMessage("/subscribers")
		
    sendMessage("Initiating sync-drop with the following regions included:")

    includedRegions = ""

    if(includeNA):
        includedRegions = addRegion("North America", includedRegions)
    if(includeEU):
        includedRegions = addRegion("Europe", includedRegions)
    if(includeOC):
        includedRegions = addRegion("Oceanic", includedRegions)

    sendMessage(includedRegions)

    sendMessage("Sync drop starts in:")

    f = {"link": "q_b5Rl0JvG8", "start": 965, "duration": 17500}
    Parent.BroadcastWsEvent("EVENT_YUT", json.dumps(f, encoding='utf-8-sig'))
    for step in range(count, 0, -1):
        sendMessage("  %d" % (step))
        time.sleep(1.0)

    sendMessage(launchText)
    
    if(useSubMode and isFromTwitch):
       Parent.SendTwitchMessage("/subscribersoff")
    
    return

def addRegion(region, regions):
    if(regions != "" ):
        regions += ", "
    regions += region
    return regions

def showHelp():
    sendMessage("!syncdrop [<countDownTime>|<countDownTime> <regions>]")
    sendMessage("countDownTime: time for the countdown in seconds")
    sendMessage("regions: selected regions. Can be any combination of EU, NA or OC")
    sendMessage("         Use the following syntax: EU, EU|NA or EU|NA|OC in any combination/order.")
    return

def sendMessage(message):
    if(isFromTwitch):
        Parent.SendTwitchMessage(message)

    if(isFromDiscord):
        Parent.SendDiscordMessage(message)

    Parent.Log(ScriptName, message)
    return

def loadSettingsFile(base, filename):
    try:
        with codecs.open(os.path.join(os.path.dirname(base), filename), encoding='utf-8-sig') as jsonData:
            ReloadSettings(jsonData.read())
            return
    except Exception as e:
        Parent.Log(ScriptName, "Error loading %s: %s" % (filename, str(e)))
        return
