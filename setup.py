#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#EMOJI from emoji import emojize
import config
import telebot
from telebot import types
import sys, time
import pickle

bot = telebot.TeleBot(config.token)

users = {}
teams = []

week = ['Monday', 'Tuesday', 'Wednesday',
        'Thursday', 'Friday']

user = None
#message ID -> will be assigned after recieving first message

def updateContact(name):
    global user
    user = users[name]    

class Day:

    def LessonsGenerator(self):
        for i in range(9, 19):
            zero = '0'
            if( i >= 10 ):
                zero = ''
            self.lessons.append((zero + str(i) + '-' + str(i + 1),zero + str(i) + '-' + str(i + 1)))
            self.binaryTable.append(1)

    def createKeyboardTimetable(self,day):
        keyboardLessons = types.InlineKeyboardMarkup(row_width = 5)
        LessonButtons = [types.InlineKeyboardButton(text = c[1], callback_data = day+','+c[0]) for c in self.lessons]
        keyboardLessons.add(*LessonButtons)
        
        return keyboardLessons

    def createTable(self,day):
        keyboardLessons = types.InlineKeyboardMarkup(row_width = 5)
        LessonButtons = [types.InlineKeyboardButton(text = c[1], callback_data = day+','+c[0]) for c in self.lessons]
        keyboardLessons.add(*LessonButtons)
        NavigationButtons = [
            types.InlineKeyboardButton(text = 'Previous', callback_data = 'Previous'+day),
            types.InlineKeyboardButton(text = day, callback_data = 'dayx'),
            types.InlineKeyboardButton(text = 'Next', callback_data = 'Next'+day)
        ]
        keyboardLessons.add(*NavigationButtons)
        return keyboardLessons

    def __init__(self, day, curUser,  notsend = False):
        #self = you.table
        self.lessons = []
        self.binaryTable = []
        self.LessonsGenerator()
        self.kb = self.createKeyboardTimetable(day)
        self.kb2 = self.createTable(day)
        self.curUser = curUser
        if notsend == True:
            bot.send_message(self.curUser.mesID, 'your timetable for ' + day , reply_markup = self.kb2)
    
    def update(self,text, day):
        #EMOJI emoji = emojize(":spiral_calendar:", use_aliases=True)
        for i in range(0,len(self.lessons)):
            if text == self.lessons[i][0]:
                if self.binaryTable[i] == 1:
                    print('Marina')
                    #EMOJI self.lessons[i] = (self.lessons[i][0],emoji)
                    self.lessons[i] = (self.lessons[i][0],'*')
                    print(self.lessons[i])
                    self.binaryTable[i] = 0
                else:
                    z = '0'
                    if( i!=0 ):
                        z = ''
                    self.lessons[i] = (self.lessons[i][0],self.lessons[i][0])
                    self.binaryTable[i] = 1
                break 
        self.kb2 = self.createTable(day)

class Timetable:
    
    week = ['Monday', 'Tuesday', 'Wednesday',
        'Thursday', 'Friday']

    def __init__(self, curUser):
        #self = you.table
        self.curUser = curUser
        self.days = {}
        for day in self.week:
            if day == 'Monday':
                self.days[day] = Day(day, self.curUser, True)
            else:
                self.days[day] = Day(day, self.curUser)
    
    def update(self):
        day = 'Monday'
        bot.send_message(self.curUser.mesID, 'Update your timetable for ' + day , reply_markup = self.days[day].kb2)

