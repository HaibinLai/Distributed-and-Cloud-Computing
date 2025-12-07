# $1 = number of pi digital to generate
# $2 = output path in HDFS

yarn jar share/hadoop/mapreduce/hadoop-mapreduce-examples-3.4.1.jar bbp 1 $1 4 $2

echo "showing results..."
hdfs dfs -cat $2/*