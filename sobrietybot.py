#!/usr/bin/env python3
from discord.ext import tasks
import discord
import sqlite3
import datetime
from time import time, sleep

token = 'TOKEN_GOES_HERE' #string
channel_id = CHANNEL_ID_HERE #int

class MyClient(discord.Client):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		# an attribute we can access from our task
		self.counter = 0
		

		# start the task to run in the background
		self.my_background_task.start()

	def addUser (self, username, date=False):
		db = sqlite3.connect('users.db')
		cursor = db.cursor()
	
		# insert users database
		query = """INSERT OR REPLACE INTO 'users' ('username', 'date', 'milestone') VALUES (?, ?, ?);"""
	
		if date:	
			date = datetime.datetime.strptime(date, '%m-%d-%Y').strftime('%Y-%m-%d')
			params = (username, date, 0)
		else:
			params = (username, datetime.datetime.now().strftime('%Y-%m-%d'), 0)
	
		cursor.execute(query, params)
		cursor.close()
		db.commit()
		db.close()
	
	def days(self, username):
		db = sqlite3.connect('users.db')
		cursor = db.cursor()
		cursor.execute('''SELECT date from users where username = '{}';'''.format(username))
	
		sobrietyDate = cursor.fetchall()[0][0]
		sobrietyDate = datetime.datetime.strptime(sobrietyDate, '%Y-%m-%d')
	
		days_sober = (datetime.datetime.now() - sobrietyDate).days
		sober_date = sobrietyDate.strftime("%Y-%m-%d")
		cursor.close()
		db.commit()
		db.close()
	
		return sobrietyDate, days_sober
	
	def leaderboard(self):
		db = sqlite3.connect('users.db')
		cursor = db.cursor()
		query = '''SELECT * FROM users ORDER BY date;'''
		records = cursor.execute(query).fetchall()
		cursor.close()
		db.commit()
		db.close()
	
		response = ' '
		count = 0
		for i in records:
			count += 1
			try: current_days = (datetime.datetime.now() - datetime.datetime.strptime(i[1], '%Y-%m-%d %H:%M:%S')).days
			except ValueError:
				print(ValueError)
				current_days = (datetime.datetime.now() - datetime.datetime.strptime(i[1], '%Y-%m-%d')).days
			response += '''{}. {} - {} days\n'''.format(str(count), i[0], current_days)
		return response
	
	
	def remove(self, username):
		db = sqlite3.connect('users.db')
		cursor = db.cursor()
		query = '''DELETE FROM users WHERE username='{}';'''.format(username)
		cursor.execute(query)
		cursor.close()
		db.commit()
		db.close()
	
	def list(self):
		db = sqlite3.connect('users.db')
		cursor = db.cursor()
		query = '''SELECT * FROM users ORDER BY username ASC;'''
		users = cursor.execute(query).fetchall()
		sobrietylist = ''
		count = 0
		for i in users:
			count += 1
			username = i[0].split('#')[0]
			current_days = self.days(i[0])[1]
			sobrietylist += str(count) + '. ' + username + ' - ' + str(current_days) + ' days sober\n'
		cursor.close()
		db.commit()
		db.close()
		return sobrietylist
	
	def goals(self):
		milestones = [3, 7, 14, 21, 31]
		db = sqlite3.connect('users.db')	
		cursor = db.cursor()
		query = '''SELECT * FROM users'''
		records = cursor.execute(query).fetchall()
		achievers = {}
		for users in records:
			username = users[0]
			days_sober = self.days(users[0])[1]
			last_milestone = users[2]
			if last_milestone == None: last_milestone = 0				
	
			for i in milestones:
				if days_sober <= i:
					if days_sober == i and days_sober != last_milestone:
						print(days_sober, last_milestone)
						query = """UPDATE users SET milestone = '{}' WHERE username = '{}';""".format(days_sober, username)
						cursor.execute(query)
						db.commit()
						achievers[username] = days_sober
						break
	
		cursor.close()
		db.close()
		return achievers

	async def on_ready(self):
		print('Logged in as')
		print(self.user.name)
		print(self.user.id)
		print('------')

	@tasks.loop(seconds=60) # task runs every 60 seconds
	async def my_background_task(self):
		channel = self.get_channel(channel_id) # channel ID goes here
		
		achievers = self.goals()
		if achievers:
					for k,v in achievers.items(): 
						await channel.send('Congratulations, {}! You have achieved a new milestone: {} days!'.format(k, v))
					return
		

	@my_background_task.before_loop
	async def before_my_task(self):
		await self.wait_until_ready() # wait until the bot logs in

	async def on_message(self, message):
		user = str(message.author) # who's messaging us?
		botnick = str(client.user).split('#')[0]
		if message.author == client.user:
			return
	
		if client.user.mentioned_in(message):
			if message.content.lower().split()[1] == 'hello':
				await message.channel.send('¡Hola, {}! ¿Como estas!?'.format(message.author))
			if message.content.lower().split()[1] == 'help':
				await message.channel.send('''Commands:
				`set [date]`  - Start tracking your sobriety. ex: `@{}` or `@{} set 1/1/1999`
				`days` - Show how long you've been sober
				`break` - Stop tracking your sobriety / take a break.
				`leaderboard` - Shows a list of everyone in the database, ordered by days sober.
				`list` - List everyone in the database.
				`help` - Show this help message'''.format(botnick, botnick))
			
			if message.content.lower().split()[1] == 'set':
						setdate = ''
						if len(message.content.split()) == 3: #e.g. @sobrietybot set 12/25/2020
							date = message.content.split()[2].replace('/', '-')
							setdate = date
							if len(setdate) == 8:  # e.g. @sobrietybot set 12-15-20
								setdate = setdate[:-2] + "20" + setdate[-2:]
							self.addUser(str(message.author), setdate)
						elif len(message.content.split()) == 2: #i.e. @sobrietybot set
							self.addUser(str(message.author))
							setdate = datetime.datetime.now().strftime("%m-%d-%Y")
						else:
							print(message.content.split())
						await message.channel.send('Sobriety date {} added for {}'.format(setdate, str(message.author).split('#')[0]))
			
			#DAYS
			if message.content.lower().split()[1] == 'days' or message.content.lower().split()[1] == 'info':
				sober_date, days_sober = self.days(user)
				if int(days_sober) == 1:
					await message.channel.send('You are {} day sober! You have been sober since {}!'.format(days_sober, sober_date.strftime("%m-%d-%Y")))
				else:
					await message.channel.send('You are {} days sober! You have been sober since {} :)'.format(days_sober, sober_date.strftime("%m-%d-%Y")))
			
			#BREAK
			if message.content.lower().split()[1] == 'break':
				self.remove(message.author)
				await message.channel.send('{} has been removed from the database. Sorry to see you go!'.format(message.author))
			
			#LEDERBOARD
			if message.content.lower().split()[1] == 'leaderboard': 
				await message.channel.send('{}'.format(self.leaderboard()))
				
			#LIST
			if message.content.lower().split()[1] == 'list': 
				await message.channel.send('{}'.format(self.list()))

			
client = MyClient()
client.run(token)