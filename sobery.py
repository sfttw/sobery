#!/usr/bin/env python3
'''Sobery is a discord bot for tracking sobriety. '''

#################
# USER CONFIG   #
#################
token = 'YOUR TOKEN HERE'
#################
#END USER CONFIG#
#################

import discord, pickle
from datetime import date
from datetime import datetime
client = discord.Client()

def database():
	f = open('sobery.db', 'rb')
	db = pickle.load(f)
	f.close()
	return db

def update(db):
	f = open('sobery.db', 'wb')
	pickle.dump(db, f)
	f.close()


def addUser(user, start_time_of_sobriety):
	db = database()
	db[user] = start_time_of_sobriety
	update(db)

def days(user):
	db = database()
	days_sober = (datetime.now() - db[user]).days
	minutes_sober = int((datetime.now() - db[user]).total_seconds() / 60.0)
	sober_date = db[user].strftime("%m-%d-%Y")

	return sober_date, days_sober, minutes_sober

def remove(user):
	'''remove user from database'''
	db = database()
	del db[user]
	update(db)

if __name__ == '__main__':
	@client.event
	async def on_ready():
		print('Logged in as {0.user}'.format(client))
	
	@client.event
	async def on_message(message):
		botnick = str(client.user).split('#')[0] # who's messaging us?
		user = str(message.author) # who's messaging us?
		if message.author == client.user:
			return
		if client.user.mentioned_in(message):	
			if message.content.lower().split()[1] == 'hello':
				await message.channel.send('¡Hola, {}!'.format(message.author))
			
			if message.content.lower().split()[1] == 'whoami':
				await message.channel.send('I am {} AKA {}'.format(client.user, botnick))
			
			##################
			#### ECHO
			###################
			if message.content.lower().split()[1] == 'echo':
				await message.channel.send(str(message.content))
		
			if message.content.lower().split()[1] == 'set' or message.content.lower().split()[1] == '$reset':
				############################
				# add a user to the database
				#############################
				setdate = '' #
				
				if len(message.content.split()) == 2:
					start_time_of_sobriety = message.content.split()[2].replace('/', '-') + ' 00:00:00'
					start_time_of_sobriety = datetime.strptime(start_time_of_sobriety, '%Y-%m-%d %H:%M:%S')
				else:
					addUser(str(message.author), datetime.now())
				await message.channel.send('Sobriety date {} added for {}'.format(setdate, str(message.author).split('#')[0]))
				
	
			################
			# Time Sober
			################	
			if message.content.lower().split()[1] == 'time' or message.content.lower().split()[1] == 'info':
				try:
					sober_date, days_sober, minutes_sober = days(user)
					if int(days_sober) == 1:
						await message.channel.send('You are {} day sober. You have been sober since {}!'.format(days_sober, sober_date))
					else:
						await message.channel.send('You are {} days and {} minutes sober. You have been sober since {}!'.format(days_sober, minutes_sober, sober_date))
				except KeyError:
					await message.channel.send("I don't see you in the database, {}! Type: `$set` to be added.".format(user))
					print(KeyError)
	
				#################
				# remove the user from the database
				################	
			if message.content.lower().split()[1] == 'break' or message.content.lower().split()[1] == 'quit':
				try: 
					sober_date, days_sober = days(user)
					remove(user)
					await message.channel.send('Sorry to see you go, {}!'.format(user))
				except KeyError:
					await message.channel.send("I don't see you in the database, {}! Type: `$set` to be added.".format(user))
				
				###############
				# Help Message
				##############
			if message.content.lower().split()[1] == 'help':
				await message.channel.send('''Commands:
				`set [date]`  - begin tracking your sobriety. ex: `$set` or `$set 12/25/2020`
				`time` - show how long you've been sober
				`break` - stop tracking your sobriety / take a break.
				`help` - show this help message and exit'''.format(message.author))
				
	
	
	client.run(token)
