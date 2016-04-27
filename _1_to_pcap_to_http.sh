#!/bin/bash

# 批量将 pcap 文件通过 tcptrace -xhttp 转换成 *.dat 文件和 http.times 文件
# 语法 ： pcap文件列表 输出路径

# pcap文件列表，每一行 为    ID    文件路径（相对于当前工作路径或绝对路径）    注释
# 输出说明，所有文件都会被输出到 输出路径 下，并且加上前缀 ID_
set -x

pcap_files=$1
output_dir=$2

[[ -d "$output_dir" ]] || mkdir "$output_dir"

while read pcap_id pcap_file pcap_comment; do
  tcptrace -n --csv -xhttp -f'port=80' --output_dir=$output_dir --output_prefix=${pcap_id}_ $pcap_file
done < $pcap_files
