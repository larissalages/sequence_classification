#!/bin/bash
import argparse
import ujson
import tflearn
import tensorflow as tf

#get all the data from a specific order
def get_data_order(label_name, order_name):
    if label_name == order_name:
        return [1, 0]
    else:
        return [0, 1]

def build_DNN(x_length,y_length):
	tf.reset_default_graph()
	# Build neural network - input data shape, number of words in vocabulary (size of first array element). 
	net = tflearn.input_data(shape=[None, x_length])
	# Two fully connected layers with 8 hidden units/neurons - optimal for this task
	net = tflearn.fully_connected(net, 4)
	net = tflearn.fully_connected(net, 4,activation='sigmoid')
	# number of intents, columns in the matrix train_y
	net = tflearn.fully_connected(net, y_length, activation='sigmoid')
	# regression to find best parameters, during training
	net = tflearn.regression(net)

	# Define Deep Neural Network model and setup tensorboard
	model = tflearn.DNN(net, tensorboard_dir='tflearn_sequence_logs')
	return model

def build_DNN_Arch1(aa_length, nu_length, y_length):
    tf.reset_default_graph()
    # Build neural network - input data shape, number of words in vocabulary (size of first array element). 
    net_aa = tflearn.input_data(shape=[None, aa_length], name="amino")
    net_nu = tflearn.input_data(shape=[None, nu_length], name="nuc")
    # Two fully connected layers with 4 hidden units/neurons
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
    # Two fully connected layers with 4 hidden units/neurons
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

def train_DNN(model, train_x,train_y,name):
    model.fit(train_x, train_y, n_epoch=5, batch_size=5, show_metric=True)
    model.save(name)
    print(name)

def train_DNN_arch12(model, train_aa, train_nu, train_y,name,grp):
    # Start training (apply gradient descent algorithm)
    # n_epoch - number of epoch to run
    # Batch size defines number of samples that going to be propagated through the network.
    model.fit({"amino":train_aa,"nuc":train_nu}, train_y, n_epoch=5, batch_size=5, show_metric=True)
    model.save(name)
    print(name)
    return name

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-f','--features_file', nargs='+', help="Features Files", required=True) # Use like: python train.py -f features_file1 features_file2 features_file3 features_file4	
    ap.add_argument("-t","--label_target",required=True,help="Label target")
    ap.add_argument("-o","--output_name", nargs='+', required=True,help="Output name")
    
    args = vars(ap.parse_args())
    
    files_name = args["features_file"]
    cls_target = args["label_target"]
    output_name = args["output_name"]
    
    for i in range(len(files_name)):
        # train_nu_x = []
        # train_aa_x = []
        train_x = []
        train_y = []
        with open(files_name[i],"r") as handle:
            for entry in handle:
                entry = ujson.loads(entry)
                if entry["type"] == "train":
                    # train_nu_x.append(entry["features"]["nuc"])
                    # train_aa_x.append(entry["features"]["amino"])
                    train_x.append(entry["cls_conf"])
                    y_value = get_data_order(entry["label"], cls_target)
                    train_y.append(y_value)
        # model = build_DNN_Arch1(len(train_aa_x[0]), len(train_nu_x[0]), len(train_y[0]))
        # print(train_aa_x[0])
        # train_DNN_arch12(model, train_aa_x, train_nu_x,train_y,output_name[i],str(i))
        print(train_x[0])
        print(train_y[0])
        model = build_DNN(len(train_x[0]), len(train_y[0]))
        train_DNN(model, train_x, train_y, output_name[i])

main()