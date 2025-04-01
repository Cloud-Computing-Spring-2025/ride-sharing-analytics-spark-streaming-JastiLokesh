# Real-Time Ride-Sharing Analytics with Apache Spark

This repository contains a real-time analytics pipeline for a ride-sharing platform using Apache Spark Structured Streaming. The system processes streaming data, performs real-time aggregations, and analyzes trends over time.

## Project Overview

The analytics pipeline consists of:
- A data simulator that generates real-time ride-sharing data
- Apache Spark Structured Streaming jobs that analyze the data
- Output to both console and CSV files for further analysis

The project is divided into three main tasks:
1. **Task 1**: Ingest and parse real-time ride data
2. **Task 2**: Perform real-time aggregations on driver earnings and trip distances
3. **Task 3**: Analyze trends over time using a sliding time window

## Prerequisites

- Python 3.7+
- Apache Spark 3.0+
- PySpark
- Faker library (`pip install faker`)

## Installation

```bash
pip install pyspark faker
```

## Project Structure

```
ride-sharing-analytics/
├── data_simulator.py              # Generates ride data and sends to socket
├── task1_ingest_parse.py          # Task 1: Basic ingestion and parsing
├── task2_driver_aggregations.py   # Task 2: Driver-level aggregations
├── task3_windowed_analytics.py    # Task 3: Time-windowed analytics
├── output/                        # Output directory for CSV files
│   ├── task1/                     # Raw parsed data
│   ├── task2/                     # Driver aggregations
│   └── task3/                     # Windowed aggregations
└── checkpoints/                   # Spark checkpoint directories
    ├── task1/
    ├── task2/
    └── task3/
```

## Running the Application

### Step 1: Start the Data Simulator

Start the data simulator in a terminal:

```bash
python data_simulator.py
```

This will start a socket server on `localhost:9999` generating ride-sharing data.

#### Data Simulator Output

```
Streaming data to localhost:9999...
New client connected: ('127.0.0.1', 52436)
Sent: {'trip_id': '4f4bd032-342d-4d71-8a0d-d8c28a22d03c', 'driver_id': 42, 'distance_km': 12.45, 'fare_amount': 62.37, 'timestamp': '2023-04-01 15:23:45'}
Sent: {'trip_id': 'a8b9c0d1-e2f3-4a5b-6c7d-8e9f0a1b2c3d', 'driver_id': 87, 'distance_km': 8.92, 'fare_amount': 35.18, 'timestamp': '2023-04-01 15:23:46'}
```

### Step 2: Task 1 - Basic Streaming Ingestion and Parsing

In a new terminal, run:

```bash
spark-submit task1_ingest_parse.py
```

#### Code Explanation

This script:
1. Creates a Spark Session
2. Defines a schema for the JSON data
3. Reads streaming data from the socket
4. Parses the JSON into a structured DataFrame
5. Outputs the parsed data to both the console and CSV files

#### Sample Output

```
-------------------------------------------
Batch: 0
-------------------------------------------
+------------------------------------+----------+-----------+-----------+-------------------+
|                             trip_id| driver_id|distance_km|fare_amount|          timestamp|
+------------------------------------+----------+-----------+-----------+-------------------+
|4f4bd032-342d-4d71-8a0d-d8c28a22d03c|        42|      12.45|      62.37|2023-04-01 15:23:45|
|a8b9c0d1-e2f3-4a5b-6c7d-8e9f0a1b2c3d|        87|       8.92|      35.18|2023-04-01 15:23:46|
+------------------------------------+----------+-----------+-----------+-------------------+
```

### Step 3: Task 2 - Real-Time Aggregations (Driver-Level)

In a new terminal, run:

```bash
spark-submit task2_driver_aggregations.py
```

#### Code Explanation

This script:
1. Creates a Spark Session
2. Reads and parses the streaming data
3. Converts timestamps to proper TimestampType
4. Performs windowed aggregations by driver_id:
   - Groups by time window and driver_id
   - Calculates total fare and average distance
5. Uses watermarks to handle late data
6. Outputs results to both console and CSV files

#### Sample Output

```
-------------------------------------------
Batch: 2
-------------------------------------------
+-------------------+-------------------+----------+----------+------------+
|       window_start|         window_end| driver_id|total_fare|avg_distance|
+-------------------+-------------------+----------+----------+------------+
|2023-04-01 15:20:00|2023-04-01 15:25:00|        42|     62.37|       12.45|
|2023-04-01 15:20:00|2023-04-01 15:25:00|        87|     35.18|        8.92|
|2023-04-01 15:21:00|2023-04-01 15:26:00|        15|     89.64|       22.75|
+-------------------+-------------------+----------+----------+------------+
```

### Step 4: Task 3 - Windowed Time-Based Analytics

In a new terminal, run:

```bash
spark-submit task3_windowed_analytics.py
```

#### Code Explanation

This script:
1. Creates a Spark Session
2. Reads and parses the streaming data
3. Converts timestamps to proper TimestampType
4. Performs 5-minute windowed aggregation, sliding by 1 minute:
   - Uses watermarks for handling late data
   - Aggregates fare amounts within each time window
5. Outputs results to both console and CSV files

#### Sample Output

```
-------------------------------------------
Batch: 3
-------------------------------------------
+-------------------+-------------------+------------------+
|       window_start|         window_end|total_fare_in_window|
+-------------------+-------------------+------------------+
|2023-04-01 15:20:00|2023-04-01 15:25:00|            187.19|
|2023-04-01 15:21:00|2023-04-01 15:26:00|            187.19|
|2023-04-01 15:22:00|2023-04-01 15:27:00|            187.19|
|2023-04-01 15:23:00|2023-04-01 15:28:00|            187.19|
|2023-04-01 15:24:00|2023-04-01 15:29:00|             97.55|
+-------------------+-------------------+------------------+
```

## Key Concepts

### Apache Spark Structured Streaming

- Uses a declarative API similar to static data processing
- Supports windowed operations and watermarking for late data
- Offers multiple output modes:
  - `append`: Only new rows (used for Task 1 CSV output)
  - `update`: Only rows that have been updated (used for console output)
  - `complete`: Entire result table (not used due to CSV limitations)

### Windowed Operations

- Grouping by time windows allows for time-based analysis
- Sliding windows provide a moving aggregation over time
- Watermarking handles late-arriving data

### CSV Output

- All tasks write their results to CSV files for further analysis
- Task 1: Raw parsed data in `output/task1/`
- Task 2: Driver and time-based aggregations in `output/task2/`
- Task 3: Time-windowed fare analysis in `output/task3/`
