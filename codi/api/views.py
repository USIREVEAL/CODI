import json
import os

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .model.disentanglement.chat import Chat
from .model.disentanglement.content import Content
from .model.disentanglement.discourse import Discourse
from .model.disentanglement.model import Model
from .model.input.community import Community
from .utils.convert_annot import convert_annot
from .utils.decorators import error_handling
from .utils.plain_parser import PlainParser


def set_features(feat_array: [int]):
    features = []
    features_groups = []

    if feat_array[0] == 1:
        features.extend(Chat.get_group_features())
        features_groups.append(Chat)

    if feat_array[1] == 1:
        features.extend(Discourse.get_group_features())
        features_groups.append(Discourse)

    if feat_array[2] == 1:
        features.extend(Content.get_group_features())
        features_groups.append(Content)

    return features, features_groups


###############
# Train Model #
###############
class TrainingView(APIView):
    _model = Model()

    @error_handling
    def post(self, request):
        try:
            features_int = request.data['features']
        except KeyError:
            features_int = [1, 1, 1]

        json_path = os.path.join(os.path.dirname(__file__), 'training/tmp/json')
        if not os.path.exists(json_path):
            os.makedirs(json_path)
        with open(os.path.join(os.path.dirname(__file__), 'training/tmp/json/latest-training.json'), 'w') as f:
            json.dump(request.data, f)

        training_set = Community().deserialize(request.data)
        self._model.train(training_set, features=set_features(features_int)[0])

        return Response(status=status.HTTP_200_OK)


##################
# Validate Model #
##################
class ValidateView(APIView):
    _model = Model()

    @error_handling
    def post(self, request):
        try:
            features_int = request.data['features']
        except KeyError:
            features_int = [1, 1, 1]

        features, features_groups = set_features(features_int)

        community = Community().deserialize(request.data)
        self._model.predict(community, validation=True, features=features, groups=features_groups)

        return Response(status=status.HTTP_200_OK)


#########################
# Predict Conversations #
#########################
class PredictView(APIView):
    _model = Model()

    @error_handling
    def post(self, request):
        try:
            features_int = request.data['features']
        except KeyError:
            features_int = [1, 1, 1]

        community = Community().deserialize(request.data)
        self._model.predict(community, features=set_features(features_int)[0])

        return Response(status=status.HTTP_200_OK)


#######################
# Convert Annotations #
#######################
class ConvertView(APIView):
    _model = Model()
    parser_classes = [PlainParser]

    @error_handling
    def post(self, request):
        convert_path = os.path.join(os.path.dirname(__file__), 'training/tmp/convert')
        if not os.path.exists(convert_path):
            os.makedirs(convert_path)

        with open(os.path.join(os.path.dirname(__file__),
                  'training/tmp/convert/custom.annot'), 'w') as f:
            f.write(request.data)

        with open(os.path.join(os.path.dirname(__file__), 'collections/names'), 'r') as f:
            names = f.readlines()
            file = convert_annot(names, 'custom')

        return Response(status=status.HTTP_200_OK, data=file)


##################
# Get Statistics #
##################
class StatisticsValidationView(APIView):
    _community_and_stats = {}

    def get(self, request):
        with open(os.path.join(os.path.dirname(__file__), 'training/tmp/json/latest-validation.json'), 'r') as f:
            self._community_and_stats = json.load(f)

        return Response(status=status.HTTP_200_OK, data=self._community_and_stats)


class StatisticsPredictionView(APIView):
    _community_and_stats = {}

    def get(self, request):
        with open(os.path.join(os.path.dirname(__file__), 'training/tmp/json/latest-prediction.json'), 'r') as f:
            self._community_and_stats = json.load(f)

        return Response(status=status.HTTP_200_OK, data=self._community_and_stats)
