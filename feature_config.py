#!/bin/bash
import ujson
import json
import pprint
import sys
from itertools import product
from copy import deepcopy
import numpy as np
import argparse

pp = pprint.PrettyPrinter(indent=4)

AAs=list('ARDNCEQGHILKMFPSTWYV')
NUCs=list('ACGT')
amino_keys = list(map(''.join, product(AAs, repeat=int(2))))
nuc_3_key =list(map(''.join, product(NUCs, repeat=int(3))))
nuc_5_key = list(map(''.join, product(NUCs, repeat=int(5))))
amino_keys_hash=dict.fromkeys(amino_keys)
nuc_3_key_hash=dict.fromkeys(nuc_3_key)
nuc_5_key_hash=dict.fromkeys(nuc_5_key)
all_key = {"nuc3m": nuc_3_key_hash,"nuc5m": nuc_5_key_hash, "amino": amino_keys_hash}

for k_type in all_key:
    for i in all_key[k_type]:
        all_key[k_type][i] = []

def get_variance(dict_list):
    for k in dict_list:
        lst = np.array(dict_list[k])
        #if the whole list is zero, put None; else calculate variance
        if np.all(lst==0):
            dict_list[k] = None
        else:
            dict_list[k] = np.var(dict_list[k])
        
def get_ratio(each_set, all_set):
    ratio = {}
    for order in each_set:
        ratio[order] = {}
        for k_type in each_set[order]:
            ratio[order][k_type] = {}
            for k in each_set[order][k_type]:
                ratio[order][k_type][k] = (float(each_set[order][k_type][k])+0.000001) / (float(all_set[k_type][k])+0.000001)
    return ratio

def get_k_smallest_ratio(ratio_set, top_k):
    smallest_ratio = {}
    for order in ratio_set:
        smallest_ratio[order] = {}
        for k_type in ratio_set[order]:
            sorted_ratio_set = sorted(ratio_set[order][k_type].items(), key=lambda x: x[1])
            smallest_ratio[order][k_type] = {}
            for index in range(top_k):
                smallest_ratio[order][k_type][sorted_ratio_set[index][0]] = sorted_ratio_set[index][1] 
    return smallest_ratio

def get_features(ratio_dict):
    features = {"amino":[], "nuc3m": [], "nuc5m": []}
    for label in ratio_dict:
        for k_type in ratio_dict[label]:
            for k_mer in ratio_dict[label][k_type]:
                if k_mer not in features[k_type]:
                    features[k_type].append(k_mer)
    return features

def main():
    ap = argparse.ArgumentParser()
    
    ap.add_argument("-bl","--block_number",required=True,help="input file name")
    ap.add_argument("-o","--output_filename",required=True,help="output file name")
    ap.add_argument("-af","--all_feature_file",required=True,help="summary file name")
    
    args = vars(ap.parse_args())
    
    block_number = args["block_number"]
    all_feature_file = args["all_feature_file"]
    output_filename = args["output_filename"]
    for bl in range(int(block_number)):
        features = {}
        with open(all_feature_file,"r") as handle:
            all_k_mer_list = deepcopy(all_key)
            each_order_list = {}
            for line in handle:
                line = json.loads(line)
                label = line["label"]
                for k_type in all_k_mer_list:
                    data = line["kmers"][k_type][bl]
                    for k in all_k_mer_list[k_type]:
                        if data is not None:
                            if label not in each_order_list:
                                each_order_list[label] = deepcopy(all_key)
                            if k in data:
                                each_order_list[label][k_type][k].append(data[k])
                                all_k_mer_list[k_type][k].append(data[k])
                            else:
                                each_order_list[label][k_type][k].append(0)
                                all_k_mer_list[k_type][k].append(0)

            # find variance
            for k_type in all_k_mer_list:
                get_variance(all_k_mer_list[k_type])
            for order in each_order_list:
                for k_type in each_order_list[order]:
                    get_variance(each_order_list[order][k_type])
            
            #pop all the zero ones
            for k_type in all_k_mer_list:
                for i in all_k_mer_list[k_type].copy():
                    if all_k_mer_list[k_type][i] is None:
                        for order in each_order_list.copy():
                            each_order_list[order][k_type].pop(i)
                        all_k_mer_list[k_type].pop(i)
            #set zero to each order ones
            for order in each_order_list:
                for k_type in each_order_list[order]:
                    for i in each_order_list[order][k_type]:
                        if each_order_list[order][k_type][i] is None:
                            each_order_list[order][k_type][i] = 0
            ratio = get_ratio(each_order_list, all_k_mer_list)
            smallest_ratio_10 = get_k_smallest_ratio(ratio, 64)
            print(smallest_ratio_10)
            features = get_features(smallest_ratio_10)
            if bl == 0:
                with open(output_filename, 'w') as f:
                    ujson.dump(features, f)
                    f.write('\n')
            else:
                with open(output_filename, 'a') as f:
                    ujson.dump(features, f)
                    f.write('\n')
        print(bl)
main()