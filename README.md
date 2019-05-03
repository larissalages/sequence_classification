#Sequence Classification Project

## Installation
### Python Virtual Environment Installation
 * Create a virtual environment: `python3 -m venv seq-env`
 * Go to the virtual environment
    * On Unix or MacOS, run: `source seq-env/bin/activate`
    * On Windows, run: `seq-env\Scripts\activate.bat`
 * Install all the python modules: `pip install -r requirements.txt`
 * Check to see if you have all the packages from requirements.txt: `pip list` 
 

## How to run the scripts
### step 1: prep_sequence.py
 * Generate a json file that contains the label name, process id and the blocks of each sequence.
 * Input parameters:
    * INPUT_FASTA_FILES (-f, list parameters): a list of input fasta files for each order
    * NUC_BLOCKS (-nbl): length of each nuc sequence that are seperated by '-'
    * AMINO_BLOCKS (-abl): length of each amino sequence that are seperated by '-'
    * SEQUENCE_FILE (-o): output file name
 * Output: json file that contains all the sequences
 * Command: `python prep_sequence.py -f <INPUT_FASTA_FILES> -abl <AMINO_BLOCKS> -nbl <NUC_BLOCKS> -o <SEQUENCE_FILE>`
 * Example command:
```python
  python prep_sequence.py -f Coleoptera.fasta Diptera.fasta Hymenoptera.fasta Lepidoptera.fasta -abl 33-33-33-33-33-33 -nbl 99-99-99-99-99-99 -o all_sequences.json
```
 * Example output:
```json
{
  "id": "DSCOL571-07", 
  "label": "coleoptera", 
  "seq_amino": 
    ["GTSLSMLIRAELGNPGSLIGDDQIYNVIVTAHA", 
      "LLLSLPVLAGAITMLLTDRNLNTSFFDPAGGGD"...], 
  "seq_nuc": 
    ["GTACTTCTCTAAGAATACTAATTCGAGCTGAATTGCTT",   
      "TGTTACAAATTTAAATACTTCCTTTTTTGACCCTGCCG"...]
}
```

### step 2: ramdom sampling
 * shuffle the data in random order
 * Input parameters:
    * SEQUENCE_FILE: sequence file that is generated from step 1
    * SHUFFLED_FILE: shuffled json sequence file
 * Output file: a sequence file in random order
 * Command: `perl -MList::Util=shuffle -e 'print shuffle(<STDIN>);' < <SEQUENCE_FILE> > <SHUFFLED_FILE>`
 * Example command:
```bash
  perl -MList::Util=shuffle -e 'print shuffle(<STDIN>);' < all_sequences.json > all_sequences_random.json
```


### step 3: all_feature_generation.py
 * Generate two json files, one is a summary of all the k-mers and another one is all the features in the sequence.
 * Input parameters:
    * SHUFFLED_FILE (-i): suffled sequence json file from step 2
    * ALL_FEATURES_FILE (-o): output feature file name
    * SUMMARY_FILE (-s): a summary of all k-mers counts
 * Output: two json files
 * Command: `python all_feature_generation.py -i <SHUFFLED_FILE> -o <ALL_FEATURES_FILE> -s <SUMMARY_FILE>`
 * Example command:
```python
  python all_feature_generation.py -i all_sequences_random.json -o all_features.json -s extractKmers_summary.json
```
 * Example output:
```json
1. extractKmers_summary.json:
  {
    "nuc": 
      {"AAA": 3039308, "AAC": 2338696, "AAG": 1410898, "AAAAA": 135575, "AAAAC": 43937...}, 
    "amino": 
      {"AA": 9687, "AR": 349 ...}, 
    "fragment_counter": 2135604, 
    "record_counter": 355934
  }
```
```json
2. all_features.json:
{
  "id": "DSCOL571-07",
  "label": "coleoptera",
  "kmers": {
    "amino": [
      {"GT": 0.0323,"AH": 0.0323 ...},
      {"FV": 0.0323,"AF": 0.0323 ...},
      ...
    ],
    "nuc": [
      {"GTACT": 0.0106,"TGC": 0.0104 ...},
      {"TCGTA": 0.0106,"CCC": 0.0104 ...},
      ...
    ]
  }
}
```

### step 4: feature_config.py
 * Decide which feature(k-mer) should go to the neural network.
 * Input parameters:
    * BLOCK_LENGTH (-bl): the number of blocks that will be generated
    * ALL_FEATURES_FILE (-af): all feature file from step3
    * FEATURE_CONFIG_FILE (-o): a feature config json file name
 * Output: a feature config json file
 * Command: `python feature_config.py -bl <BLOCK_LENGTH> -af <ALL_FEATURES_FILE> -o <FEATURE_CONFIG_FILE>`
 * Example command:
```python
  python feature_config.py -bl 6 -af all_features.json -o feature_data/feature_config.json
```
 * Example output:
```json
{
  "amino":["SL","SM","GT","LI","GN","GS","LS","SI","LL","MI"],
  "nuc3m":["TTT","AAT","ATT","TTA","ATA","TAT","TAA","GAA","ATC","AAC"],
  "nuc5m":["TTTTT","ATTAA","TTTAA","TAATT","AGAAT","ATAAT","TTAAT","TTATT","AATTA","AATTG"]
}
```

