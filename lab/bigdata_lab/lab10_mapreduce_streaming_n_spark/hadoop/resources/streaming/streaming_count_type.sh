hadoop jar share/hadoop/tools/lib/hadoop-streaming-3.4.1.jar \
  -D mapreduce.job.reduces=1 \
  -D mapreduce.job.maps=1 \
  -files resources/streaming/type_mapper.py,resources/streaming/sum_reducer.py \
  -input /Pokemon.csv \
  -output /out \
  -mapper type_mapper.py \
  -reducer sum_reducer.py


echo "----------------------------------- RESULTS ------------------------------"
hdfs dfs -cat /out/*
echo "----------------------------------- RESULTS ------------------------------"

echo "deleting output dir so that it can be reused"
hdfs dfs -rm -r /out