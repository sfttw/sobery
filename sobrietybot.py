#!/usr/bin/env python3
import sqlite3
import datetime
import discord
client = discord.Client()
token = 'YOUR TOKEN HERE'


def addUser (username, date=False):
	db = sqlite3.connect('users.db')
	cursor = db.cursor()

	# insert users database
	query = """INSERT OR REPLACE INTO 'users' ('username', 'date') VALUES (?, ?);"""

	if date:	
		date = datetime.datetime.strptime(date, '%m-%d-%Y').strftime('%Y-%m-%d')
		params = (username, date)
	else:
		params = (username, datetime.datetime.now().strftime('%Y-%m-%d'))

	cursor.execute(query, params)
	cursor.close()
	db.commit()
	db.close()

def days(username):
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

def leaderboard():
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

def remove(username):
	db = sqlite3.connect('users.db')
	cursor = db.cursor()
	query = '''DELETE FROM users WHERE username='{}';'''.format(username)
	cursor.execute(query)
	cursor.close()
	db.commit()
	db.close()

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
			if message.content.lower().split()[1] == 'help':
				await message.channel.send('''Commands:
				`set [date]`  - begin tracking your sobriety. ex: `@{}` or `$set 12/25/2020`
				`days` - show how long you've been sober
				`break` - stop tracking your sobriety / take a break.
				`help` - show this help message and exit'''.format(message.author))

			if message.content.lower().split()[1] == 'hello':
				await message.channel.send('¡Hola, {}! ¿Como estas?'.format(message.author))

			if message.content.lower().split()[1] == 'remove' or message.content.lower().split()[1] == 'break':
				remove(message.author)
				await message.channel.send('{} has been removed from the database. Sorry to see you go!'.format(message.author))

			if message.content.lower().split()[1] == 'leaderboard':
				await message.channel.send('{}'.format(leaderboard()))

			if message.content.lower().split()[1] == 'set':

				setdate = '' #

				if len(message.content.split()) == 3:
					date = message.content.split()[2].replace('/', '-')
					setdate = date
					addUser(str(message.author), date)
				elif len(message.content.split()) == 2:
					addUser(str(message.author))
					setdate = 'today!'
				else:
					print(message.content.split())
				await message.channel.send('Sobriety date {} added for {}'.format(setdate, str(message.author).split('#')[0]))

			if message.content.lower().split()[1] == 'days' or message.content.lower().split()[1] == 'info':
				sober_date, days_sober = days(user)
				if int(days_sober) == 1:
					await message.channel.send('You are {} day sober! You have been sober since {}!'.format(days_sober, sober_date.strftime("%m-%d-%Y")))
				else:
					await message.channel.send('You are {} days sober! You have been sober since {} :)'.format(days_sober, sober_date.strftime("%m-%d-%Y")))
	client.run(token)