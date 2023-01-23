import os
import json

from codi.api.tests.framework import Framework
from codi.api.model.input.community import Community


class TestCommunity(Framework):
    def test_deserialize(self):
        with open(os.path.join(os.path.dirname(__file__),
                               'fixture_data/community_with_three_members_and_two_channels.json')) as file:
            json_data = json.load(file)
            community = Community().deserialize(json_data)

            self.assertIsNotNone(community)
            self.assertEqual(len(community.members), 3)
            self.assertEqual(len(community.channels), 2)
