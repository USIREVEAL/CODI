import os
import re
import uuid
import json


def convert_annot(names_list: [str], filename: str):
    """
    Convert a .annot file to a .json file for training.

    :param names_list: The names of the files to convert
    :param filename: The name of the annot file
    """
    base_path = os.path.join(os.path.dirname(__file__), f'../training/tmp/convert/')
    annot_path = os.path.join(base_path, f'{filename}.annot')
    json_path = os.path.join(base_path, f'{filename}.json')

    annot = open(annot_path, 'r').readlines()

    out = {
        'id': str(uuid.uuid4()),
        'name': f'{filename}-set',
        'members': [],
        'channels': [{
            'id': str(uuid.uuid4()),
            'name': 'training',
            'path': 'training-set/training',
            'messages': []
        }],
    }

    for line in annot:
        line = line.strip()

        if re.compile(r'^(T-?\d*)\s').findall(line)[0].strip() == "T-1" or not re.compile(r'([A-z]*)\s:').findall(line):
            continue

        member_id = retrieve_member(line, out)
        retrieve_message(line, out, member_id, names_list)

    with open(json_path, 'w') as f:
        json.dump(out, f)

    return out


def retrieve_member(line: str, out: dict):
    """
    Retrieve the author of the message from a .annot line.

    :param line: The line to retrieve the author from
    :param out: The output dictionary
    :return: The author's id
    """
    member_re = re.compile(r'([A-z]*)\s:')
    member_name = member_re.findall(line)[0]
    member_id = str(uuid.uuid4())

    for member in out['members']:
        if member['name'] == member_name:
            return member['id']

    out['members'].append({
        'id': member_id,
        'name': member_name
    })

    return member_id


def retrieve_message(line: str, out: dict, member_id: str, names_list: [str]):
    """
    Retrieve the message content from a .annot line.

    :param line: The line to retrieve the message from
    :param out: The output dictionary
    :param member_id: The author's id
    :param names_list: The possible names of the members
    :return: The message content
    """
    conversation_re = re.compile(r'^(T-?\d*)\s')
    message_re = re.compile(r'^T\d*\s(?:\d*\.?)*\s(?:[A-z]*\s?)*\s:(.*)')
    timestamp_re = re.compile(r'^T\d*\s(\d*)')

    message = reformat_mention(message_re.findall(line)[0], out, names_list).strip()
    conversation = conversation_re.findall(line)[0].strip()

    out['channels'][0]['messages'].append({
        'id': str(uuid.uuid4()),
        'authorId': member_id,
        'content': message,
        'conversation': conversation,
        'timestamp': timestamp_re.findall(line)[0].strip()
    })


def reformat_mention(message: str, out: dict, names_list: [str]):
    """
    Reformat the content of the message if a mention to a member is found.

    :param message: The message to reformat
    :param out: The output dictionary
    :param names_list: The possible names of the members
    :return: The reformatted message
    """
    mention_re = re.compile(r'\s([A-Z][a-z]*?):\s')

    try:
        for mention in mention_re.findall(message):
            found = False

            for member in out['members']:
                if member['name'] == mention:
                    found = True
                    message = message.replace(f'{mention}:', f'<@U{member["id"]}|{member["name"]}>')
                    break

            if found:
                continue

            if mention not in names_list:
                continue

            member_id = str(uuid.uuid4())
            member_name = mention

            out['members'].append({
                'id': member_id,
                'name': member_name
            })

            message = message.replace(f'{mention}:', f'<@U{member_id}|{member_name}>')

        return message
    except IndexError:
        return message
