import json
import os

# metrics calculation on json files

gt_path = "wiki_dataset/separate_jsons_processed"

test_folders = ['./wiki_dataset/opentapioca_jsons', './wiki_dataset/res/jsons/sent_context', './wiki_dataset/res/jsons/full_context', './wiki_dataset/res/jsons/aliases_sent', './wiki_dataset/res/jsons/aliases_full']

for folder in test_folders:
    files = os.listdir(folder)

    correct_at_3 = 0

    correct = 0  # совпадает с GT
    unlinked_false = 0  # у которых есть айди, но стоит -1
    linked_false = 0  # у которых нет айди, но в поле стоит
    incorrect_link = 0

    unmentioned = 0

    total_GT = 0
    total_pred = 0
    print(folder)

    for file in files:
        with open(os.path.join(gt_path, file)) as gtfp:
            gt = json.load(gtfp)['listWikiEntity']
        with open(os.path.join(folder, file))  as pred_fp:
            pred = json.load(pred_fp)['listWikiEntity']

        total_GT += len(gt)
        total_pred += len(pred)

        for i in pred:
            for j in gt:
                if i['currentText'] == j['currentText'] and i['startPosition'] == j['startPosition']: #((i['startPosition'] >= j['startPosition'] and i['endPosition'] <= j['endPosition']) or ((i['startPosition'] >= j['startPosition'] and i['startPosition'] <= j['endPosition']) ^ (i['endPosition'] >= j['startPosition'] and i['endPosition'] <= j['endPosition']))):
                    if i['id'] != -1 and i['id'] != -1:
                        if i['id'][0] == j['id']:
                            correct += 1
                        else:
                            incorrect_link += 1
                        # correct += 1
                        n = i['id'].count(j['id'])
                        correct_at_3 += n / 3
                    elif i['id'] == -1 and j['id'] == -1:
                        correct += 1
                        correct_at_3 += 1
                    elif j['id'] == -1 and i['id'] != -1:
                        linked_false += 1
                    elif j['id'] != -1 and i['id'] == -1:
                        unlinked_false += 1
                    else:
                        incorrect_link += 1

        gt_entities = [ent['currentText'] for ent in gt]
        pred_entities = [ent['currentText'] for ent in pred]

        unmentioned_list = []

        for e1 in pred_entities:
            if e1 not in gt_entities:
                # print(e1, folder)
                unmentioned += 1
                unmentioned_list.append(e1)

        # print(unmentioned_list)

    print(correct / total_GT, linked_false / total_GT, unlinked_false / total_GT, incorrect_link / total_GT, unmentioned/ total_GT)
    print(correct_at_3 / total_GT)


    TP = 0
    FP = 0
    FN = 0
    for name in files:
        with open(os.path.join(gt_path, file)) as gtfp:
            gt = json.load(gtfp)['listWikiEntity']
        with open(os.path.join(folder, file))  as pred_fp:
            pred = json.load(pred_fp)['listWikiEntity']

        for i in gt:
            ment_true = i['currentText']
            id_true = str(i['id']).strip()
            cont_true = i['startPosition']
            start_true = i['endPosition']

            for j in pred:
                ment_pred = j['currentText']
                if j['id'] == -1:
                    id_pred = str(j['id']).strip()
                else:
                    id_pred = str(j['id'][0]).strip()
                cont_pred = j['startPosition']
                start_pred = j['endPosition']

                if cont_true == cont_pred and ment_true == ment_pred and start_true == start_pred:
                    if id_true == id_pred:
                        TP += 1
                    else:
                        FN += 1
                elif id_true == id_pred:
                    FP += 1

    gt_entities = [ent['currentText'] for ent in gt]
    pred_entities = [ent['currentText'] for ent in pred]

    # maybe this should be omitted; however, these values are very rare and do not change the results
    for e1 in pred_entities:
        if e1 not in gt_entities:
            FP += 1

    prec = TP / (TP + FP)
    recall = TP / (TP+FN)

    print(f"Precision: {prec}\nRecall: {recall}\nF1-score: {2*prec*recall/(prec+recall)}\n")

