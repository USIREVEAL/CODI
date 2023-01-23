import tqdm

from sklearn.metrics import precision_recall_fscore_support


def micro_averaged_f_score_labels(statistics: dict, gold: [int], pred: [int], feature_group: str = None):
    """
    For each conversation i in gold:
        compute the maximum F-score for each conversation j in proposed;
        compute the sum of all the maximum F-scores averaged by the size of conversation i.
    return the sum

    :param statistics: The statistics dictionary to be returned by the route
    :param gold: Sorted list of gold truth conversation labels for utterances in the dataset
    :param pred: Sorted list of proposed conversation labels for utterances in the dataset
    :param feature_group: The name(s) of the feature group(s) used
    """
    f = 0
    f_is = []

    for conversation_numb in tqdm.tqdm(set(gold)):
        f_scores_pred = []
        gold_conv_len = len([i for i in gold if i == conversation_numb])

        for conversation_numb_pred in set(pred):
            proposed_conv_len = len([i for i in pred if i == conversation_numb_pred])

            overlap_size = 0

            for i in range(len(gold)):
                if gold[i] == conversation_numb and pred[i] == conversation_numb_pred:
                    overlap_size += 1

            precision = overlap_size / proposed_conv_len
            recall = overlap_size / gold_conv_len

            if precision != 0 or recall != 0:
                f_scores_pred.append((2 * precision * recall) / (precision + recall))
            else:
                f_scores_pred.append(0)

        f_i = max(f_scores_pred)
        f_is.append(f_i)
        f += (gold_conv_len / len(gold)) * f_i

    if feature_group:
        label = feature_group
    else:
        label = 'Combined'

    statistics[f'{label}-clustering'] = {
        'accuracy': None,
        'precision': None,
        'recall': None,
        'f1_score': f
    }

    print("F", f)

    return f


def f_score(statistics: dict, labels: [int], prediction: [int], feature_group: str = None, times: dict = None):
    """
    Compute the accuracy, precision, recall, and F1 score given the gold set and the prediction set.

    :param statistics: The statistics dictionary to be returned by the route
    :param labels: The ground truth
    :param prediction: The predicted results
    :param feature_group: String indicating the feature group
    :param times: Time statistics
    """
    right = 0
    lines = 0
    true1 = 0
    false1 = 0
    missed1 = 0

    for true, pred_label in zip(labels, prediction):
        if true == pred_label:
            right += 1
        if true == 1 and pred_label == 1:
            true1 += 1
        elif pred_label == 1:
            false1 += 1
        elif true == 1:
            missed1 += 1
        lines += 1

    print(right, true1, false1, missed1)

    precision = 0
    if true1 + false1 > 0:
        precision = true1 / (true1 + false1)
    rec = true1 / (true1 + missed1)
    f = 0
    if precision + rec > 0:
        f = (2 * precision * rec) / (precision + rec)

    err = (lines - right) / lines
    acc = 1 - err
    print("Acc", acc, "P", precision, "R", rec, "F", f)

    print(f'zeros ratio - labels: {len(list(filter(lambda numb: numb == 0, labels))) / len(labels)}')
    print(f'zeros ratio - pred: {len(list(filter(lambda numb: numb == 0, prediction))) / len(prediction)}')

    print(f'sklearn micro-averaged: {precision_recall_fscore_support(labels, prediction, average="micro")}')
    print(f'sklearn unspecified: {precision_recall_fscore_support(labels, prediction)}')

    if feature_group:
        label = feature_group
    else:
        label = 'Combined'

    statistics[label] = {
        'accuracy': acc,
        'precision': precision,
        'recall': rec,
        'f1_score': f
    }

    if times:
        statistics[label]['times'] = times
