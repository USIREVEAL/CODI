#!/usr/bin/env python3

import os
import json
import time
import argparse
import requests


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-t', '--training-set', nargs=1, help='Dataset to use for training')
    parser.add_argument('-v', '--validation-set', nargs='+', help='Dataset(s) to use for validation')
    parser.add_argument('-p', '--platforms', nargs='+', help='The platforms for the training and validation datasets')

    args = parser.parse_args()

    training = []

    with open(os.path.join(os.path.dirname(__file__), f'../{args.training_set[0]}')) as f:
        training += f.readlines()

    # train
    headers = {'Content-Type': 'text/plain'}
    headers_train_val = {'Content-Type': 'application/json'}
    json_res = requests.request('post', 'http://127.0.0.1:8000/api/convert', headers=headers,
                                data=''.join(training).encode('utf-8'))

    json_res = json_res.json()
    json_res['platform'] = args.platforms[0]

    requests.request('post', 'http://127.0.0.1:8000/api/train', headers=headers_train_val,
                     data=json.dumps(json_res))

    for dataset in args.validation_set:

        # validate
        validation = []

        with open(os.path.join(os.path.dirname(__file__), f'../{dataset}')) as f:
            validation += f.readlines()

        json_res_val = requests.request('post', 'http://127.0.0.1:8000/api/convert', headers=headers,
                                    data=''.join(validation).encode('utf-8'))

        json_res_val = json_res_val.json()
        json_res_val['platform'] = args.platforms[1]
        requests.request('post', 'http://127.0.0.1:8000/api/validate', headers=headers_train_val,
                         data=json.dumps(json_res_val))

