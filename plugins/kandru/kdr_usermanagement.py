from ts3tools import ts3tools
from Levenshtein import distance
import time
from copy import deepcopy

"""
    This little plugin manages users for our official
    kandru teamspeak (ts3.kandru.de). This is great for
    bigger communities with much channels because it provides
    a few great improvements to teamspeak.

    Done:
    - admin notification

    ToDo:
    - multilanguage
    - search users
    - join users channel
    - set yourself gaming groups
    - notification if user is online

    Dependencys:
    pip3 install python-Levenshtein
"""

# configuration

# list of admin groups
# scan interval (should not be less than 2 seconds)

# wait interval for next admin message (should not be less then 60 seconds)

# plugin name (must be unique!)
name = 'kdr_usermanagement'
base = None
db = None
config = None
core_TS3clients = None
core_TS3chat = None
core_TS3channel = None

# plugin variables
userlist = {}
channellist = {}
grouplist = {}
guestlist = {}
registerlist = {}
nextProof = 0
adminGroups = []
funcAdminOptions = {}
funcSearchOptions = {}

# initial method (called from ts3eventscripts)
def setup(ts3base):
    global base, core_TS3clients, core_TS3chat, core_TS3channel, db, config, funcSearchOptions, funcAdminOptions, adminGroups
    # get ts3base, it's needed for nearly everything
    base = ts3base
    # get db
    db = base.get_class('core.TS3db')
    # get core TS3clients
    core_TS3clients = base.get_class('core.TS3clients')
    core_TS3channel = base.get_class('core.TS3channel')
    core_TS3chat = base.get_class('core.TS3chat')
    # register callbacks
    base.register_callback(name, 'ts3.start', event_start)
    base.register_callback(name, 'ts3.loop', event_loop)
    base.register_callback(name, 'ts3.chat.cmd.admin', cmd_admin)
    base.register_callback(name, 'ts3.chat.cmd.s', cmd_search)
    base.register_callback(name, 'ts3.chat.cmd.yes', cmd_yes)
    base.register_callback(name, 'ts3.chat.cmd.group', cmd_group)
    base.register_callback(name, 'ts3.chat.cmd.register', cmd_register)
    base.register_callback(name, 'ts3.chat.cmd.test', cmd_test)
    base.register_callback(name, 'ts3.clientjoined', event_clientjoined)
    base.register_callback(name, 'ts3.clientleft', event_clientleft)
    # set help entries
    core_TS3chat.add_command_help('admin', 'notify all available admins', 'Contact all available admins via private chat. DO NOT USE ABUSE OR YOU WILL GET BANNED!')
    core_TS3chat.add_command_help('s', 'search an online user', 'Search your friend on our server. If he is only you will be able to see in what channel he is. Your friend will get notified that you have searched him :)')
    core_TS3chat.add_command_help('group', 'add or delete gaming groups from yourself', 'Type command without arguments to see all available gaming groups. Type [u]!group add ID[/u] to add yourself to this group. Type [u]!group del ID[/u] to remove yourself from this group.')
    core_TS3chat.add_command_help('register', 'register yourself on this server', 'you can register yourself on this server if you\'re online for at least one hour.')
    # get config
    config = ts3tools.get_instance_config(base, name)
    if config is None:
        config = ts3tools.get_global_config(name)
    # initialize plugin variables with configs
    funcAdminOptions = {'next': 0, 'interval': int(config['global']['reuseAdminCommand']), 'list': []}
    funcSearchOptions = {'next': 0, 'interval': int(config['global']['reuseSearchCommand']), 'doyoumean': {}, 'lastuse': []}
    adminGroups = config['funcAdmin']['adminGroups'].split(',')

def cmd_test(event):
    for key in channellist:
        print(key + ' - ' + channellist[key]['channel_name'])

