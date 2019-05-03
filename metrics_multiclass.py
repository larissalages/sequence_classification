import pickle
import argparse
import pandas as pd
import re
from numpy import array
from sklearn.metrics import roc_curve, auc
from sklearn.metrics import accuracy_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import f1_score
from sklearn import metrics
import matplotlib 
matplotlib.use('agg')
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import numpy as np
from sklearn.metrics import classification_report
import os

def fix_format(string):
    return re.sub('[\[\]\']','',string)

def plot_roc(y_test,y_score):
    # Compute ROC curve and ROC area for each class
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    y_test = array(y_test)
    y_score = array(y_score)
    
    fpr, tpr, thresholds = roc_curve(y_test, y_score)
    
    roc_auc = auc(fpr, tpr)

    
    plt.figure()
    lw = 2
    plt.plot(fpr, tpr, color='darkorange',lw=lw, label='ROC curve (area = %0.5f)' % roc_auc)
    plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic example')
    plt.legend(loc="lower right")
    plt.show()

def metrics_DNN(predict_y,id_test,test_y,classes,scores):
    
    true_positive = 0
    true_negative = 0
    false_positive = 0
    false_negative = 0
    id_misclassified = []
    pred_misclassified = []
    y_misclassified = []
    
    #class[0] is the positive class, test_y == 1 is the positive class
    for i in range(len(predict_y)):
        if (predict_y[i] == classes[0] and test_y[i] == 1):
            true_positive += 1
            
        elif (predict_y[i] == classes[1] and test_y[i] == 0):
            true_negative += 1
            
        elif(predict_y[i] == classes[1] and test_y[i] == 1):
            false_negative += 1
            pred_misclassified.append(predict_y[i])
            id_misclassified.append(id_test[i])
            y_misclassified.append(classes[0])
            
        elif(predict_y[i] == classes[0] and test_y[i] == 0):
            false_positive += 1
            pred_misclassified.append(predict_y[i])
            id_misclassified.append(id_test[i])
            y_misclassified.append(classes[1])
    
    
    df_misclassified = pd.DataFrame({'id': id_misclassified,'predicted': pred_misclassified,'real_class': y_misclassified})
            
    precision_classe0 = float(true_positive)/(true_positive + false_positive)
    sensitivity = float(true_positive)/(true_positive + false_negative) #recall for class0
    F1_score_class0 = 2*(float(precision_classe0*sensitivity)/(precision_classe0 + sensitivity))
    
    precision_classe1 = float(true_negative)/(true_negative + false_negative)
    specificity = float(true_negative)/(false_positive + true_negative)#recall for class1
    F1_score_class1 = 2*(float(precision_classe1*specificity)/(precision_classe1 + specificity))
    
    accuracy = float(true_positive + true_negative)/len(predict_y)
    
    print("Class " + classes[0] +":")
    print("Precision: " + str(precision_classe0))
    print("Sensitivity: " + str(sensitivity))
    print("F1 score: " + str(F1_score_class0))
    
    print("")
    
    print("Class " + classes[1] +":")
    print("Precision: " + str(precision_classe1))
    print("Specificity: " + str(specificity))
    print("F1 score: " + str(F1_score_class1))
    
    print("")
    
    print("Accuracy:")
    print(accuracy)

    plot_roc(test_y,scores)
    
    return df_misclassified

def map_label(df,target):
    new_label = []
    for order in df.label:
        if order == target:
            new_label.append(1)
        else:
            new_label.append(0)

    return new_label

def main():
    #params:
    ap = argparse.ArgumentParser()
    ap.add_argument("-p","--predict_file",nargs='+',required=True,help="Predict file, generate by the classify")
    
    args = vars(ap.parse_args())

    predictions_file = args["predict_file"]
    folder = 'output_data/all_orders/'
    classes = os.listdir("data/amino")
    classes = [x.replace(".txt", "") for x in classes if x.endswith(".txt") ]
    classes.sort()
    target_names = classes
    #Open files
    for i in predictions_file:
        predict_data = pd.read_csv(i)
        # predict_data.label = map_label(predict_data,target)

        print("Accuracy")
        acc = accuracy_score(predict_data.label_num, predict_data.prediction)
        print(acc)

        print("Summary")
        print(classification_report(predict_data.label_num, predict_data.prediction, target_names=target_names))

        #print("F1 score")
        #f1 = f1_score(predict_data.label_num, predict_data.prediction)
        #print(f1)

        #print("AUC")
        #fpr, tpr, thresholds = metrics.roc_curve(predict_data.label_num, predict_data.prediction, pos_label=1)
        #print(metrics.auc(fpr, tpr))

main()