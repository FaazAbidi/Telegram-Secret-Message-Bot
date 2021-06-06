import os
import random
from datetime import datetime, timezone
import asyncio
import csv
import time
from telethon import TelegramClient, sync, errors
from telethon_secret_chat import SecretChatManager, SECRET_TYPES
from telethon.tl.types import InputPeerChat
from telethon.tl.functions.messages import SearchRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import InputMessagesFilterEmpty
from upload_report import upload_report, upload_individual_invite_count


api_id = "[your app id]"   # enter your APP ID here
api_hash = "[your app hash]"  # enter your APP HASH here

client = TelegramClient('xxx', api_id, api_hash).start()

myself = client.get_me()
try: host_name = myself.first_name
except: host_name = myself.first_name + " " + myself.last_name
host_number = myself.phone
user_to_template = {}


def find_group_by_hash(group_hash, isPublic):
    t_group = None
    if isPublic:
        target_group_object = client.get_entity("t.me/%s"%(group_hash))
        for d in client.get_dialogs():
            if d.is_group:
                if abs(target_group_object.id) == int(str(abs(d.id))[3:]) or abs(target_group_object.id) == abs(d.id):
                    t_group = d
                    break
        return t_group
    
    elif isPublic == False:
        target_group_object = client.get_entity("t.me/joinchat/%s"%(group_hash))
        for d in client.get_dialogs():
            if d.is_group:
                if abs(target_group_object.id) == abs(d.id) or abs(target_group_object.id) == int(str(abs(d.id))[3:]):
                    t_group = d
                    break

        return t_group


def msgCount_n_time_filter_user(
    user, 
    group, 
    time24=False,
    time36=False,
    message_count_filter=False,
    message_count_limit=0
    ):
    
    all_messages = []
    user_is_active = False
    hour_36 = 129600
    hour_24 = 86400
    for message in client.iter_messages(group,from_user=user):
        if message.message:
            all_messages.append(message)
            msg_date = message.date.replace(tzinfo=timezone.utc).timestamp()
            time_difference =  datetime.utcnow().timestamp() - msg_date
            if time24:
                if time_difference < hour_24:
                    user_is_active = True
                    break
            elif time36:
                if time_difference < hour_36:
                    user_is_active = True
                    break
    
    if message_count_filter:
        if len(all_messages) >= message_count_limit:
            user_is_active = True
        else:
            user_is_active = False
                
    return user_is_active


def get_messages_in_group_by_user(user, group, time_filter=False):
    messages_by_user = []
    for message in client.iter_messages(group,from_user=user):
        if message.message:
            messages_by_user.append(message.message)
    
    return messages_by_user


def send_invites(
    targeted_group, 
    your_group, 
    confirmation, 
    templates, 
    target_public, 
    your_public,
    time_filter=False,
    message_count_filter=False,
    message_count_limit=0
    ):

    targeted_group_final = None
    invite_count = 0
    all_rows = []

    if confirmation == 'Y':
        print("Finding the targeted group from your account...\n")
        targeted_group_final = find_group_by_hash(targeted_group, target_public)
        your_group = find_group_by_hash(your_group, your_public)

        if targeted_group_final is not None:
            print("Found the targeted group successfully...\n")
            print("Extracting all the members from the targeted group...\n")

            # extracted_members = [x for x in client.get_participants(
            #     targeted_group_final, aggressive=True)]
            extracted_members = []
            for extract in client.get_participants(targeted_group_final, aggressive=True):
                if extract.bot == False:
                    if time_filter:
                        if msgCount_n_time_filter_user(
                            extract, 
                            targeted_group_final, 
                            time24=True,
                            message_count_filter=False
                            ):
                            extracted_members.append(extract)
                    elif message_count_filter:
                        if msgCount_n_time_filter_user(
                            extract, 
                            targeted_group_final, 
                            time24=False,
                            message_count_filter=True,
                            message_count_limit=message_count_limit
                        ):
                            extracted_members.append(extract)
                    elif time_filter and message_count_filter:
                        if msgCount_n_time_filter_user(
                            extract, 
                            targeted_group_final, 
                            time24=True,
                            message_count_filter=True,
                            message_count_limit=message_count_limit
                        ):
                            extracted_members.append(extract)
                    else:
                        extracted_members.append(extract)


            your_group_members = [str(y.id) for y in client.get_participants(
                your_group, aggressive=True)]

            print("Extracted %s members...\n" % (len(extracted_members)))
            print("Sending invites now...\n")

            for member in extracted_members:

                if str(member.id) not in your_group_members:
                    templates = get_templates()
                    random_temp = random.randint(0,len(templates)-1)
                    template = templates[random_temp]
                    del random_temp

                    sleep_time = random.randint(20,200)
                    print("Waiting %s seconds before sending the next message..."%(sleep_time))
                    time.sleep(sleep_time)

                    try: member_name = str(member.first_name + " " + member.last_name)
                    except: member_name = str(member.first_name)
                    try: member_username = str(member.username)
                    except: member_username = "NA"
                    try: member_phone = str(member.phone)
                    except: member_phone = "NA"
                    dateNtime = str(datetime.utcnow().strftime("%d %b %Y %H:%M:%S"))

                    rows_values = [dateNtime,
                                host_name,
                                host_number,
                                template.message,
                                member_name,
                                member_phone,
                                member_username,
                                targeted_group_final.title,
                                your_group.title
                                ]
                                
                    # client.send_message(member.id, template)
                    print("Sending message to %s now...\n"%(member_name))
                    current_template = template
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(testsec(member.id, template))
                    invite_count += 1
                    all_rows.append(rows_values)
                    del rows_values

            print("Invites sent to %s out of %s \n" %
                  (invite_count, len(extracted_members)))
            print("Remaining %s members are already in your group\n" %
                  (len(extracted_members)-invite_count))

            individual_report = [
                host_name,
                dateNtime,
                invite_count
            ]

            print("Uploading report now...\n")
            upload_report(all_rows)
            upload_individual_invite_count(individual_report)
            print("Report uploaded succesfully.\n")

        else:
            print("Group not found. Try again.")

    else:
        print("Request Cancelled")