def event_start(event):
    global userlist, channellist, grouplist, guestlist
    # create tables if neccessary
    db.create_table(
        name, [['instance', 'VARCHAR(255)'], ['uid', 'VARCHAR(30)'], ['dbid', 'INT'], ['clid', 'INT'], ['name', 'TEXT'], ['action', 'TEXT'], ['comment', 'TEXT'], ['timestamp', 'INT']], 'actionlog')
    # get user and channellist
    userlist = core_TS3clients.clientlist()
    channellist = core_TS3channel.channellist()
    grouplist = core_TS3clients.grouplist()
    # add guests to guestlist
    for key in userlist:
        if config['global']['guestGroupID'] in userlist[key]['client_servergroups'].split(','):
            guestlist[key] = time.time()
    # talk to every client
    # for key in userlist:
    #    msg = 'Hey '
    #    msg += userlist[key]['client_nickname']
    #    msg += ', I\'m the Server Bot and help you to have a nice stay on our server. To see all server commands type [u]!help[/u] in chat. If you have problems with other people just type [u]!admin[/u]. Abuse will result in permanent ban.'
    #    core_TS3chat.send_pm(base, userlist[key]['clid'], msg, True)

def event_loop(event):
    global nextProof, userlist, channellist, grouplist, funcAdminOptions
    if nextProof <= time.time():
        # get clientlist
        userlist = core_TS3clients.clientlist()
        # get channellist
        channellist = core_TS3channel.channellist()
        # get grouplist
        grouplist = core_TS3clients.grouplist()
        # update nextProof
        nextProof = time.time() + int(config['global']['scanInterval'])
        # check guest registration
        check_guest_registration()
    # garbage collection for func Admin
    if funcAdminOptions['next'] <= time.time():
        # reset list with users
        funcAdminOptions['list'] = []
        funcAdminOptions['next'] = time.time() + funcAdminOptions['interval']
    # garbage collection for func Search
    if funcSearchOptions['next'] <= time.time():
        # reset list with users
        funcSearchOptions['doyoumean'] = {}
        funcSearchOptions['lastuse'] = []
        funcSearchOptions['next'] = time.time() + funcSearchOptions['interval']

def event_clientjoined(event):
    global guestlist
    # sleep some seconds to give the userlist time to get user information
    time.sleep(10)
    if event['clid'] in userlist:
        if config['global']['guestGroupID'] in userlist[event['clid']]['client_servergroups'].split(','):
            guestlist[event['clid']] = time.time()

def event_clientleft(event):
    global guestlist, registerlist
    if event['clid'] in guestlist:
        del guestlist[event['clid']]
    if event['clid'] in registerlist:
        del registerlist[event['clid']]

def cmd_admin(event):
    global funcAdminOptions
    # list of admin names
    admins = []
    # comment from user
    comment = ''.join(event['args'])
    # create admin message
    msg = '\\n[b]Attention:[/b] [u][url=client://' + event['sender']['uid'] + ']'
    msg += event['sender']['name']
    msg += '[/url][/u] (' + event['sender']['uid'] + ') in Channel '
    msg += '[b][url=channelid://' + userlist[event['sender']['id']]['cid'] + ']' + channellist[userlist[event['sender']['id']]['cid']]['channel_name'] + '[/url][/b]'
    msg += ' requested help!\\n'
    if comment != '':
        msg += '\\n[b]Comment[/b]: ' + comment
    # if the user doesn't request admin help short time ago
    if event['sender']['uid'] not in funcAdminOptions['list']:
        # send to every user in admin groups
        for key in userlist:
            inList = False
            for group in userlist[key]['client_servergroups'].split(','):
                if group in adminGroups:
                    inList = True
            if inList:
                # add to admin list
                admins.append(userlist[key]['client_nickname'])
        send_msg_toadmins(msg)
        # send message to user what admins he could reach
        if admins:
            msg = '\\nPlease wait. You reached the admins: ' + ', '.join(map(str, admins))
            if comment != '':
                msg += '\\n[b]Your comment[/b]: ' + comment
            # add user to list because he shouldn't call admins twice
            funcAdminOptions['list'].append(event['sender']['uid'])
            # add log entry to db
            add_action(event['sender']['uid'], event['sender']['id'], event['sender']['clid'], event['sender']['name'], '!admin', msg)
        else:
            msg = 'Sorry :( , no Admins online. Please try again later ...'
    else:
        # send warn message to user
        msg = 'Sorry :( , you requested help short time ago. Please wait a few minutes!'
    core_TS3chat.send_pm(base, event['sender']['id'], msg, True)

