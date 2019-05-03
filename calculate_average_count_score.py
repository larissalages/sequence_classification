import pandas as pd
import argparse
import collections


def Average(lst): 
    return float(sum(lst)) / len(lst) 

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-f','--files', nargs='+', help="Input files", required=True) # Use like: python train.py -f features_file1 features_file2 features_file3 features_file4	

    args = vars(ap.parse_args())

    files_name = args["files"]

    i = 0
    for file in files_name:
    	df = pd.read_csv(file)

    	counter=collections.Counter(df['score'])
    	columns = list(df)
    	list_avr = []
    	list_idx_names = []

    	for col in columns: 
    		if "confidence" in col:
    			list_avr.append(Average(df[col]))
    			list_idx_names.append(col)

    	if i == 0:
    		df_new = pd.DataFrame(list_idx_names,columns = ['order'])
    		df_new[str(i)] = list_avr

    		df_score = pd.DataFrame.from_records([dict(counter)])
    	else:
			df_i = pd.DataFrame(list_idx_names,columns = ['order'])
			df_i[str(i)] = list_avr
			df_scr_i = pd.DataFrame.from_records([dict(counter)])

			df_new = df_new.merge(df_i[[str(i),'order']], on='order', how='inner')
			df_score = pd.concat([df_score,df_scr_i], axis=0)

    	i += 1

    df_score = df_score.fillna(0)
    df_score['block'] = [0,1,2,3,4,5]
    df_new.to_csv('table_conf.tsv',index=False,sep='\t')
    df_score.to_csv('table_score.tsv',index=False,sep='\t')

main()