#!/bin/bash
for entry in "data/amino"/*
do
  temp=" "${entry//data\/amino\/}
  INPUT_FASTA+=$temp
done
echo $INPUT_FASTA
# INPUT_FASTA=" Coleoptera.txt Diptera.txt Hymenoptera.txt Lepidoptera.txt"
AMINO_BLOCKS="33-33-33-33-33-33"
NUC_BLOCKS="99-99-99-99-99-99"
SEQUENCE_FILE="all_sequences_15.json"
ALL_FEATURES_FILE="all_features_15.json"
SHUFFLED_FILE="all_sequences_random_15.json"
SUMMARY_FILE="extractKmers_summary_15.json"
BLOCK_LENGTH="6"
TRAINING_PERCENT="0.1"
SUBSAMPLING_PERCENT="1"
FEATURE_CONFIG_FILE="feature_data/feature_config_15.json"
EACH_BLOCK_FILE="feature_data/block0_all.json feature_data/block1_all.json feature_data/block2_all.json feature_data/block3_all.json feature_data/block4_all.json feature_data/block5_all.json"
# SPLIT_FILES="test_train_data/block0_all_split.json test_train_data/block1_all_split.json test_train_data/block2_all_split.json test_train_data/block3_all_split.json test_train_data/block4_all_split.json test_train_data/block5_all_split.json"
SPLIT_FILES="output_data/all_order_matrix/result_data_split.json"

# python prep_sequence.py -f ${INPUT_FASTA} -abl ${AMINO_BLOCKS} -nbl ${NUC_BLOCKS} -o ${SEQUENCE_FILE}
# perl -MList::Util=shuffle -e 'print shuffle(<STDIN>);' < $SEQUENCE_FILE > $SHUFFLED_FILE
# python all_feature_generation.py -i $SHUFFLED_FILE -o $ALL_FEATURES_FILE -s $SUMMARY_FILE
# python feature_config.py -bl $BLOCK_LENGTH -af $ALL_FEATURES_FILE -o $FEATURE_CONFIG_FILE
# python feature_filter.py -cf $FEATURE_CONFIG_FILE -af $ALL_FEATURES_FILE -o $EACH_BLOCK_FILE
# python split_train_test.py -f $EACH_BLOCK_FILE -o $SPLIT_FILES -tp $TRAINING_PERCENT -sp $SUBSAMPLING_PERCENT

for i in $INPUT_FASTA
do
  ORDER=${i//.txt}
  echo $ORDER
  MODEL_NAME="model/model_cls_conf_${ORDER}.tflearn"
  PREDICTION_NAME="output_data/all_order_matrix/prediction/prediction_${ORDER}.csv"
  # MODEL_NAME="model/0model_${ORDER}.tflearn model/1model_${ORDER}.tflearn model/2model_${ORDER}.tflearn model/3model_${ORDER}.tflearn model/4model_${ORDER}.tflearn model/5model_${ORDER}.tflearn" 
  # PREDICTION_NAME="output_data/all_orders/0prediction_${ORDER}.csv output_data/all_orders/1prediction_${ORDER}.csv output_data/all_orders/2prediction_${ORDER}.csv output_data/all_orders/3prediction_${ORDER}.csv output_data/all_orders/4prediction_${ORDER}.csv output_data/all_orders/5prediction_${ORDER}.csv"

  python trainer.py -f $SPLIT_FILES -t $ORDER -o $MODEL_NAME
  python classify.py -f $SPLIT_FILES -m $MODEL_NAME -o $PREDICTION_NAME -t $ORDER
  python metrics.py -p $PREDICTION_NAME -t $ORDER
done
