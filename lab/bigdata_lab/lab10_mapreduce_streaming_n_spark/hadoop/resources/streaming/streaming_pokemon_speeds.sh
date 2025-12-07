hadoop jar share/hadoop/tools/lib/hadoop-streaming-3.4.1.jar \
  -D mapreduce.job.reduces=1 \
  -D mapreduce.job.maps=1 \
  -files resources/streaming/type_speed_mapper.py,resources/streaming/max_reducer.py \
  -input /Pokemon.csv \
  -output /out \
  -mapper type_speed_mapper.py \
  -reducer max_reducer.py


echo "----------------------------------- RESULTS ------------------------------"
hdfs dfs -cat /out/*
echo "----------------------------------- RESULTS ------------------------------"

echo "deleting output dir so that it can be reused"
hdfs dfs -rm -r /out