def cmd_search(event):
    global funcSearchOptions
    if event['sender']['uid'] not in funcSearchOptions['lastuse']:
        tmp_userlist = {}
        tmp_username = None
        tmp_key = None
        input_username = ''.join(event['args']).lower()
        for key in userlist:
            dist = distance(input_username, userlist[key]['client_nickname'].lower())
            if dist == 0:
                tmp_username = userlist[key]['client_nickname']
                tmp_key = key
                break
            elif dist <= 5:
                tmp_userlist[key] = {'name': userlist[key]['client_nickname'], 'dist': dist}
        if tmp_username is not None:
            msg = '[b]' + tmp_username + '[/b]'
            msg += ' is in channel [b][url=channelid://' + userlist[tmp_key]['cid'] + ']' + channellist[userlist[tmp_key]['cid']]['channel_name'] + '[/url][/b]. He got a notification about your search.'
            # add user to list because he shouldn't search twice
            funcSearchOptions['lastuse'].append(event['sender']['uid'])
            if config['funcSearch']['notifySearchedUser'] == 'yes':
                # send information to use that someone searched for him
                umsg = 'Information: [b]' + event['sender']['name'] + '[/b] was looking for you with [u]!s ' + tmp_username + '[/u]. If it\'s a friend of yours, maybe you want to talk to him?'
                core_TS3chat.send_pm(base, userlist[tmp_key]['clid'], umsg, True)
            # log action
            add_action(event['sender']['uid'], event['sender']['id'], event['sender']['clid'], event['sender']['name'], '!s', msg)
        elif tmp_userlist:
            tmp_sort = sorted(tmp_userlist, key=lambda x: (tmp_userlist[x]['dist']))
            if tmp_sort[0] is not None:
                msg = 'did you mean [b]' + tmp_userlist[tmp_sort[0]]['name'] + '[/b]? Type !yes or search again.'
                funcSearchOptions['doyoumean'][event['sender']['uid']] = {'type': 'did_you_mean', 'key': tmp_sort[0], 'timestamp': str(time.time())}
        else:
            msg = 'Sorry, user not found :('
    else:
        # send warn message to user
        msg = 'Sorry :( , you requested the user search short time ago. Please wait a few minutes!'
    core_TS3chat.send_pm(base, event['sender']['id'], msg, True)

def cmd_yes(event):
    global funcSearchOptions
    if event['sender']['uid'] in funcSearchOptions['doyoumean']:
        if float(funcSearchOptions['doyoumean'][event['sender']['uid']]['timestamp']) >= (time.time() - 30):
            tmp_key = funcSearchOptions['doyoumean'][event['sender']['uid']]['key']
            msg = '[b]' + userlist[tmp_key]['client_nickname'] + '[/b]'
            msg += ' is in channel [b][url=channelid://' + userlist[tmp_key]['cid'] + ']' + channellist[userlist[tmp_key]['cid']]['channel_name'] + '[/url][/b].  He got a notification about your search.'
            # add user to list because he shouldn't search twice
            funcSearchOptions['lastuse'].append(event['sender']['uid'])
            core_TS3chat.send_pm(base, event['sender']['id'], msg, True)
            # log action
            add_action(event['sender']['uid'], event['sender']['id'], event['sender']['clid'], event['sender']['name'], '!s', msg)
            print(config['funcSearch']['notifySearchedUser'])
            if config['funcSearch']['notifySearchedUser'] == 'yes':
                # send information to use that someone searched for him
                umsg = 'Information: [b]' + event['sender']['name'] + '[/b] was looking for you with [u]!s ' + userlist[tmp_key]['client_nickname'] + '[/u]. If it\'s a friend of yours, maybe you want to talk to him?'
                core_TS3chat.send_pm(base, userlist[tmp_key]['clid'], umsg, True)

