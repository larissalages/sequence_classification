import pandas as pd
import sys, os
import ujson
import numpy as np
from collections import Counter
import random
import csv

folder = 'output_data/all_orders/'
classes = os.listdir("data/amino")
classes = [x.replace(".txt", "") for x in classes if x.endswith(".txt") ]
classes.sort()

def get_label_max_conf(cls_matrix, conf_matrix):
    cls_list = []
    conf_list = []
    class_result = ""
    # print(cls_list)
    # print(conf_list)
    for order in range(len(conf_matrix[0])):
        conf_column_list = conf_matrix[:,order]
        max_conf = max(conf_column_list)
        max_conf_indices = [i for i, x in enumerate(conf_column_list) if x == max_conf]
        max_conf_index = random.choice(max_conf_indices)
        conf_list.append(max_conf)
        cls_list.append(cls_matrix[max_conf_index,order])
    
    # choose the highest confidence if there's multiple 1
    if cls_list.count(1) > 1:
        cls_indices = [i for i, x in enumerate(cls_list) if x == 1]
        all_one_conf_lst = [conf_list[x] for x in cls_indices]
        max_conf = max(all_one_conf_lst)
        max_conf_indices = [i for i, x in enumerate(all_one_conf_lst) if x == max_conf]
        max_conf_index = random.choice(max_conf_indices)
        cls_index = cls_indices[max_conf_index]
        class_result = classes[cls_index]
    # if all zeros, we choose the min because that is the one who is not confident about getting a "0" -> it is more likely to be "1"
    elif cls_list.count(1) == 0:
        min_conf = min(conf_list)
        min_conf_indices = [i for i, x in enumerate(conf_list) if x == min_conf]
        min_conf_index = random.choice(min_conf_indices)
        class_result = classes[min_conf_index]
    else:
        cls_index = cls_list.index(1)
        class_result = classes[cls_index]
    # print(cls_list)
    # print(conf_list)
    # print(class_result)
    return class_result


filename = sys.argv[1]
total_count = 0
count_true = 0

for entry in sys.stdin:
    entry = ujson.loads(entry)
    cls_matrix = np.array(entry["cls_matrix"])
    conf_matrix = np.array(entry["conf_matrix"])
    # print(cls_matrix)
    # print(conf_matrix)
    # print(label)
    label = entry["label"]
    new_label = get_label_max_conf(cls_matrix, conf_matrix)
    result = [entry["id"], entry["label"], new_label]
    print(result)
    if total_count == 0:
        with open(filename, "w") as outcsv:
            writer = csv.writer(outcsv)
            writer.writerow(["id","label","pred_label_high_conf"])
        total_count += 1
    with open(filename, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(result)
    if label == new_label:
        count_true += 1
    total_count += 1

print(total_count)
print(count_true)
print(count_true/total_count)
