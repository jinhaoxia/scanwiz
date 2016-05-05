#!/bin/bash

set -x

db_name="test.db"
output_dir="data/tcptrace"
pcap_list="pcap_list.txt"
seq_output="dataset4spmf.txt"
map_output="dataset4spmf.map"
ans_output="dataset4spmf.ans"
minsup="80%"

./_1_to_pcap_to_http.sh $pcap_list $output_dir | tee analysis
./_2_3_4_5_to_database.sh $pcap_list $output_dir $db_name
./_7_make_dataset_for_spmf.py $db_name $seq_output $map_output
java -jar spmf.jar run VMSP $seq_output $ans_output $minsup | tee $ans_output
