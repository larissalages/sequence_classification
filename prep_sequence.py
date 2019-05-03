#!/bin/bash
from Bio import SeqIO
import argparse
import json

# this function will parse the fasta files into a dict for each sequence
def fasta_file_parse(file, seq_type):
	result_list = []
	with open('data/%s/%s' % (seq_type, file), "rU") as handel:
		for record in SeqIO.parse(handel, "fasta"):
			record_dict = {}
			data_list = str(record.id).split('|')
			record_dict['id'] = data_list[0]
			record_dict['label'] = data_list[2]
			record_dict['seq_%s' % seq_type] = str(record.seq.upper())
			result_list.append(record_dict)
	return result_list

#This function will split each sequence into blocks
def seq_split(blocks, seq, start_position, seq_type):
	block_list = []
	for bl in blocks:
		end_position = start_position + bl
		seq_substring = seq[start_position:end_position]
		if seq_type == "nuc":
			missing_seq = seq_substring.count('-') + seq_substring.count('N')
		elif seq_type == "amino":
			missing_seq = seq_substring.count('-') + seq_substring.count('X')
		if missing_seq < len(seq_substring) * 0.1 and len(seq_substring) == (end_position-start_position):
			block_list.append(seq_substring)
		else:
			block_list.append(None)
		start_position = end_position
	return block_list


if __name__ == '__main__':
	ap = argparse.ArgumentParser()

	ap.add_argument("-f","--files", nargs='+', required=True,help="files that need to be executed")
	ap.add_argument("-abl","--amino_acid_block_length",required=False,help="the length of each block for amino acid sequence")
	ap.add_argument("-nbl","--nucleotide_block_length",required=False,help="the length of each block for nucleotide sequence")
	ap.add_argument("-o","--output_filename",required=True,help="output file name")
	
	args = vars(ap.parse_args())

	files = args["files"]
	amino_block_length = args["amino_acid_block_length"]
	nucleo_block_length = args["nucleotide_block_length"]
	output_filename = args["output_filename"]
	if amino_block_length != None:
		amino_block_length = amino_block_length.split("-")
		amino_block_length = [int(i) for i in amino_block_length]
	if nucleo_block_length != None:
		nucleo_block_length = nucleo_block_length.split("-")
		nucleo_block_length = [int(i) for i in nucleo_block_length]

	nuc_start_position = 0
	amino_start_position = 0
	count = 0
	for file in files:
		amino_seq = fasta_file_parse(file, 'amino')
		nuc_seq = fasta_file_parse(file, 'nuc')
		for i in range(len(amino_seq)):
			amino_seq[i].update(nuc_seq[i])
			sequence_dict = amino_seq[i]
			sequence_dict['seq_amino'] = seq_split(amino_block_length, sequence_dict['seq_amino'], amino_start_position, 'amino')
			sequence_dict['seq_nuc'] = seq_split(nucleo_block_length, sequence_dict['seq_nuc'], nuc_start_position, 'nuc')
			if None not in sequence_dict['seq_amino'] and None not in sequence_dict["seq_nuc"]:
				if count == 0:
					with open(output_filename, 'w') as f:
						json.dump(sequence_dict, f)
						f.write('\n')
						count += 1
				else:
					with open(output_filename, 'a') as f:
						json.dump(sequence_dict, f)
						f.write('\n')