def make_csv(rows, group_name):
    f = open('extracted_members_%s.csv'%(group_name), 'w', encoding="utf-8")
    writer = csv.writer(f)
    writer.writerow(["Member Name","Member Phone","Member Username","Messages Count"])
    for row in rows: writer.writerow(row)
    f.close()


def extract_group_members(target_group, public_group):
    t_group = None
    full_members = []
    t_group = find_group_by_hash(target_group, public_group)
    print("Targeted group found successfully...\n")
    print("Starting to extract members...\n")

    if t_group:
        for m in client.get_participants(t_group, aggressive=True):
            print(m.first_name)
            try: m_name = str(m.first_name + " " + m.last_name)
            except: m_name = str(m.first_name)
            m_phone = str(m.phone)
            m_username = str(m.username)
            m_message_count = len(get_messages_in_group_by_user(m, t_group))
            full_members.append([
                m_name,
                m_phone,
                m_username,
                m_message_count
            ])

        print("Finished extracting %s members...\n"%(len(full_members)))
        print("Making CSV file...\n")
        make_csv(full_members, t_group.title)
        print("Created CSV file succesfully...\n")


def get_templates():
    template_group = None

    for search in client.get_dialogs():
        if search.is_group and search.name == "Templates":
            template_group = search
            break

    templates = [template for template in client.iter_messages(template_group.id) if template.message]

    return templates


def main():
    targeted_group = input("Enter the hash of the targeted group? ")
    targeted_public = input("Is the targeted group public? (y/n) ")
    your_group = input("Enter the hash of your group? ")
    your_public = input("Is the targeted group public? (y/n) ")

    if targeted_public == "y": targeted_public = True
    elif targeted_public == "n": targeted_public = False
    if your_public == "y": your_public = True
    elif your_public == "n": your_public = False

    print("You have two options:")
    print("1. Extract members from the targeted group and create a CSV without sending them secret messages.")
    print("2. Extract members from the tageted group and send secret messages to only those who are not in your group.")
    choice = input("Either 1 or 2? ")

    if choice == "2":
        time_filter = input("Do you want to add 24hour time filter? (y/n) ")
        if time_filter == "y": time_filter = True
        elif time_filter == "n": time_filter = False
        else: time_filter = False

        message_count_filter = input("Do you want to add message count filter time filter? (y/n) ")
        if message_count_filter == "y": message_count_filter = True
        elif message_count_filter == "n": message_count_filter = False
        else: message_count_filter = False

        if message_count_filter:
            message_count_limit = int(input("Enter message count limit (must be integer) "))
        else:
            message_count_limit = 0

        print("Targeted Group: %s" % (targeted_group))
        print("Your Group: %s\n" % (your_group))
        confirmation = input(
            "If the above details are correct, enter 'Y' to proceed ")
        print("\n\n")

        templates = get_templates()

        send_invites(
            targeted_group, 
            your_group, 
            confirmation, 
            templates, 
            targeted_public, 
            your_public, 
            time_filter,
            message_count_filter,
            message_count_limit
            )

    elif choice == "1":
        extract_group_members(targeted_group, targeted_public)


async def new_chat(chat, created_by_me):

    if created_by_me:
        await manager.send_secret_message(chat.id, user_to_template[chat.id])
        return
    else:
        print("We have accepted the secret chat request of {}".format(chat))


async def testsec(user_id, template):
    try:
        await client.connect()
        chat = await manager.start_secret_chat(user_id)
        user_to_template[chat] = template.message
        manager.new_chat_created
    except errors.FloodWaitError as e:
        print('Flood wait for', e.seconds, "seconds")


manager = SecretChatManager(client, auto_accept=True,
                            new_chat_created=new_chat)
manager.add_secret_event_handler(
    event_type=SECRET_TYPES.accept,
    func=new_chat)

main()

print("done")

with client:
    client.run_until_disconnected()
