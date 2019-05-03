#!/bin/bash
import ujson
import pprint
import sys
import argparse

pp = pprint.PrettyPrinter(indent=4)

#argv[1] is the config file, [2] is all feature file
def main():
    ap = argparse.ArgumentParser()
    
    ap.add_argument("-cf","--config_file",required=True, help="input file name")
    ap.add_argument("-o","--output_filename", nargs='+', required=True,help="output file name")
    ap.add_argument("-af","--all_feature_file",required=True, help="summary file name")
    
    args = vars(ap.parse_args())
    
    config_file = args["config_file"]
    all_feature_file = args["all_feature_file"]
    output_files = args["output_filename"]
    with open(config_file, "r") as output_handle:
        for bl, features in enumerate(output_handle):
            features = ujson.loads(features)
            output_filename = output_files[bl]
            filename = '%s' % (output_filename)
            with open(all_feature_file,"r") as handle:
                count = 0
                for line in handle:
                    line = ujson.loads(line)
                    amino = line["kmers"]["amino"][bl]
                    nuc3m = line["kmers"]["nuc3m"][bl]
                    nuc5m = line["kmers"]["nuc5m"][bl]
                    if amino is not None and nuc3m is not None and nuc5m is not None:
                        entry = line.copy()
                        entry["features"] = {"amino": [], "nuc3m": [], "nuc5m": []}
                        entry["features_name"] = {"amino": [], "nuc3m": [], "nuc5m": []}
                        for k_type in features:
                            #data is a list of features
                            data = dict.fromkeys(features[k_type])
                            for k in data:
                                if k in entry["kmers"][k_type][bl]:
                                    data[k] = entry["kmers"][k_type][bl][k]
                                else:
                                    data[k] = 0
                            entry["features"][k_type] = data.values()
                            entry["features_name"][k_type] = data.keys()
                        entry.pop("kmers")
                        if count == 0:
                            with open(filename, 'w') as f:
                                ujson.dump(entry, f)
                                f.write('\n')
                        else:
                            with open(filename, 'a') as f:
                                ujson.dump(entry, f)
                                f.write('\n')
                    count += 1
            print('finished'+ str(bl))

main()
