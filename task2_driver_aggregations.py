from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, sum, avg, to_timestamp, window
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType
import os

def main():
    # Create Spark session
    spark = SparkSession.builder \
        .appName("RideShare-Task2-DriverAggregations") \
        .master("local[*]") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")
    print("Task 2: Performing real-time driver-level aggregations")

    # Define schema for input JSON
    ride_schema = StructType([
        StructField("trip_id", StringType(), True),
        StructField("driver_id", IntegerType(), True),
        StructField("distance_km", DoubleType(), True),
        StructField("fare_amount", DoubleType(), True),
        StructField("timestamp", StringType(), True)
    ])

    # Prepare output directories
    output_dir = "output/task2"
    checkpoint_dir = "checkpoints/task2"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(checkpoint_dir, exist_ok=True)

    # Read from socket
    raw_stream = spark.readStream \
        .format("socket") \
        .option("host", "localhost") \
        .option("port", 9999) \
        .load()

    # Parse JSON input
    parsed_stream = raw_stream \
        .selectExpr("CAST(value AS STRING) as json_data") \
        .select(from_json(col("json_data"), ride_schema).alias("data")) \
        .select("data.*")

    # Convert timestamp to TimestampType
    parsed_stream = parsed_stream.withColumn("event_time", to_timestamp("timestamp"))

    # Perform windowed aggregations with watermark
    windowed_agg = parsed_stream \
        .withWatermark("event_time", "1 minute") \
        .groupBy(
            window(col("event_time"), "5 minutes", "1 minute"),
            col("driver_id")
        ) \
        .agg(
            sum("fare_amount").alias("total_fare"),
            avg("distance_km").alias("avg_distance")
        ) \
        .select(
            col("window.start").alias("window_start"),
            col("window.end").alias("window_end"),
            col("driver_id"),
            col("total_fare"),
            col("avg_distance")
        )

    # Console Output (update mode)
    console_query = windowed_agg.writeStream \
        .outputMode("update") \
        .format("console") \
        .option("truncate", "false") \
        .start()

    # CSV Output (append mode)
    csv_query = windowed_agg.writeStream \
        .outputMode("append") \
        .format("csv") \
        .option("path", output_dir) \
        .option("checkpointLocation", checkpoint_dir) \
        .option("header", "true") \
        .start()

    print("Streaming started! Writing to console and CSV. Press Ctrl+C to stop.")

    try:
        spark.streams.awaitAnyTermination()
    except KeyboardInterrupt:
        print("Streaming stopped.")
        console_query.stop()
        csv_query.stop()

if __name__ == "__main__":
    main()