class Team:

    weekDays = ['Monday', 'Tuesday', 'Wednesday',
        'Thursday', 'Friday']

    def WholeWeek(self,messageID):
        ans = {}
        FreeTimeText = '' #just to send free time as a text
        for i in users[self.members[0]].table.week:
            ans[i] = []
            for j in range(0, 10):
                ans[i].append(1)

        for day in users[self.members[0]].table.week:
            
            FreeTimeTextDay = day + ' :\n'

            for j in self.members:
                j = users[j]
                print(j.username, j.table.days[day].binaryTable)
                for x in range(0, 10):
                    if (ans[day][x] == 1 and ans[day][x] == j.table.days[day].binaryTable[x]) :
                        ans[day][x] = 1
                    else:
                        ans[day][x] = 0

            curDay = Day(day,self.curUser, False)
            startTime = '*'

            anyFreeTime = False

            for i in range(0,10):
                curDay.binaryTable[i] = ans[day][i]
                if curDay.binaryTable[i] == 0:
                    if( startTime != '*' ):
                        FreeTimeTextDay += 'free from ' + startTime + ' to ' + curDay.lessons[i][0][0:2] + '\n'
                        startTime = '*'
                        anyFreeTime = True
                else:
                    if startTime == '*':
                        startTime = curDay.lessons[i][0][0:2]

            if( startTime != '*' ):
                    FreeTimeTextDay += 'free from ' + startTime + ' to ' + '19' + '\n'
                    startTime = '*'
                    anyFreeTime = True
            if anyFreeTime:
                FreeTimeText += FreeTimeTextDay + '\n' 

            curDay.kb = curDay.createKeyboardTimetable(day)
            #bot.send_message(self.curUser.mesID, 'your timetable for ' + day , reply_markup = curDay.kb)
        bot.send_message(messageID, FreeTimeText)
        
    def DayTime(self, messageID, username, Data):
        
        freeMembers = 'Availabe users: \n'

        day = Data[0]
        time = Data[1].split('-')

        day = day[0].upper() + day[1:]

        if day not in self.weekDays:
            bot.send_message(messageID, "Error, write again without mistakes!")
            users[username].DayTime = 1
            return

        for j in self.members:
            j = users[j]
            free = True
            print(j.username, j.table.days[day].binaryTable)
            for x in range(int(time[0])-9, int(time[1])-9):
                if (j.table.days[day].binaryTable[x] == 0) :
                    free = False
                    break
            if free:
                freeMembers += j.username + '\n'
                 
        numMembers = len(self.members)
        AvailabeUsers = freeMembers.count('\n') - 1
        freeMembers += str(AvailabeUsers) + " from " + str(numMembers) + ' (' + str( 100*AvailabeUsers/numMembers ) + "%)"
        #bot.send_message(self.curUser.mesID, 'your timetable for ' + day , reply_markup = curDay.kb)
        bot.send_message(messageID, freeMembers)
 
    def FreeTime(self,messageID):

        keyboardVariant = types.InlineKeyboardMarkup(row_width = 1)
        Buttons = [ 
            types.InlineKeyboardButton(text = 'Whole Week', callback_data = 'whole'),
            types.InlineKeyboardButton(text = 'Day and Time', callback_data = 'daytime') 
            ]
        keyboardVariant.add(*Buttons)
        bot.send_message(messageID,text = 'Choose',reply_markup = keyboardVariant)

    def __init__(self,curUser):
        self.name = ''
        self.members = []
        self.curUser = curUser
    # def add and del members

