import pandas as pd
import os, sys

# score caluclation
folder = 'output_data/all_orders/'
classes = os.listdir("data/amino")
classes = [x.replace(".txt", "") for x in classes if x.endswith(".txt") ]
# classes = ["Coleoptera", "Diptera", "Hymenoptera", "Lepidoptera"]
# #merge for each block
# for bl in ['0' ,'1', '2', '3', '4', '5']:
#     bl = str(bl)
#     df_block = None
#     for filename in os.listdir(folder):
#         if filename.endswith('.csv'):
#             if bl in filename:
#                 order = ''
#                 for cl in classes:
#                     if cl in filename:
#                         order = cl
#                 df_each = pd.read_csv(folder+filename)
#                 confidence_name = 'confidence_score_%s' % (order)
#                 df_each = df_each.rename(index=str, columns={'prediction': order,'confidence_score':confidence_name})
                
#                 if df_block is None:
#                     df_block = df_each[['id', 'label', order, confidence_name]]
#                 else:
#                     df_block = df_block.merge(df_each[['id', order, confidence_name]], on='id', how='inner')
#     if df_block is not None:
#         df_block.to_csv(folder+bl+'.csv', index=False)

def turn_to_y_list(order):
    result = [0] * len(classes)
    i = classes.index(order)
    result[i] = 1
    return result

for number in ['0' ,'1', '2', '3', '4', '5']:
    number = str(number)
    df = pd.read_csv(folder + number + '.csv')
    score_lst = []
    for index, row in df.iterrows():
        result = row[classes].tolist()
        label = str(row['label'])
        true_label = turn_to_y_list(label)
        score = 0
        cls_index = classes.index(label)
        try:
            for i in range(len(result)):
                if result[i] is true_label[i]:
                    if i is cls_index:
                        score += 100
                    else:
                        score += 33
                else:
                    if i is cls_index:
                        score -= 100
                    else:
                        score -= 33
            score_lst.append(score)
        except:
            print(result)
            print(true_label)
    df['score'] = score_lst
    print(df.head())
    df.to_csv(folder + number + '.csv', index=False)