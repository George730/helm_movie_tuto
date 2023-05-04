#!/bin/bash

#first, get the current miliseconds
cur_mili=$(($(date +%s%N)/1000000))

#set the miliseconds you want to get data from
#currently set to 12 hours
time_to_check=43200000

#get the starting time by subtracting curent time and miliseconds in 12 hours
start_time=$(($cur_mili - $time_to_check))

#make a file name that contains the date and the filename
file_name=../csvs/$(date "+%Y-%m-%d_%H").csv

#run the command that gets that the data
$(kafkacat -b localhost:9092 -C -t movielog20 -o s@$start_time -o e@$cur_mili > $file_name)