class User:

    def __init__(self,mesID, username):
        self.mesID = mesID
        self.table = None
        self.friends = []
        self.groups = []
        self.username = username
        self.cntFriend = 0
        self.cntTeam = 0
        self.cntTeamToJoin = 0
        self.chGroup = -1
        self.DayTime = 0
        users[username] = self
        updateDB()
    
    def zeroCnts(self):
        self.cntFriend = 0
        self.cntTeam = 0
        self.cntTeamToJoin = 0
        self.DayTime = 0

    def createTimeTable(self):
        self.table = Timetable(self)

    def show(self,msg):
        kb = types.ReplyKeyboardMarkup(row_width = 2,resize_keyboard = True, one_time_keyboard=False)
        btn =[ types.KeyboardButton('Update Timetable'),
        types.KeyboardButton('Create Team'),
        types.KeyboardButton('Free Time'),
        types.KeyboardButton('Join Group')
        ]
        #btn = types.KeyboardButton("?")
        kb.add(*btn)
        #bot.reply_to(self.mesID,'text', parse_mode='markdown', reply_markup = kb)
        bot.send_message(self.mesID,'Menu', reply_markup=kb)
  
    def update(self):
        self.table.update()

    def showFriends(self):
        kb = types.InlineKeyboardMarkup(row_width = 4)
        btn = []
        print(len(self.friends))
        for x in range(0, len(self.friends)):
            btn.append(types.InlineKeyboardButton(text = self.friends[x].username, callback_data = 'x'))
        kb.add(*btn)
        bot.send_message(self.mesID, 'Your Friends' , reply_markup = kb)

    def addFriend(self):
        bot.send_message(self.mesID, 'What is name of your Friend!')
        global cntFriend 
        cntFriend = 1

    def createGroup(self):
        bot.send_message(self.mesID, 'Create name for group')
        curGroup = Team(self)
        curGroup.members.append(self.username)
        teams.append( curGroup )
        self.groups.append( len(teams)-1 )
        
        self.cntTeam = 1
        kb = types.InlineKeyboardMarkup(row_width = 4)
        btn = []
        for x in range(0, len(self.friends)):
            btn.append(types.InlineKeyboardButton(text = self.friends[x].username, callback_data = 'FriendChosen'+','+self.friends[x].username))
        kb.add(*btn)
        bot.send_message(self.mesID, 'Your Friends' , reply_markup = kb)
    
    def JoinGroup(self):
        self.cntTeamToJoin = 1

        bot.send_message(self.mesID, 'Enter name of the group')

    def showGroup(self,name):
        kb = types.InlineKeyboardMarkup(row_width = 4)
        btn = []
        print(len(self.groups))
        for x in self.groups:
            if teams[x].name == name:
                curgroup = x
                break
        for x in curgroup.members:
            btn.append(types.InlineKeyboardButton(text =x.username, callback_data = x.username))
        kb.add(*btn)
        bot.send_message(self.mesID, 'Members of {} group'.format(curgroup.name) , reply_markup = kb)

    def FreeTime(self):
        kb = types.InlineKeyboardMarkup(row_width = 4)
        btn = []
        print(len(self.groups))
        for x in self.groups:
            btn.append(types.InlineKeyboardButton(text = teams[x].name, callback_data = 'ChosenGroup' + ',' + teams[x].name))
        kb.add(*btn)
        bot.send_message(self.mesID, 'List of groups' , reply_markup = kb)

def openDB():
    global users,teams
    usersFile = open("users.pickle","rb")
    users = pickle.load(usersFile)
    usersFile.close()
    teamsFile = open("teams.pickle","rb")
    teams = pickle.load(teamsFile)
    teamsFile.close()

def zeroDB():
    usersFile = open("users.pickle","wb")
    pickle.dump({},usersFile)
    usersFile.close()
    teamsFile = open("teams.pickle","wb")
    pickle.dump([],teamsFile)
    teamsFile.close()

def updateDB():
    global users,teams
    usersFile = open("users.pickle","wb")
    pickle.dump(users,usersFile)
    usersFile.close()
    teamsFile = open("teams.pickle","wb")
    pickle.dump(teams,teamsFile)
    teamsFile.close()

@bot.message_handler(commands=['start'])
def start(message):
    global user

    #zeroDB()
    openDB()
    if message.chat.username not in users:
        bot.send_message(message.chat.id, 'Signing up new User')
        user = User(message.chat.id, message.chat.username)
        users[message.chat.username].createTimeTable()
    else:
        user = users[message.chat.username]

    #print(*users[message.chat.username].table.days['Monday'].binaryTable)

    updateDB()
    users[message.chat.username].show(message)

