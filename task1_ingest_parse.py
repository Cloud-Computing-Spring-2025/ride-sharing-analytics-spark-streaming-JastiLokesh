#!/usr/bin/env python3
# task1_ingest_parse.py - Task 1: Basic Streaming Ingestion and Parsing

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType
import os

def main():
    # Create Spark Session
    spark = SparkSession.builder \
        .appName("RideShare-Task1-IngestParse") \
        .master("local[*]") \
        .getOrCreate()
    
    # Set log level to reduce verbosity
    spark.sparkContext.setLogLevel("WARN")
    
    print("Task 1: Ingesting and parsing streaming ride-sharing data")
    
    # Define the schema for the incoming JSON data
    ride_schema = StructType([
        StructField("trip_id", StringType(), True),
        StructField("driver_id", IntegerType(), True),
        StructField("distance_km", DoubleType(), True),
        StructField("fare_amount", DoubleType(), True),
        StructField("timestamp", StringType(), True)
    ])
    
    # Ensure output directory exists
    output_dir = "output/task1"
    checkpoint_dir = "checkpoints/task1"
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    # Read the streaming data from socket
    raw_stream = spark.readStream \
        .format("socket") \
        .option("host", "localhost") \
        .option("port", 9999) \
        .load()
    
    # Parse the JSON data
    parsed_stream = raw_stream \
        .selectExpr("CAST(value AS STRING) as json_data") \
        .select(from_json(col("json_data"), ride_schema).alias("data")) \
        .select("data.*")
    
    # Start the streaming query to output data to console
    console_query = parsed_stream.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "false") \
        .start()
    
    # Start the streaming query to output data to CSV files
    csv_query = parsed_stream.writeStream \
        .outputMode("append") \
        .format("csv") \
        .option("path", output_dir) \
        .option("checkpointLocation", checkpoint_dir) \
        .option("header", "true") \
        .start()
    
    print(f"Streaming is active. Data will be written to console and {output_dir}/ directory")
    print("Press Ctrl+C to terminate")
    
    try:
        # Wait for any of the queries to terminate
        spark.streams.awaitAnyTermination()
    except KeyboardInterrupt:
        print("Stopping streaming application")
        console_query.stop()
        csv_query.stop()

if __name__ == "__main__":
    main()