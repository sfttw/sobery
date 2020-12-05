#!/usr/bin/env python3
'''SAM is a discord bot for tracking sobriety. 
Named after Sam from the TV show Cheers,
an ex alcoholic, ex baseball star who worked as a bartender.

by iw!'''
#################
# USER CONFIG   #
#################
token = "YOUR BOT'S API KEY"
#################
#END USER CONFIG#
#################

import discord, pickle
from datetime import date
from datetime import datetime
client = discord.Client()

def database():
	f = open('sam.db', 'rb')
	db = pickle.load(f)
	f.close()
	return db

def update(db):
	f = open('sam.db', 'wb')
	pickle.dump(db, f)
	f.close()


def addUser(user, setdate, setdate2):
	db = database()
	db[user] = setdate2
	update(db)

def days(user):
	db = database()
	days_sober = (date.today() - db[user]).days
	sober_date = db[user].strftime("%m-%d-%Y")

	return sober_date, days_sober

def remove(user):
	'''remove user from database'''
	db = database()
	del db[user]
	update(db)

if __name__ == '__main__':

	@client.event
	async def on_ready():
		print('Cheers! --{0.user}'.format(client))
	
	@client.event
	async def on_message(message):
		if message.author == client.user:
			return
		user = str(message.author).split('#')[0]
		if message.content.lower().startswith('$hello'):
			await message.channel.send('¡Hola, {}!'.format(message.author))
	
		if message.content.lower().startswith('$set') or message.content.lower().startswith('$add'):
			#################
			# add a user to the database
			################
			current_date = date.today()
			current_date_str = current_date.strftime("%m-%d-%Y")
			setdate = '' #
			
			if len(message.content.split()) > 1:
				setdate = message.content.split()[1]
				setdate = setdate.replace('/', '-')
				setdate2 = datetime.strptime(setdate, '%m-%d-%Y') .date()
			else:
				setdate = current_date.strftime("%m-%d-%Y")
				setdate2 = current_date.strftime("%m-%d-%Y")
			await message.channel.send('Sobriety date {} added for {}'.format(setdate, str(message.author).split('#')[0]))
			addUser(str(message.author).split('#')[0], setdate, setdate2)

			#################
			# calculate how many days the user has been sober
			################	
		if message.content.lower().startswith('$days'):
			try:
				sober_date, days_sober = days(user)
				if int(days_sober) == 1:
					await message.channel.send('You are {} day sober. You have been sober since {}!'.format(days_sober, sober_date))
				else:
					await message.channel.send('You are {} days sober. You have been sober since {}!'.format(days_sober, sober_date))
			except KeyError:
				await message.channel.send("I don't see you in the database, {}! Type: `$set` to be added.".format(user))

			#################
			# remove the user from the database
			################	
		if message.content.lower().startswith('$quit') or message.content.lower().startswith('$remove'):
			try: 
				sober_date, days_sober = days(user)
				remove(user)
				await message.channel.send('Sorry to see you go, {}!'.format(user))
			except KeyError:
				await message.channel.send("I don't see you in the database, {}! Type: `$set` to be added.".format(user))
			
			###############
			# Help Message
			##############
		if message.content.lower().startswith('$help'):
			await message.channel.send('''Commands:
			`$set [date]`  - begin tracking your sobriety. ex: `$set` or `$set 12/25/2020`
			`$days` - show how many days you've been sober
			`$quit` - stop tracking your sobriety / take a break.
			`$help` - show this help message and exit'''.format(message.author))
			
	
	
	client.run(token)
