import pandas as pd
import sys, os
import ujson
import numpy as np

classes = os.listdir("data/amino")
classes = [x.replace(".txt", "") for x in classes if x.endswith(".txt") ]

csv_name = sys.argv[1]
df_all = pd.read_csv(csv_name)
all_column = df_all.columns.values.tolist()
cls_column = [x for x in all_column if "_class_" in x]
conf_column = [x for x in all_column if "_conf_score_" in x]
for index, row in df_all.iterrows():
    label = row["label"]
    pid = row["id"]
    cls_matrix = []
    conf_matrix = []
    for i in range(6):
        each_block_cls = [x for x in cls_column if str(i) in x]
        each_block_cls = row[each_block_cls].tolist()
        each_block_conf = [x for x in conf_column if str(i) in x]
        each_block_conf = row[each_block_conf].tolist()
        cls_matrix.append(each_block_cls)
        conf_matrix.append(each_block_conf)
    entry = {"id": pid, "label": label, "cls_matrix": cls_matrix, "conf_matrix": conf_matrix}
    entry = ujson.dumps(entry)
    sys.stdout.write(entry + '\n')
