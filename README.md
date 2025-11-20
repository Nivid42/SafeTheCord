# SafeTheCord
Python based Discord Bot which has some Features for our private needs in our Community.
Further Development is depending on needs.

# Features
- **Spamfilter** Filters Spam by checking against a white List to prevent harmful Links to enter the Discord.
- **BirthdayReminder** Had to program this since everyone doesn't know, also very lightweight with csv (on purpose.. Feel free to Change my Mind :-))

# Installation
1. Clone the Repository:
```
git clone https://github.com/Nivid42/SafeTheCord.git
```


2. Change names of all example Files to their original names
```
bot.log.example → bot.log
birthdays.csv.example → birthdays.csv
.env.example → .env
```


3. Configure .env and config.ini.
   - .env holds your Discord API Token
   - config.ini holds non sensitive Data such as Channel-ID & the Whitelist.


4. Build & Run
```
docker compose up -d --build
```

# Contribute
Contributions are welcome! Whether it's bug fixes, new features, or improvements to the documentation – feel free to open an issue or submit a pull request. <br>
If you have ideas or suggestions but don't want to code them yourself, just open an issue and let's discuss it!
I
