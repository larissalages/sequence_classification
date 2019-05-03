#!/bin/bash
import sys
import pprint as pp
import ujson
from itertools import product
import argparse

AAs='ARDNCEQGHILKMFPSTWYV'
NUCs='ACGT'

amino_keys = list(map(''.join, product(AAs, repeat=int(2))))
nuc_3_key =list(map(''.join, product(NUCs, repeat=int(3))))
nuc_5_key = list(map(''.join, product(NUCs, repeat=int(5))))

amino_keys_hash=dict.fromkeys(amino_keys,0)
nuc_3_key_hash=dict.fromkeys(nuc_3_key,0)
nuc_5_key_hash=dict.fromkeys(nuc_5_key,0)


globalCountsOfKmers={"nuc3m":nuc_3_key_hash, "nuc5m":nuc_5_key_hash, "amino":amino_keys_hash}


def stringToWords(s,acceptableWords,wordLength):
	counts={}
	for i in range(len(s)-wordLength+1):
		k=s[i:i+wordLength]
		if k in acceptableWords:
			if k not in counts:
				counts[k] = 1
			else:
				counts[k]= counts[k] +1
	return counts

def count_method(s,kMerType,wordLength):
	kMerDict = dict.fromkeys(kMerType)
	for i in kMerDict:
		kMerDict[i] = s.count(i)
	for i in kMerDict.copy():
		if kMerDict[i] is 0:
			del kMerDict[i]
	return kMerDict

def check_equality(dict1, dict2):
	if dict1.items() == dict2.items():
		print('True')
	else:
		print('False')

def divideBySumOfDictValues(d):
	denom=float(sum(d.values()))
	for k in d.keys(): d[k]=round(d[k]/denom,4)
	return d

def main():
	ap = argparse.ArgumentParser()

	ap.add_argument("-i","--input_filename",required=True,help="input file name")
	ap.add_argument("-o","--output_filename",required=True,help="output file name")
	ap.add_argument("-s","--summary_filename",required=True,help="summary file name")
	
	args = vars(ap.parse_args())

	input_file = args["input_filename"]
	output_file = args["output_filename"]
	summary_file = args["summary_filename"]
	with open(input_file,"r") as handle:
		record_counter=0
		fragment_counter=0
		for line in handle:
			entry=ujson.loads(line)
			
			#output - one per entry
			kmers={"amino":[],"nuc3m": [], "nuc5m": []}			
			try:
				#assuming equal number of amino and nuc fragments
				for i in range(len(entry["seq_amino"])):
					amino=entry["seq_amino"][i]
					nuc=entry["seq_nuc"][i]
					fragment_counter+=1
					if amino == None or nuc == None:
						kmers["amino"].append(None)
						kmers["nuc3m"].append(None)
						kmers["nuc5m"].append(None)					
					else:
						#amino
						amino_counts=stringToWords(amino,amino_keys_hash,2)
						for k,v in amino_counts.items(): globalCountsOfKmers["amino"][k]+=v
						divideBySumOfDictValues(amino_counts)
						
						#nuc					
						nuc3_counts=stringToWords(nuc,nuc_3_key_hash,3)
						nuc5_counts=stringToWords(nuc,nuc_5_key_hash,5)
						for k,v in nuc3_counts.items(): globalCountsOfKmers["nuc3m"][k]+=v
						for k,v in nuc5_counts.items(): globalCountsOfKmers["nuc5m"][k]+=v
						divideBySumOfDictValues(nuc3_counts)
						divideBySumOfDictValues(nuc5_counts)
						
						#add to block specifc list
						kmers["amino"].append(amino_counts)
						kmers["nuc3m"].append(nuc3_counts)
						kmers["nuc5m"].append(nuc5_counts)
		
				entry.pop("seq_amino")
				entry.pop("seq_nuc")
					
				entry["kmers"]=kmers
				
				if record_counter == 0:
					with open(output_file, 'w') as f:
						ujson.dump(entry, f)
						f.write('\n')
				else:
					with open(output_file, 'a') as f:
						ujson.dump(entry, f)
						f.write('\n')
				record_counter+=1
			except:
				sys.stderr.write("Error: skipping "+entry["id"]+" due to error.\n")

	with open(summary_file,"w") as h:
		globalCountsOfKmers["fragment_counter"]=fragment_counter
		globalCountsOfKmers["record_counter"]=record_counter
		h.write(ujson.dumps(globalCountsOfKmers))
main()