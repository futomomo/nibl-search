#!/usr/bin/env py -2
import urllib
import json
import hexchat

lastSearch = []
botList = {}

__module_name__ = 'NIBL XDCC Search'
__module_version__ = '1.0'
__module_description__ = 'Searches NIBL bots for the query and returns results, for easy searching.'

tabName = '(NIBL-Search)'
channelName = '#nibl'
helpUsage = '''Usage: NIBL search <search query>
       NIBL get <index>
'''

class AppURLopener(urllib.FancyURLopener):
    version = 'nibl-search/1.0'

urllib._urlopener = AppURLopener()

def updateBotList():
    global botList
    botUrl = 'https://api.nibl.co.uk/nibl/bots'
    stringResult = ''
    try:
        fileObj = urllib.urlopen(finalUrl)
        # print('The HTTP status code was: ' + str(fileObj.getcode()))
        if fileObj.getcode() != 200:
            fileObj.close()
            return
        for lines in fileObj.readlines():
            if len(lines) == 0:
                print('Empty response')
                fileObj.close()
                return
            else:
                for line in lines:
                    stringResult += line
        fileObj.close()
    except IOError:
        print('IOError: unable to make a connection to url')
        return
    jsonResult = json.loads(stringResult)['content']
    for bot in jsonResult:
        botList[str(bot['id'])] = bot['name']
    return

def search(word, word_eol, userdata):
    global lastSearch
    global botList
    baseUrl = 'https://api.nibl.co.uk/nibl/search?query='
    searchQuery = word_eol[2]
    safeQuery = urllib.quote_plus(searchQuery)
    finalUrl = baseUrl+safeQuery
    # print('Final url: ' + finalUrl)
    stringResult = ''
    # print('Opening \'' +  finalUrl + '\'')
    urllib.urlcleanup()
    try:
        fileObj = urllib.urlopen(finalUrl)
        # print('The HTTP status code was: ' + str(fileObj.getcode()))
        if fileObj.getcode() != 200:
            fileObj.close()
            return
        for lines in fileObj.readlines():
            if len(lines) == 0:
                print('Empty response')
                fileObj.close()
                return
            else:
                for line in lines:
                    stringResult += line
        fileObj.close()
    except IOError:
        print('IOError: unable to make a connection to url')
        return
    jsonResult = json.loads(stringResult)['content']
    lastSearch = jsonResult[:]
    tabContext = hexchat.find_context(channel=tabName)
    if tabContext is None:
        hexchat.command('QUERY {}'.format(tabName))
        tabContext = hexchat.find_context(channel=tabName)

    tabContext.emit_print('Generic Message', 'SEARCH', 'Query \'' + searchQuery + '\'\nFound ' + str(len(jsonResult)) + ' results')
    outString = ''
    for i,item in enumerate(jsonResult):
        itemString = '{}. \035\00307{}\017 \002----\017 \00311/msg {} xdcc send {}\017\n'.format(i+1, item['name'], botList[str(item['botId'])], item['number'])
        if len(outString) + len(itemString) > 2000:
            tabContext.emit_print('Generic Message', '', outString.rstrip())
            outString = itemString
        else:
            outString += itemString
    if len(resultString) > 0:
        tabContext.emit_print('Generic Message', '', outString.rstrip())
    return

def download(word, word_eol, userdata):
    global lastSearch
    tabContext = hexchat.find_context(channel=tabName)
    if tabContext is None:
        hexchat.command('QUERY {}'.format(tabName))
        tabContext = hexchat.find_context(channel=tabName)
    if len(lastSearch) == 0:
        tabContext.emit_print('Generic Message', 'GET', '\002\00304ERROR: Last search result is empty, please make a search with results over 0 first!\017')
        return
    indexToGet = 0
    try:
        indexToGet = int(word[2])-1
    except ValueError:
        tabContext.emit_print('Generic Message', 'GET', '\002\00304ERROR: Download index is not a number.\017')
        return
    if indexToGet >= len(lastSearch):
        tabContext.emit_print('Generic Message', 'GET', '\002\00304ERROR: Download index is out of range.\017')
        return
    itemToGet = lastSearch[indexToGet]
    commandString = 'MSG {} xdcc send {}'.format(botList[str(itemToGet['botId'])], itemToGet['number'])
    tabContext.emit_print('Generic Message', 'GET', 'GETting \035\00307{}\017'.format(itemToGet['name']))
    tabContext.command(commandString)
    return

def main(word, word_eol, userdata):
    if len(word) < 3:
        print('ERROR: Incorrect amount of arguments.')
    elif word[1] == 'search':
        search(word, word_eol, userdata)
    elif word[1] == 'get':
        download(word, word_eol, userdata)
    return hexchat.EAT_ALL

updateBotList()

hexchat.hook_command('NIBL', main, help=helpUsage)
