#!/bin/bash

hdfs dfs -copyFromLocal resources/text.txt /
echo "uploaded file to HDFS!"

hdfs dfs -copyFromLocal resources/Pokemon.csv /
echo "uploaded file to HDFS!"

echo "showing current contents in HDFS root (/)"
hdfs dfs -ls /

