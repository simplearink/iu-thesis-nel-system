import pandas as pd
import os

# metrics calculation on csv files

ground_truth = "./news_dataset/processed"

filenames = [f"{i}.csv" for i in range(1, 31) if i != 26]

pred_paths = ["./news_dataset/opentapioca_jsons", "./news_dataset/res/sent_context", "./news_dataset/res/full_context", "./news_dataset/res/aliases_sent", "./news_dataset/res/aliases_full"]

for pred_path in pred_paths:
    correct = 0  # совпадает с GT
    unlinked_false = 0  # у которых есть айди, но стоит -1
    linked_false = 0  # у которых нет айди, но в поле стоит
    incorrect_link = 0

    unmentioned = 0

    total_GT = 0
    total_pred = 0
    correct_at_3 = 0
    print(pred_path)
    for name in filenames:
        gt = pd.read_csv(os.path.join(ground_truth, name))
        pred = pd.read_csv(os.path.join(pred_path, name))

        total_GT += len(gt)
        total_pred += len(pred)

        for i, row1 in pred.iterrows():
            if not isinstance(row1['id'], int):
                row1['id'] = eval(row1['id']) if "[" in row1['id'] else row1['id']
            for j, row2 in gt.iterrows():
                if row1['entity'] == row2['entity'] and row1['start'] == row2['start']: #((row1['start'] >= row2['start'] and row1['end'] <= row2['end']) or ((row1['start'] >= row2['start'] and row1['start'] <= row2['end']) ^ (row1['end'] >= row2['start'] and row1['end'] <= row2['end']))):
                    # print(row1['entity'], "|",  row2['entity'])
                    if row1['id'] != -1 and row2['id'] != -1:
                        if row1['id'][0] == row2['id']:
                            correct += 1
                        else:
                            incorrect_link += 1
                        n = row1['id'].count(row2['id'])
                        correct_at_3 += n / 3

                    elif row1['id'] == -1 and row2['id'] == -1:
                        correct += 1
                        correct_at_3 += 1
                    elif row2['id'] == -1 and row1['id'] != -1:
                        linked_false += 1
                    elif row2['id'] != -1 and row1['id'] == -1:
                        unlinked_false += 1
                    else:
                        incorrect_link += 1

        unmentioned_list = []

        for e in list(pred['entity']):
            if e not in list(gt['entity']):
                unmentioned += 1
                unmentioned_list.append(e)

    # print(#correct/total_GT * 100,
    #       #(unlinked_false + linked_false + incorrect_link) / total_GT * 100,
    #       unlinked_false / (unlinked_false + linked_false + incorrect_link) * 100,
    #       linked_false / (unlinked_false + linked_false + incorrect_link) * 100,
    #       incorrect_link / (unlinked_false + linked_false + incorrect_link) * 100,
    #       # unmentioned/total_pred * 100,
    #       # "OTHER",
    #       # total_GT
    # )

    print(correct / total_GT, linked_false / total_GT, unlinked_false / total_GT, incorrect_link / total_GT,
          unmentioned / total_GT)

    print(correct_at_3 / total_GT)

    TP = 0
    FP = 0
    FN = 0
    for name in filenames:
        gt = pd.read_csv(os.path.join(ground_truth, name))
        pred = pd.read_csv(os.path.join(pred_path, name))

        for i, row1 in gt.iterrows():
            ment_true = row1['entity']
            id_true = str(row1['id']).strip()
            cont_true = row1['start']
            start_true = row1['end']

            for j, row2 in pred.iterrows():
                ment_pred = row2['entity']
                if not isinstance(row2['id'], int):
                    row2['id'] = eval(row2['id'])[0] if "[" in row2['id'] else row2['id']
                id_pred = str(row2['id']).strip()
                cont_pred = row2['start']
                start_pred = row2['end']

                if cont_true == cont_pred and ment_true == ment_pred and start_true == start_pred:
                    if id_true == id_pred:
                        TP += 1
                    else:
                        FN += 1
                elif id_true == id_pred:
                    FP += 1

    gt_entities = [ent['entity'] for _, ent in gt.iterrows()]
    pred_entities = [ent['entity'] for _, ent in pred.iterrows()]

    # maybe this should be omitted; however, these values are very rare and do not change the results
    for e1 in pred_entities:
        if e1 not in gt_entities:
            FP += 1

    prec = TP / (TP + FP)
    recall = TP / (TP + FN)

    # print(prec, recall)

    print(f"Precision: {prec}\nRecall: {recall}\nF1-score: {2 * prec * recall / (prec + recall)}\n")