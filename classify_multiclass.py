#!/bin/bash
import argparse
import json
import pandas as pd
import tensorflow as tf
import tflearn
import time
import csv
import os, sys
import numpy as np

def map_class(label_name, list_class):
    return list_class.index(label_name)

def build_DNN(x_length,y_length):

	tf.reset_default_graph()
	# Build neural network - input data shape, number of words in vocabulary (size of first array element). 
	net = tflearn.input_data(shape=[None, x_length])
	#hidden layers
	net = tflearn.fully_connected(net, 4)
	net = tflearn.fully_connected(net, 8)
	net = tflearn.fully_connected(net, 4)
	# number of intents, columns in the matrix train_y
	net = tflearn.fully_connected(net, y_length, activation='softmax')
	# regression to find best parameters, during training
	net = tflearn.regression(net, optimizer='adam')

	# Define Deep Neural Network model and setup tensorboard
	model = tflearn.DNN(net, tensorboard_dir='tflearn_sequence_logs')
	return model

def build_DNN_Arch1(aa_length, nu_length, y_length):
	tf.reset_default_graph()
	# Build neural network - input data shape, number of words in vocabulary (size of first array element). 
	net_aa = tflearn.input_data(shape=[None, aa_length], name="amino")
	net_nu = tflearn.input_data(shape=[None, nu_length], name="nuc")
	# Two fully connected layers with 8 hidden units/neurons
	net_aa = tflearn.fully_connected(net_aa, 4)
	net_nu = tflearn.fully_connected(net_nu, 4)
	# number of intents, columns in the matrix train_y
	net = tflearn.merge_outputs([net_aa, net_nu])
	net = tflearn.fully_connected(net, 4)
	net = tflearn.fully_connected(net, y_length, activation='sigmoid')
	# regression to find best parameters, during training
	net = tflearn.regression(net, optimizer='adam')

	# Define Deep Neural Network model and setup tensorboard
	model = tflearn.DNN(net, tensorboard_dir='tflearn_arch1_logs', tensorboard_verbose=3)
	return model

def build_DNN_Arch2(aa_length, nu_length, y_length):
	tf.reset_default_graph()
	# Build neural network - input data shape, number of words in vocabulary (size of first array element). 
	net_aa = tflearn.input_data(shape=[None, aa_length], name="amino")
	net_nu = tflearn.input_data(shape=[None, nu_length], name="nuc")
	# Two fully connected layers with 8 hidden units/neurons
#     net_aa = tflearn.fully_connected(net_aa, 4)
	net_nu = tflearn.fully_connected(net_nu, 4)
	# number of intents, columns in the matrix train_y
	net = tflearn.merge_outputs([net_aa, net_nu])
	net = tflearn.fully_connected(net, 4)
	net = tflearn.fully_connected(net, y_length, activation='sigmoid')
	# regression to find best parameters, during training
	net = tflearn.regression(net, optimizer='adam')

	# Define Deep Neural Network model and setup tensorboard
	model = tflearn.DNN(net, tensorboard_dir='tflearn_arch2_logs', tensorboard_verbose=3)
	return model



def predict(model, test_x):
	results = model.predict([test_x])[0]
	max_neuron = max(results)
	idx_max_neuron = np.where(results == max_neuron)[0][0]
	score_conf = results[idx_max_neuron]
	class_result = idx_max_neuron

	return class_result, score_conf


def get_test_data_length(feature_file):
    with open(feature_file,"r") as handle:
        for entry in handle:
            entry = json.loads(entry)
            x_length = len(entry["cls_conf"])
            y_length = 15
            return x_length, y_length

def get_true_label(label_name, order_name):
    #positive result (is lepidoptera) returns 1, negative result (is not lepidoptera) returns 0
    if label_name == order_name:
        return 1
    else:
        return 0
def main():

    ap = argparse.ArgumentParser()
    ap.add_argument('-m','--models', nargs='+', help="trained models", required=True) # Use like: python train.py -m model1 model2 fmodel3 model4	
    ap.add_argument('-f','--features_file', nargs='+', help="Features Files", required=True) # Use like: python train.py -f features_file1 features_file2 features_file3 features_file4	
    ap.add_argument("-o","--output_name",nargs='+', required=True,help="Output name")
    #ap.add_argument("-t","--label_target",required=True,help="Label target")

    args = vars(ap.parse_args())

    files_name = args["features_file"]
    models_name = args["models"]
    output_name = args["output_name"]

    folder = 'output_data/all_orders/'
    classes = os.listdir("data/amino")
    classes = [x.replace(".txt", "") for x in classes if x.endswith(".txt") ]
    classes.sort()

    for i in range(len(files_name)):

        test_x_length, test_y_length = get_test_data_length(files_name[i])
        model = build_DNN(test_x_length,test_y_length)
        model.load(models_name[i])
        with open(files_name[i],"r") as handle:
            count = 0
            for entry in handle:
                entry = json.loads(entry)
                if entry["type"] == "test":

                    label = entry["label"]
                    label_num = map_class(label, classes)

                    class_result, confidence_score = predict(model, entry["cls_conf"])

                    entry_result = [entry["id"], entry["label"], label_num, class_result, confidence_score, models_name[i]]
                    if count == 0:
                        with open(output_name[i],"w") as outcsv:
                            writer = csv.writer(outcsv)
                            writer.writerow(["id","label","label_num","prediction","confidence_score","model_name"])
                        count += 1
                    with open(output_name[i], "a", newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(entry_result)

main()