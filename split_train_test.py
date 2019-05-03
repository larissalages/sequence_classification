import argparse
import ujson
import numpy as np 
import pandas as pd
import subprocess
import re

#check if nuc or aa have data
def check_zeros(lst):
    lst = np.array(lst)
    if np.all(lst == 0):
        return True
    else:
        return False

def check_number(string):
    print(string)
    result = re.findall(r'\d+', string)
    return int(result[0])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-f','--features_file', nargs='+', help="Features Files", required=True) # Use like: python train.py -f features_file1 features_file2 features_file3 features_file4	
    ap.add_argument("-o","--output_name",nargs='+', required=True,help="Output name")
    ap.add_argument("-tp","--training_percent", required=True, help="training percent")
    ap.add_argument("-sp","--subsampling_percent", required=True, help="subsampling percent")
    
    args = vars(ap.parse_args())
    files_name = args["features_file"]
    output_name = args["output_name"]
    training_percent = args["training_percent"]
    training_percent = float(training_percent)
    subsampling_percent = args["subsampling_percent"]
    subsampling_percent = float(subsampling_percent)

    for file_index, block_file in enumerate(files_name):
        #this step is to get the line length of json file by execute a shell command in terminal
        print(block_file)
        print(output_name[file_index])
        command = "wc -l %s"%(block_file)
        line_length = subprocess.check_output(command, shell=True)
        line_length = str(line_length).split(" ")
        line_length = check_number(line_length[2])
        train_number = int(line_length * training_percent)
        testing_number = int((line_length - train_number) * subsampling_percent)
        print(train_number)
        print(testing_number)
        with open(block_file,"r") as handle:
            for i, entry in enumerate(handle):
                entry = ujson.loads(entry)
                if i <= train_number:
                    entry["type"] = "train"
                elif i <= train_number + testing_number:
                    entry["type"] = "test"
                else:
                    break
                entry["features"]["nuc"] = entry["features"]["nuc3m"] + entry["features"]["nuc5m"]
                entry["features"].pop("nuc3m")
                entry["features"].pop("nuc5m")

                # only write if the nuc and amino both are not zero
                if check_zeros(entry["features"]["nuc"])==False and check_zeros(entry["features"]["amino"])==False:
                    if i == 0:
                        print(output_name[file_index])
                        with open(output_name[file_index], 'w') as f:
                            ujson.dump(entry, f)
                            f.write('\n')
                    else:
                        with open(output_name[file_index], 'a') as f:
                            ujson.dump(entry, f)
                            f.write('\n')

main()