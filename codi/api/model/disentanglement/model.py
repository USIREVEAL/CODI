import os
import re
from typing import Dict, Any, Tuple

import tqdm
import time
import json
import numpy
import pickle
import datetime
import configparser

# from nltk.classify import MaxentClassifier, megam
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
# from imblearn.combine import SMOTETomek
from imblearn.over_sampling import SMOTE

from ..input.channel import Channel
from ..input.message import Message
from .relatedness import Relatedness
from .conversation import Conversation
from ..input.community import Community
from ...utils.compute_statistics import *
from ...utils.decorators import measure_time
from ..disentanglement.feature import Feature
from ...utils.serialize_community import serialize_community


class Model:
    """
    This class represents the model of the disentanglement.
    """
    def __init__(self):
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), '../../../../config.ini'))

        self._gold_conversations = []
        self._pred_conversations = []
        self._unigram_probabilities = None
        self._constants = config['constants']
        self._hyperparameters = config['hyperparameters']

        self._load()

    def _save(self, model_type: str = None):
        """
        Save the trained model in the directory `models/`. This model will then be used for the prediction of
        the POSTed community.
        """
        # Check if the `models/` directory exists
        if not os.path.exists(os.path.join(os.path.dirname(__file__), '../../training/tmp/models')):
            os.makedirs(os.path.join(os.path.dirname(__file__), '../../training/tmp/models'))

        # Save the trained model
        if model_type:
            save_path = os.path.join(os.path.dirname(__file__), f'../../training/tmp/models/model-{model_type}.pickle')
        else:
            save_path = os.path.join(os.path.dirname(__file__), '../../training/tmp/models/model.pickle')

        with open(save_path, 'wb') as f:
            pickle.dump(self._trained_model, f)

    def _load(self, model_type: str = None):
        """
        Load the model from a .pickle file.

        :param model_type: The type of the model (i.e. the feature group name)
        """
        try:
            with open(os.path.join(os.path.dirname(__file__), '../../training/tmp/json/latest-training.json'),
                      'r') as f:
                json_obj = json.load(f)
                self._training_set = Community().deserialize(json_obj)
        except FileNotFoundError:
            self._training_set = None

        if model_type:
            path = os.path.join(os.path.dirname(__file__), f'../../training/tmp/models/model-{model_type}.pickle')
            print(f'loaded: model-{model_type}.pickle')
        else:
            path = os.path.join(os.path.dirname(__file__), '../../training/tmp/models/model.pickle')

        try:
            with open(path, 'rb') as f:
                self._trained_model = pickle.load(f)
        except FileNotFoundError:
            self._trained_model = None

    ###############################################################################################################
    # Perform step 1: Max Entropy Classifier                                                                      #
    ###############################################################################################################
    # All the following functions are used in order to compute the Max Entropy Classifier for the given data set. #
    # This is the first step of the conversation disentanglement process.                                         #
    ###############################################################################################################
    def _in_window(self, message_1: Message, message_2: Message):
        """
        Check if the two messages are within a 129 seconds window.

        :param message_1: The first message
        :param message_2: The second message
        :return: True if the two messages are within a 129 seconds window,
                 False otherwise
        """
        message1_timestamp = message_1.timestamp
        message2_timestamp = message_2.timestamp

        if isinstance(message1_timestamp, datetime.datetime):
            diff = abs(int(message2_timestamp.timestamp()) - int(message1_timestamp.timestamp()))
        else:
            diff = abs(int(message2_timestamp) - int(message1_timestamp))

        # FIXME Marco removed pairs with equal to have same output as EC-modded-algorithm
        return diff < int(self._hyperparameters['max window size'])

    def _get_previous_n_pairs(self, messages: [Message], message_index: int):
        """
        Given a message and its index, get all the pairs between the message and the previous n messages. in this case n
        is a hyperparameter.

        :param messages: The list of messages
        :param message_index: The index of the message
        :return: The list of pairs
        """
        pairs = []
        pairs_indices = []
        i = message_index - 1

        while i >= 0 and message_index - i <= int(self._hyperparameters['previous n messages to check']):
            pairs.append((messages[message_index], messages[i]))
            pairs_indices.append((message_index, i))
            i -= 1

        return pairs, pairs_indices

    def _get_more_pairs_if_in_window(self, messages: [Message], message_index: int):
        """
        Given a message, get all the pairs that lie within a self._hyperparameters['max window size'] seconds window
        and are not the pairs with the previous self._hyperparameters['previous n messages to check'] messages.

        :param messages: The list of messages
        :param message_index: The index of the message
        :return: The list of pairs
        """
        pairs = []
        pairs_indices = []
        i = message_index - int(self._hyperparameters['previous n messages to check']) - 1

        while i >= 0 and self._in_window(messages[message_index], messages[i]):
            pairs.append((messages[message_index], messages[i]))
            pairs_indices.append((message_index, i))
            i -= 1

        return pairs, pairs_indices

    # Message Relatedness

    def _get_all_pairs(self, messages: [Message]):
        """
        Get all the pairs of messages. For every message, create pairs with the messages in the 129 seconds window.
        Moreover, create pairs also with the previous 4 messages.

        :param messages: The list of messages sorted with respect to time
        :return: The list of Relatedness objects
        """
        all_pairs = []
        all_pairs_indices = []
        pairs_objs = []

        for i in tqdm.tqdm(range(len(messages)), desc='Creating pairs'):
            pairs = []
            pairs_indices = []
            previous_pairs, previous_indices = self._get_previous_n_pairs(messages, i)
            pairs.extend(previous_pairs)
            pairs_indices.extend(previous_indices)
            window_pairs, window_indices = self._get_more_pairs_if_in_window(messages, i)
            pairs.extend(window_pairs)
            pairs_indices.extend(window_indices)

            # Reverse ordering to preserve temporal sorting of pairs
            pairs = list(reversed(pairs))
            pairs_indices = list(reversed(pairs_indices))
            all_pairs.extend(pairs)
            all_pairs_indices.extend(pairs_indices)

        for msg1, msg2 in all_pairs:
            pair_obj = Relatedness()
            pair_obj.message1 = msg1
            pair_obj.message2 = msg2

            pairs_objs.append(pair_obj)

        return pairs_objs

    def _extract_all_features(self,
                              pairs: [Relatedness],
                              features: [Feature],
                              unigram_probabilities: {str: float},
                              training: bool = True):
        """
        Extract all the features from the pairs.

        :param pairs: The list of pairs
        :param features: The list of features types
        :param training: Whether we are training the model or not
        :param unigram_probabilities: A dictionary containing the probability of each word
        :return: The list of extracted features
        """
        labels = []
        feature_matrix = []

        for pair in tqdm.tqdm(pairs, desc='Extracting features'):
            feat_vec = Feature.get_features(pair.message1,
                                            pair.message2,
                                            features,
                                            self._hyperparameters,
                                            unigram_probabilities)
            feature_matrix.append([feature for feature in feat_vec])

            if training:
                labels.append(int(pair.message1.conversation == pair.message2.conversation))

        return feature_matrix, labels if training else feature_matrix

    @staticmethod
    def _flatten_features(feature_matrix: [[Feature]]):
        """
        Given a matrix of features, flatten it into a matrix of feature values.

        :param feature_matrix: The matrix of features
        :return: The flattened matrix of features
        """
        flattened_matrix = []

        for row in feature_matrix:
            flattened_row = []

            for item in row:
                if isinstance(item.val, list):
                    # FIXME Marco: Apparently values greater than 1 are bad for these classifiers (Should investigate)
                    binary_list = [it if it == 0.0 else 1.0 for it in item.val]
                    flattened_row.extend(binary_list)
                else:
                    flattened_row.append(item.val if item.val == 0.0 else 1.0)

            flattened_matrix.append(flattened_row)

        return flattened_matrix

    @measure_time
    def _compute_max_entropy(self, feature_matrix: [[Feature]], labels: [int]):
        """
        Given the feature matrix, compute the Max Entropy classifier.

        :param feature_matrix: The matrix of the feature objects
        :param labels: The vector of labels
        """
        labels = numpy.array(labels)
        flattened_matrix = numpy.array(self._flatten_features(feature_matrix))

        classifier = self._hyperparameters['classifier']
        if classifier == 'RANDOM_FOREST':
            sm = SMOTE()
            features_resampled, labels_resampled = sm.fit_resample(flattened_matrix, labels)
            self._trained_model = RandomForestClassifier(n_estimators=500).fit(features_resampled, labels_resampled)
        elif classifier == 'LOGISTIC_REGRESSION':
            self._trained_model = LogisticRegression(random_state=0, tol=1e-14, max_iter=100000, penalty='none')\
                .fit(flattened_matrix, labels)
        # elif classifier == 'MEGAM':
            # megam.config_megam(os.path.join(os.path.dirname(__file__), '../../utils/megam_0.92'))
            # features = [({str(index): elem for (index, elem) in enumerate(a)}, b) for (a, b) in zip(flattened_matrix,
            #                                                                                         labels)]
            #
            # self._trained_model = MaxentClassifier.train(features, 'megam', trace=0, max_iter=1000, min_lldelta=0.001)
        else:
            raise RuntimeError(f"Unsupported classifier: {classifier}")

    @measure_time
    def _predict_max_entropy(self, feature_matrix: [[Feature]], pairs: [Relatedness], group: str = None)\
            -> Tuple[Any, Dict[str, Dict[str, Relatedness]]]:
        # FIXME the type Any in this hinting should be resolved to the actual type by providing an interface for
        #  trained models with basic methods that can be called on all trained models (e.g., predict)
        #  with appropriate type hinting
        """
        Given a feature matrix, compute a prediction of its Maximum Entropy.

        :param feature_matrix: The matrix of the feature objects
        :param pairs: The list of generated pairs
        """
        pairs_and_predictions = {}

        flattened_matrix = numpy.array(self._flatten_features(feature_matrix))

        self._load(group)

        classifier = self._hyperparameters['classifier']
        if classifier == 'MEGAM':
            features = [({str(index): elem for (index, elem) in enumerate(a)}) for a in flattened_matrix]
            predictions = self._trained_model.classify_many(features)
            probabilities = self._trained_model.prob_classify_many(features)
        elif classifier == 'LOGISTIC_REGRESSION' or classifier == 'RANDOM_FOREST':
            predictions = self._trained_model.predict(flattened_matrix)
            probabilities = self._trained_model.predict_proba(flattened_matrix)
        else:
            raise RuntimeError(f"Unsupported classifier: {classifier}")

        # FIXME Marco added forcing of predictions to test greedy
        # fake_predictions = []
        # # with open("temp_debug_classifier_predictions_python_mar_2020.csv") as f:
        # with open("temp_debug_classifier_predictions_test_disco.csv") as f:
        #     lines = f.readlines()
        #     for line in lines:
        #         pred, relatedness = line.split()
        #         fake_predictions.append((int(pred), float(relatedness)))

        # total_discrepancy = 0.0
        # total_wrong_predictions = 0
        for i, pair in enumerate(pairs):
            # TODO this checks can be optimized with a function to extract percentages for each classifier
            if classifier == 'MEGAM':
                pair.percentage = probabilities[i].prob(1)
            elif classifier == 'LOGISTIC_REGRESSION' or classifier == 'RANDOM_FOREST':
                pair.percentage = probabilities[i][1]
                # total_discrepancy += abs(probabilities[i][1] - fake_predictions[i][1])
                # pair.percentage = fake_predictions[i][1]
                # if predictions[i] != fake_predictions[i][0]:
                #     # t1 = pair.message1
                #     # t2 = pair.message2
                #     # t3 = pair.percentage
                #     # t4 = flattened_matrix[i]
                #     total_wrong_predictions += 1
                # predictions[i] = fake_predictions[i][0]
            else:
                raise RuntimeError(f"Unsupported classifier: {classifier}")

            if pair.message1.uuid in pairs_and_predictions:
                pairs_and_predictions[pair.message1.uuid][pair.message2.uuid] = pair
            else:
                pairs_and_predictions[pair.message1.uuid] = {pair.message2.uuid: pair}

        # print(f"Total discrepancy with faked data: {total_discrepancy}")
        # print(f"Total wrong predictions: {total_wrong_predictions}")
        return predictions, pairs_and_predictions

    ###############################################################################################################
    # Perform step 2: Conversation Clustering                                                                     #
    ###############################################################################################################
    # All the following functions are used in order to compute the clusters of conversations, given the Max       #
    # Entropy Classifier and the community messages. This is the second and final step of the conversation        #
    # disentanglement process.                                                                                    #
    ###############################################################################################################
    @staticmethod
    def _compute_weight(probability: float):
        """
        Given a probability, compute the weight of the pair.

        :param probability: The probability of the pair of messages
        """
        # return numpy.log(probability / (1 - probability))
        return probability - .5

    @staticmethod
    def _get_pair_probability(pairs: Dict[str, Relatedness], second_message: Message) -> float:
        try:
            probability = pairs[second_message.uuid].percentage
        except KeyError:
            probability = 0.5
        return probability

    def _get_qualities_from_clusters(self,
                                     conversations: [Conversation],
                                     pairs: Dict[str, Relatedness]):
        """
        Given a list of clusters, return The sum of the weights of the nodes in the cluster.

        :param conversations: The list of clusters
        :param pairs: The dictionary of pairs and associated probabilities for a given message
        :return The sum of the weights of the nodes for each cluster
        """
        qualities = [(-1, 0.0)] * len(conversations)

        for i, cluster in enumerate(conversations):
            quality_sum = 0.0

            for second_message in cluster.messages:
                quality_sum += self._compute_weight(self._get_pair_probability(pairs, second_message))
            qualities[i] = (i, quality_sum)

        return qualities

    @measure_time
    def _cluster_messages(self, pairs: Dict[str, Dict[str, Relatedness]], messages: {str, Message}):
        """
        Given a dictionary of message pairs and their probabilities, cluster the conversations.

        :param pairs: The dictionary of message pairs and their probabilities
        :return: The clusters of the conversations
        """
        conversations = []
        best_cluster = None

        for message in tqdm.tqdm(messages, desc='Clustering messages'):
            p = {}
            try:
                p = pairs[messages[message].uuid]
            except KeyError:
                # print(f"message {message} not in pairs")
                pass
            qualities = self._get_qualities_from_clusters(conversations, p)

            if len(qualities) > 0:
                best_cluster = max(qualities, key=lambda x: x[1])

            if best_cluster and best_cluster[1] > 0:
                conversations[best_cluster[0]].messages.append(messages[message])
                self._pred_conversations.append(best_cluster[0] + 1)

                # if is_last:
                #     messages_modified[message].conversation = f'T{best_cluster[0] + 1}'

            else:
                new_convo = Conversation()
                new_convo.uuid = len(conversations) + 1
                new_convo.messages.append(messages[message])

                conversations.append(new_convo)
                self._pred_conversations.append(new_convo.uuid)

                # if is_last:
                #     messages_modified[message].conversation = f'T{new_convo.uuid}'

        # return messages_modified if is_last else messages

    ####################
    # Helper functions #
    ####################
    @staticmethod
    def _convert_structure(conversations: [Conversation]):
        """
        Given a list of Conversation objects, return a dictionary of conversations and messages.

        :param conversations: The list of conversations
        :return: The dictionary of conversations
        """
        conversations_dict = {}

        for i, conversation in enumerate(conversations):
            messages_dict = {}

            for message in conversations[i].messages:
                messages_dict[message.uuid] = message

            final_conversation = Conversation()
            final_conversation.uuid = conversation.uuid
            final_conversation.messages = messages_dict

            conversations_dict[conversation.uuid] = final_conversation

        return conversations_dict

    @staticmethod
    def get_unigram_probabilities(community: Community, range_top_words: int = 50):
        """
        Given a set of all the community messages, compute the unigram probabilities.

        :param community: The community containing all the messages
        :param range_top_words: The number of top words to remove
        :return: A dictionary of unigram probabilities
        """
        unigram_probabilities = {}
        messages = community.get_messages()

        for message in tqdm.tqdm(messages, desc='Computing unigram probabilities'):
            # message_txt = re.sub(r'[^\w\s]', '', message.processable_text)
            # message.processable_text = re.sub(r'[^\w\s]', '', message.processable_text)

            for word in message.processable_text.split():
                # Do not add if it is a removed block (e.g. __MENTION__) or a number or space
                if re.match(r'_{2}([A-Z]*_?)*_{2}|_|\?', word) or word.isnumeric() or word in ['', ' ']:
                    continue

                try:
                    unigram_probabilities[word.lower()] += 1
                except KeyError:
                    unigram_probabilities[word.lower()] = 1

        # Remove the top 50 most common unigrams
        for i in range(range_top_words):
            maximum = max(unigram_probabilities, key=unigram_probabilities.get)
            unigram_probabilities.pop(maximum)

        total = sum(unigram_probabilities.values())

        # Normalize the probabilities
        for word in unigram_probabilities:
            unigram_probabilities[word] = unigram_probabilities[word] / total

        return unigram_probabilities

    @staticmethod
    def _get_target_conversation_labels(channel: Channel):
        """
        Given a channel of a community, retrieve all the target conversations labels.

        :param channel: The Channel from which to retrieve the conversations labels from
        :return: The list of conversation labels
        """
        return [int(message.conversation.replace('T', '')) for message in channel.messages.values()]

    def _set_conversation_labels(self, channel: Channel, time_sorted_messages_dict: Dict[str, Message]):
        """
        Modify the conversation of each message based on the pred_conversation vector.

        :param channel: A channel of the community
        """
        for i, message in enumerate(time_sorted_messages_dict.keys()):
            channel.messages[message].conversation = f'T{self._pred_conversations[i]}'

    ############################################################
    # Main functions for training, validating, and predicting  #
    ############################################################
    @measure_time
    def train(self, training_set: Community, features: [Feature] = Feature().get_default_features(), group: str = None):
        """
        Train the model by getting all the possible message pairs, extracting the features from the pairs, feeding the
        features to the max entropy classifier, and finally feeding the result to the clustering algorithm.

        :param training_set: The training set
        :param features: A list of feature types
        :param group: The feature group name
        :return: The trained model
        """
        for channel in training_set.channels.values():
            if len(channel.messages) > 0:
                self._unigram_probabilities = self.get_unigram_probabilities(training_set)
                time_sorted_messages = sorted(channel.messages.values(), key=lambda message: message.timestamp)
                pairs = self._get_all_pairs(time_sorted_messages)

                feature_matrix, labels = self._extract_all_features(pairs, features, self._unigram_probabilities)
                self._compute_max_entropy(feature_matrix, labels)

        self._save(group)

    def predict(self,
                community: Community,
                features: [Feature] = Feature().get_default_features(),
                validation: bool = False,
                groups: list = None):
        """
        Given a community, divide its messages into conversations. In order to do so, we use the `predict()` method
        of the trained model.

        :param community: The community for which disentangle the conversations
        :param features: A vector of features types
        :param validation: Whether we are validating the model
        :param groups: List of groups of features
        :return: The disentangled community
        """
        try:
            self._load()
        except Exception as e:
            raise Exception(e)

        times = {}
        labels = None
        statistics = {}
        predictions = None

        self._pred_conversations = []
        gold = serialize_community(community)

        for channel in community.channels.values():
            if len(channel.messages) > 0:
                time_sorted_messages_dict = dict(sorted(channel.messages.items(),
                                                        key=lambda message: message[1].timestamp))
                time_sorted_messages = sorted(channel.messages.values(), key=lambda message: message.timestamp)

                self._unigram_probabilities = self.get_unigram_probabilities(community)
                pairs = self._get_all_pairs(time_sorted_messages)

                if validation:
                    self._gold_conversations = self._get_target_conversation_labels(channel)

                    for group in groups:
                        start = time.time()

                        _, train_time = self.train(self._training_set,
                                                   group.get_group_features(),
                                                   group=group().__str__().lower())
                        self._load(group().__str__().lower())
                        feature_matrix, labels = self._extract_all_features(pairs,
                                                                            group.get_group_features(),
                                                                            self._unigram_probabilities)

                        (predictions, pairs_and_predictions), max_entropy_time = \
                            self._predict_max_entropy(feature_matrix, pairs, group=group().__str__().lower())

                        _, clustering_time = self._cluster_messages(pairs_and_predictions, time_sorted_messages_dict)

                        stop = time.time()

                        times = {
                            'train_time': train_time,
                            'max_entropy_time': max_entropy_time,
                            'clustering_time': clustering_time,
                            'total_time': round(stop - start, 3),
                        }

                        f_score(statistics, labels, predictions, group().__str__(), times=times)
                        micro_averaged_f_score_labels(statistics,
                                                      self._gold_conversations,
                                                      self._pred_conversations,
                                                      group().__str__())

                        self._pred_conversations = []

                if (validation and len(groups) > 1) or not validation:
                    start = time.time()

                    _, train_time = self.train(self._training_set, features)
                    self._load()
                    feature_matrix, labels = self._extract_all_features(pairs, features, self._unigram_probabilities)

                    (predictions, pairs_and_predictions), max_entropy_time = self._predict_max_entropy(feature_matrix,
                                                                                                       pairs)
                    _, clustering_time = self._cluster_messages(pairs_and_predictions, time_sorted_messages_dict)
                    # channel.messages = messages
                    self._set_conversation_labels(channel, time_sorted_messages_dict)

                    stop = time.time()

                    times = {
                        'train_time': train_time,
                        'max_entropy_time': max_entropy_time,
                        'clustering_time': clustering_time,
                        'total_time': round(stop - start, 3),
                    }

                if validation and len(groups) > 1:
                    f_score(statistics, labels, predictions, times=times)
                    micro_averaged_f_score_labels(statistics, self._gold_conversations, self._pred_conversations)

            self._pred_conversations = []

        if validation:
            community = community.save_json(1, statistics, gold)
        else:
            community = community.save_json(2, statistics)

        return community
