import requests

from django.shortcuts import render
from django.views import View


class Home(View):
    def get(self, request):
        return render(request, 'home.html')


class Stats(View):
    _context = {}
    # FIXME this is a quick hack to obtain locally contrasting colors.
    #  better separation can be obtained systematically with complementary colors. Use them instead.
    _color_palette = [
        '#962319',
        '#689C98',
        '#DF763D',
        '#EBCB77',
        '#9ECD7D',
        '#68B58C',
        '#C9462C',
        '#587F8F',
        '#E1974A',
        '#7550AB'
    ]

    @staticmethod
    def _get_conversations(community):
        conversations_dict = {'channels': []}

        for i, channel in enumerate(community['channels']):
            conversations_dict['channels'].append({'conversations': [], 'labels': []})

            time_sorted_messages = sorted(channel['messages'], key=lambda msg: msg['timestamp'])
            community['channels'][i]['time_sorted_messages'] = time_sorted_messages
            for message in time_sorted_messages:
                if message['conversationId'] in conversations_dict['channels'][i]['labels']:
                    conversations_dict['channels'][i]['conversations'][message['conversationId']-1]['messages']\
                        .append(message)
                else:
                    conversations_dict['channels'][i]['conversations'].append({'messages': [message]})
                    conversations_dict['channels'][i]['labels'].append(message['conversationId'])

        return conversations_dict

    def get(self, request, *args, **kwargs):
        community = requests.get(f'http://127.0.0.1:8000/api/statistics/{kwargs["operation"]}')

        if community.status_code == 200:
            community = community.json()

            # Assign a color for each conversation + postprocessing
            for channels in community['channels']:
                for message in channels['messages']:
                    message['conversationId'] = int(message['conversationId'].replace('T', ''))
                    message['color'] = self._color_palette[message['conversationId'] % len(self._color_palette)]

            if community['type'] == 'validation':
                gold_messages = {}

                # Assign a color for each conversation + postprocessing
                for channels in community['gold']['channels']:
                    for message in channels['messages']:
                        message['conversationId'] = int(message['conversationId'].replace('T', ''))
                        message['color'] = self._color_palette[message['conversationId'] % len(self._color_palette)]

                # Cluster the messages based on their conversation label
                for key, channel in enumerate(community['gold']['channels']):
                    conversations = {}

                    for message in channel['messages']:
                        if message['conversationId'] in conversations:
                            conversations[message['conversationId']].append(message)
                        else:
                            conversations[message['conversationId']] = [message]

                    gold_messages[key] = conversations

                self._context['gold'] = gold_messages

                channels = []

                for channel in self._context['gold']:
                    conversations = []

                    for key in sorted(self._context['gold'][channel]):
                        conversations.append(self._context['gold'][channel][key])

                    channels.append(conversations)

                self._context['gold'] = channels

            self._context['community'] = community
            self._context['conversations'] = self._get_conversations(community)
            self._context['statistics'] = community['statistics']
            self._context['type'] = community['type'].title()
            self._context['type_raw'] = community['type']
            self._context['status'] = 200
        elif community.status_code == 500:
            self._context['status'] = 500
            self._context['type'] = kwargs["operation"]

        return render(request, 'stats.html', context={'context': self._context})


class Annotate(View):
    def get(self, request):
        return render(request, 'annotate.html')
