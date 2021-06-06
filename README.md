# Telegram-Secret-Message-Bot
A Telegram Bot for extracting group members and sending them secret end-to-end encrypted messages. As you might know, regular messages in Telegram are not end-to-end encrypted means they are decrypted at Telegrams servers and Telegram can read them.

A secret message feature in Telegram, however, does support end-to-end encryption but there is little no resource on how to automate and leverage this feature with Bots and Telegram API.

A python package named [Telethon](https://pypi.org/project/Telethon/) is a life saver in automating Telegram with everything except secret chats and messages. For that, in this project I have used [Telethon Secret Chat](https://pypi.org/project/telethon-secret-chat/) which is the only python package that supports Telegram secret chats.

It took a long amount of time to go throught the documentation of Telethon-secret-chat, it is poorly documented without any useful examples, and get my code working. 

Fortunately, it's good to go now.
