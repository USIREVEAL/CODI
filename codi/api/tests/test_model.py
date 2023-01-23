import os

from codi.api.tests.framework import Framework
from codi.api.model.disentanglement.model import Model


class TestModel(Framework):
    def setUp(self, path: str = None):
        path = os.path.join(os.path.dirname(__file__), f'./fixture_data/{path}')
        data = self._read_data_from_fixtures(path)

        self._community = self._get_community_object(data)
        self._members, self._messages = self._get_community_members_and_messages(data)


class TestPairs(TestModel):
    def setUp(self, path: str = None):
        super().setUp('./community_for_pair_extraction.json')

    def test_get_all_pairs(self):
        messages = [message for message in self._messages.values()]

        pairs_of_ids = []

        # Added model specific parameters to be invariant during tests
        model = Model()
        model._hyperparameters["max window size"] = '129'
        model._hyperparameters["previous n messages to check"] = '4'

        pairs = model._get_all_pairs(messages)

        for pair in pairs:
            pairs_of_ids.append((pair.message1.uuid, pair.message2.uuid))

        swapped_pairs = []
        expected_pairs = [('2', '1'),
                          ('3', '1'), ('3', '2'),
                          ('4', '1'), ('4', '2'), ('4', '3'),
                          ('5', '1'), ('5', '2'), ('5', '3'), ('5', '4'),
                          ('6', '1'), ('6', '2'), ('6', '3'), ('6', '4'), ('6', '5'),
                          ('7', '3'), ('7', '4'), ('7', '5'), ('7', '6'),
                          ('8', '4'), ('8', '5'), ('8', '6'), ('8', '7'),
                          ('9', '5'), ('9', '6'), ('9', '7'), ('9', '8'),
                          ('10', '6'), ('10', '7'), ('10', '8'), ('10', '9')]

        for elem1, elem2 in expected_pairs:
            swapped_pairs.append((elem2, elem1))

        # If lists have equal length AND they are the same when converted to sets, then they are equal
        self.assertEqual(len(pairs_of_ids), len(expected_pairs))
        bool_pairs = set(pairs_of_ids) == set(expected_pairs)
        bool_swapped = set(pairs_of_ids) == set(swapped_pairs)

        self.assertTrue(bool_pairs or bool_swapped)
