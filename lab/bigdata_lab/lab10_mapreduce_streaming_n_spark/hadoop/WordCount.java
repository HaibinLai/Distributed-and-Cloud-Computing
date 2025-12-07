//
//
//
//
// NOTE: I have already complied a jar (wc.jar) for this MapReduce job that you can find in resources/ - this code is just for reference
//
//
//
//

import java.io.IOException;
import java.util.StringTokenizer;

import org.apache.hadoop.conf.Configuration;

import org.apache.hadoop.fs.Path;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;

import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;

import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;

public class WordCount {

  public static class TokenizerMapper extends Mapper<Object, Text, Text, IntWritable>{

    private final static IntWritable one = new IntWritable(1);
    private Text word = new Text();

    public void map(Object key, Text value, Context context
                    ) throws IOException, InterruptedException {
      StringTokenizer itr = new StringTokenizer(value.toString());
      while (itr.hasMoreTokens()) {
        word.set(itr.nextToken());
        context.write(word, one);
      }
    }
  }

  public static class IntSumReducer extends Reducer<Text, IntWritable, Text, IntWritable> {
    private IntWritable result = new IntWritable();

    public void reduce(Text key, Iterable<IntWritable> values, Context context
		    ) throws IOException, InterruptedException {
      int sum = 0;
      for (IntWritable val : values) {
        sum += val.get();
      }
      result.set(sum);
      context.write(key, result);
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    Job job = Job.getInstance(conf, "word count");

    job.setJarByClass(WordCount.class);

    // Explicitly define the input formatter. Map expects <k,v> as input!
    // TextInputFormat does the following:
    //    Splits the input files into chunks (InputSplits) based on HDFS block boundaries.
    //    Reads each line of text within those splits. 
    //    Emits each line as a <key, value> pair where: 
    //      the key is the byte offset of that line within the file (LongWritable)
    //      the value is the actual text content of that line (Text).
    // You can use a costume input formatter class that is suitable for your data
    job.setInputFormatClass(TextInputFormat.class);

    // the mapper class splitting the chunks into words and emitting <word, 1> pairs
    job.setMapperClass(TokenizerMapper.class);
     // combiner for the map outputs (usually the same as the reducer since we want to run a reduction on local data to minimise what needs to be sent over the network)
    job.setCombinerClass(IntSumReducer.class);

    // the reducer class summing the counts for the same keys
    job.setReducerClass(IntSumReducer.class);

    // the types of the output KV: <Text, IntWritable>
    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(IntWritable.class);

    // setts the input and output HDFS paths based on the cmd args provided
    FileInputFormat.addInputPath(job, new Path(args[0]));
    FileOutputFormat.setOutputPath(job, new Path(args[1]));

    // await completion before exit
    System.exit(job.waitForCompletion(true) ? 0 : 1); 
  }
}
