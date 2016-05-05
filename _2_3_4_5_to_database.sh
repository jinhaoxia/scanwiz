#!/bin/bash

set -x

pcap_files=$1
output_dir=$2
db_name=$3

# python _2_create_database.py $db_name

while read pcap_id pcap_file pcap_comment; do
  if [ "$pcap_id" -le "0" ]; then
    continue
  fi
  python _3_http_times_to_database.py $db_name $pcap_id $output_dir
  python _5_append_headers_to_database.py $db_name $pcap_id $output_dir
done < $pcap_files