def cmd_group(event):
    if config['global']['guestGroupID'] not in userlist[event['sender']['id']]['client_servergroups'].split(','):
        # get all groups with specific sort id
        tmp_grouplist = {}
        for key in grouplist:
            if grouplist[key]['sortid'] == config['funcGroup']['groupSortID']:
                tmp_grouplist[key] = grouplist[key]['name']
        if len(event['args']) == 2:
            if event['args'][1] in tmp_grouplist:
                if event['args'][0] == 'add':
                    core_TS3clients.client_add_servergroup(event['args'][1], userlist[event['sender']['id']]['client_database_id'])
                elif event['args'][0] == 'del':
                    core_TS3clients.client_del_servergroup(event['args'][1], userlist[event['sender']['id']]['client_database_id'])
            else:
                msg = 'This group is not a gaming group. Don\'t try to cheat on me!'
                core_TS3chat.send_pm(base, event['sender']['id'], msg, True)
        else:
            msg = 'Available groups. Add group with [u]!group add ID[/u] or delete group with [u]!group del ID[/u].\\n'
            core_TS3chat.send_pm(base, event['sender']['id'], msg, True)
            for key in tmp_grouplist:
                msg += tmp_grouplist[key] + '\\n'
            count = len(tmp_grouplist)
            if count != 0:
                tmp_sorted = sorted(tmp_grouplist, key=lambda x: (tmp_grouplist[x]))
                for key in tmp_sorted:
                    msg = '    [color=blue]' + key + '[/color]' + ' - ' + tmp_grouplist[key] + '\\n'
                    core_TS3chat.send_pm(base, event['sender']['id'], msg, True)
            else:
                msg = 'No groups here yet. :-(\\n'
                core_TS3chat.send_pm(base, event['sender']['id'], msg, True)
    else:
        msg = 'You\'re a guest and can\'t use this command!'
        core_TS3chat.send_pm(base, event['sender']['id'], msg, True)

def cmd_register(event):
    global registerlist
    if config['global']['guestGroupID'] in userlist[event['sender']['id']]['client_servergroups'].split(','):
        if event['sender']['id'] in registerlist:
            core_TS3clients.client_add_servergroup(config['funcRegister']['registeredGroupID'], userlist[event['sender']['id']]['client_database_id'])
            msg = 'You\'ve successfully registered yourself on our teamspeak. Have fun and play fair!'
            add_action(event['sender']['uid'], event['sender']['id'], event['sender']['clid'], event['sender']['name'], '!register', msg)
            amsg = '[b]Information:[/b] [u][url=client://' + event['sender']['uid'] + ']'
            amsg += event['sender']['name']
            amsg += '[/url][/u] (' + event['sender']['uid'] + ') in Channel '
            amsg += '[b][url=channelid://' + userlist[event['sender']['id']]['cid'] + ']' + channellist[userlist[event['sender']['id']]['cid']]['channel_name'] + '[/url][/b]'
            amsg += ' registered himself! Please keep an eye on fresh registered newbies :)\n'
            send_msg_toadmins(amsg)
            # delete user from registerlist
            del registerlist[event['sender']['id']]
        else:
            msg = 'You can\'t register now because you have to spend more time on our teamspeak before registration.'
    else:
        msg = 'You\'re not a guest anymore and can\'t use this command!'
        if event['sender']['id'] in registerlist:
            del registerlist[event['sender']['id']]
    core_TS3chat.send_pm(base, event['sender']['id'], msg, True)

def send_msg_toadmins(msg):
    # send to every user in admin groups
        for key in userlist:
            inList = False
            for group in userlist[key]['client_servergroups'].split(','):
                if group in adminGroups:
                    inList = True
            if inList:
                # send message
                core_TS3chat.send_pm(base, userlist[key]['clid'], msg, True)

def check_guest_registration():
    global guestlist, registerlist
    tmp_guestlist = deepcopy(guestlist)
    for key in tmp_guestlist:
        if int(tmp_guestlist[key]) + (int(config['funcRegister']['timeToWaitBeforeRegistration'])*60) <= time.time():
            del guestlist[key]
            registerlist[key] = time.time()
            msg = 'Hey guest. If you wan\'t you can register yourself on our teamspeak server with [u]!register[/u]. After that you\'re able to give yourself gaming groups. More information with [u]!help group[/u].'
            core_TS3chat.send_pm(base, key, msg, True)

def add_action(uid, dbid, clid, clientname, action, comment):
    timestamp = str(time.time())
    db.query('INSERT INTO `' + db.get_table_name(name, 'actionlog') + '` (`instance`, `uid`, `dbid`, `clid`, `name`,`action`,`comment`,`timestamp`) VALUES ("' + base.identifier + '", "' + uid + '", "' + dbid + '", "' + clid + '", "' + clientname + '", "' + action + '", "' + comment + '", "' + timestamp + '");', wait=False)
