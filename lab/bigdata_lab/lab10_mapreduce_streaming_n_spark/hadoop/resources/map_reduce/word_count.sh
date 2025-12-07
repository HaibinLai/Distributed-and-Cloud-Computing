# $1 = output path in HDFS

yarn jar resources/wc.jar WordCount /text.txt $1 

echo "showing results..."
hdfs dfs -cat $1/*