### step 5: feature_filter.py
 * Filter the selected features from all_features.json
 * Input parameters:
    * FEATURE_CONFIG_FILE (-cf): features config json file from step 4
    * ALL_FEATURES_FILE (-af): all feature file from step3
    * EACH_BLOCK_FILE (-o, list parameters): one or more json features_files names for each block
 * Output: 6 json file for each block in feature_data folder
 * Command: `python feature_filter.py -cf <FEATURE_CONFIG_FILE> -af <ALL_FEATURES_FILE> -o <EACH_BLOCK_FILE>`
 * Example command:
```python
  python feature_config.py -af all_features.json -cf feature_data/feature_config.json -o feature_data/block0.json feature_data/block1.json
```
 * Example output: 0_block.json
```json
{
  "id":"DSCOL571-07",
  "label":"coleoptera",
  "features":{
    "amino":[0.0323,0.0645,0.0323,0.0323,0.0645,0.0323,0.0323,0,0,0],
    "nuc3m":[0.0521,0.0312,0.0729,0.0208,0.0521,0.0417,0.0312,0.0104,0.0208,0.0104],
    "nuc5m":[0.0106,0.0213,0.0106,0.0106,0.0106,0.0106,0.0106,0,0,0]
  },
  "features_name":{
    "amino":["GT","SL","LS","SM","LI","GN","GS","SI","LL","MI"],
    "nuc3m":["TAA","GAA","AAT","ATA","ATT","TTA","ATC","TTT","TAT","AAC"],
    "nuc5m":["AGAAT","TAATT","AATTA","TTAAT","AATTG","ATAAT","TTATT","TTTTT","ATTAA","TTTAA"]
  }
}
```

### step 6: split_train_test.py
 * Decide which data will be part of the train set and the test set.
 * Input parameters:
    * EACH_BLOCK_FILE (-f, list parameters): one or more json features_files from step 5
    * SPLIT_FILES(-o, list parameters): one or more json output file names after training and testing data split 
    * TRAINING_PERCENT (-tp): the percent of training data (e.g, -tp 0.1 implies 10% of traing and 90% testing)
    * SUBSAMPLING_PERCENT (-sp): the percent of subsample in testing data (e.g, -sp 0.1 implies 10% of that 90% testing data will be used as testing. This is for speed purpose)
 * Inputs: one or more json features_files, the name of the output_file
 * Output: The same data contained in the features file iput, but with a extra filed, called type that will indicate if the data belongs to train set ou test set.
 * Command: `python split_train_test.py -f <EACH_BLOCK_FILE> -o <SPLIT_FILES> -tp <TRAINING_PERCENT> -sp <SUBSAMPLING_PERCENT>`
 * Example command:

```
    python split_train_test.py -f feature_data/block0.json feature_data/block1.json -o test_train_data/block0_split.json test_train_data/block1_split.json -tp 0.1 -sp 0.1
```
 * Example output: block0_split.json
```json
{
  "GBMUS217-17": {
    "type": "train",
    "features": {
      "AA": [0.0323, 0.0323, 0.0323, ...],
      "NU": [0.0208, 0.0208, 0.0312, ...]
    },
    "features_names": {
      "AA": ["GT","SL","LS"...],
      "NU": ["TAA","GAA","AAT" ...]
    },
    "label": "coleoptera"
  }
}
```

### step 7: trainer.py
* Generate the trained model
* Input parameters:
    * SPLIT_FILES (-f, list parameters): one or more json train_test_split files from step 6
    * ORDER (-t): target order
    * MODEL_NAME (-o, list parameters): one or more tflearn model names
* Output: One or more trained models saved in tflearn files, inside the folder model.
* Command: `python trainer.py -f <SPLIT_FILES> -t <ORDER> -o <MODEL_NAME>`
* Example command:
```
  python3 trainer.py -f test_train_data/block0_split.json test_train_data/block1_split.json -o model/model_lepidoptera_b0.tflearn model/model_lepidoptera_b1.tflearn -t lepidoptera
```

### step 8: classify.py
* Generate predictions for the test data
* Input parameters:
    * SPLIT_FILES (-f, list parameters): one or more json train_test_split files from step 6
    * MODEL_NAME (-m, list parameters): one or more tflearn model name from step 7
    * PREDICTION_NAME (-o, list parameters): one of more prediction csv file names
    * ORDER (-t): target order
* Outputs: One or more csv files with all predictions and the real label
* Command: `python classify.py -f <SPLIT_FILES> -m <MODEL_NAME> -o <PREDICTION_NAME> -t <ORDER>`
* Example command:
```
  python classify.py -f test_train_data/block0_split.json test_train_data/block1_split.json -m model/0model_lep.tflearn model/1model_lep.tflearn -o output_data/0prediction_lep.csv output_data/1prediction_lep.csv -t lepidoptera
```

* Example output: 0prediction_lep.csv
```
| id           | label       | label_num | prediction | confidence_score | model_name                             |
|--------------|-------------|-----------|------------|------------------|----------------------------------------|
| OPPFS1542-17 | hymenoptera | 0         | 0          | 0.5241           | model/model_coleoptera_block_0.tflearn |
| GLGS6751-17  | lepidoptera | 0         | 0          | 0.6781           | model/model_coleoptera_block_0.tflearn |
| WOGRA430-16  | lepidptera  | 0         | 0          | 0.7865           | model/model_coleoptera_block_0.tflearn |
```
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
### all_pipeline.sh
 * This script is a combination of all the previous scripts.