@bot.callback_query_handler(func = lambda x: True)
def callback_handler(call):
    #global user

    #updateContact(call.message.chat.username)
    
    if call.message.chat.username not in users:
        start(call.message)
    
    if users[call.message.chat.username] == None:
        bot.answer_callback_query(call.id, text='Please, write down /start')
    else:
        print(call.data)
        if 'FriendChosen' in call.data:
            a = call.data.split(',')
            users[call.message.chat.username].groups[len(users[call.message.chat.username].groups)-1].members.append( users[a[1]] )
            
            updateDB()
        elif 'ChosenGroup' in call.data:
            a = call.data.split(',')
            for i in users[call.message.chat.username].groups:
                if teams[i].name == a[1]:
                    curgroup = teams[i]
                    users[call.message.chat.username].chGroup = i
                    break
            curgroup.FreeTime(users[call.message.chat.username].mesID)

            updateDB()
        elif 'whole' in call.data:
            teams[users[call.message.chat.username].chGroup].WholeWeek(users[call.message.chat.username].mesID)
        elif 'daytime' in call.data:
            users[call.message.chat.username].DayTime = 1
            bot.send_message(users[call.message.chat.username].mesID,'Enter day and time range')
        elif 'Previous' in call.data:
            day = call.data[8:]
            ind = week.index(day)
            if( day == 'Monday' ):
                day = 'Friday'
            else:
                day = week[ind-1]
            bot.edit_message_text(text = 'Your timetable for ' + day,chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup = users[call.message.chat.username].table.days[day].kb2)
        elif 'Next' in call.data:
            day = call.data[4:]
            ind = week.index(day)
            if( day == 'Friday' ):
                day = 'Monday'
            else:
                day = week[ind+1]
            bot.edit_message_text(text = 'Your timetable for ' + day,chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup = users[call.message.chat.username].table.days[day].kb2)
        elif 'dayx' in call.data:
            pass
        else:
            print('kkk')
            arr = call.data.split(',')
            day = arr[0]
            text = arr[1]

            print(text, day)
            users[call.message.chat.username].table.days[day].update(text, day)
            bot.edit_message_text(text = 'Your timetable for ' + day,chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup = users[call.message.chat.username].table.days[day].kb2)
    
            updateDB()

    updateDB()

@bot.message_handler(content_types=['text'])
def handling(message):

   # updateContact(message.chat.username)

    if message.chat.username not in users:
        start(message)
    
    if message.text == 'Update Timetable':
        
        users[message.chat.username].zeroCnts()
        users[message.chat.username].update()
        
        updateDB()
    elif message.text == 'friend':
        users[message.chat.username].zeroCnts()
        users[message.chat.username].addFriend()
                
        updateDB()
    elif message.text == 'Free Time':
        users[message.chat.username].zeroCnts()
        users[message.chat.username].FreeTime()
    elif message.text == 'Create Team':
        users[message.chat.username].zeroCnts()
        users[message.chat.username].createGroup()

        updateDB()
    elif message.text == 'Join Group':
        users[message.chat.username].zeroCnts()
        users[message.chat.username].JoinGroup()

        updateDB()

    elif users[message.chat.username].cntFriend != 0:
        nickname = message.text
        if nickname in users:
            users[message.chat.username].friends.append(users[nickname])
            bot.send_message(users[message.chat.username].mesID, 'Yeah! {} is your Friend!'.format(nickname))
            users[message.chat.username].showFriends()
        else:
            bot.send_message(users[message.chat.username].mesID, 'Error! {} not found!'.format(nickname))
        users[message.chat.username].cntFriend = 0

    elif users[message.chat.username].cntTeam != 0:
        print(message.text)
        name = message.text
        users[message.chat.username].cntTeam = 0
        for group in teams:
            if group.name == name:
                bot.send_message(users[message.chat.username].mesID, 'Error! A group with this name already exists! Please, write another one ')
                users[message.chat.username].cntTeam = 1
                break
        if users[message.chat.username].cntTeam == 0:
            teams[len(teams)-1].name = name
            bot.send_message(users[message.chat.username].mesID, 'Yeah! Group has been created')
            
    elif users[message.chat.username].cntTeamToJoin != 0:
        name = message.text
        for group in teams:
            if group.name == name:
                indTeam = teams.index(group)
                teams[indTeam].members.append(users[message.chat.username].username)
                users[message.chat.username].groups.append(indTeam)
                updateDB()
                bot.send_message(users[message.chat.username].mesID, 'Yeah, You are the member of the group! Now you can choose suitable time for meeting')
                users[message.chat.username].cntTeamToJoin = 0
                break
        if users[message.chat.username].cntTeamToJoin == 1:
            bot.send_message(users[message.chat.username].mesID, 'Error! There is no group called {}. Try again'.format(name))

    elif users[message.chat.username].DayTime != 0:#Here !!!!!
        print('LOL')
        users[message.chat.username].DayTime = 0    
        text = message.text
        Data = text.split(' ')
        teams[users[message.chat.username].chGroup].DayTime(users[message.chat.username].mesID, message.chat.username, Data)   
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

if __name__ == '__main__':
    openDB()
    bot.polling(none_stop=True)
