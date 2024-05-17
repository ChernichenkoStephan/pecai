import csv
import asyncio
import time
from pyrogram import Client

api_id = 7000952 
api_hash = "4e73a2f8e9a0876740de8c36c2ee532e"

ids = [
    'balichat',
    'balichatik',
]

messages_len = 10_000


def message_to_row(message):
    mentioned = ''
    if message.mentioned is not None:
        mentioned = f'{message.mentioned}'

    reply_to_message_id = ''
    if message.reply_to_message_id is not None:
        reply_to_message_id = f'{message.reply_to_message_id}'

    return [message.text, reply_to_message_id, mentioned]

def write_to_csv(name, messages):
    print('writing to file.')
    with open(f'{name}.csv', mode='w') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        writer.writerow(['text','reply_to_message_id','mentioned'])
        for m in messages:
            writer.writerow(message_to_row(m))

async def get_messages(c, chat_id, limit):
    i = 0
    res = list()
    print('starting.')
    async for message in c.get_chat_history(chat_id):
        res.append(message)
        if i == limit:
            break
        if i % 100 == 0:
            print(f'{i+1} done.')
            time.sleep(3)
        i += 1
    return res

async def main():
    async with Client("my_account", api_id, api_hash) as c:
        for id in ids:
            messages = await get_messages(c, id, messages_len)
            write_to_csv(id, messages)


asyncio.run(main())
