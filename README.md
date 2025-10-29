# Sicily-Wind-Failure-Database
Automated generation of a power line failure database for Sicily based on daily maximum wind speeds and node-level selection rules.
# Sicily Wind Failure Database Generator

This script automatically generates a dataset of power line failures in **Sicily**, 
based on daily maximum wind speed data collected at each transmission tower node.

## 🔍 Overview
The goal of this script is to create a realistic failure database that can be used 
for **Bayesian updating**, **Markov chain modeling**, and **risk assessment** 
within the VAFFEL framework.

Each node (tower) is analyzed year by year to determine which days are most 
likely to produce wind-induced failures, based on defined thresholds and 
priority scoring rules.

## ⚙️ Key Features
- Reads preprocessed wind data (`per_way_node_day_wind_minmax.csv`)
- Detects and selects nodes and days exceeding wind speed thresholds
- Ensures non-repeated node selection across years
- Labels failure days (`failure = 1`) for selected nodes
- Saves output to CSV for further reliability and fragility analysis

## 📊 Input & Output
**Input file:**  
`per_way_node_day_wind_minmax.csv`  
(contains wind speed, node ID, date, and way ID)

**Output file:**  
`per_way_node_day_wind_minmax_failures_one_node_per_year_no_repeat.csv`  
(generated file with failure labeling)

## 🧠 Algorithm
- Threshold-based wind event detection (`THRESH = 15 m/s`)
- Priority scoring for extreme wind levels (≥19, ≥20, ≥21 m/s)
- Randomized selection among top candidates per year using RNG
- Guarantees different node selection between consecutive years

## 🛠️ Technologies
Python • Pandas • NumPy

## 🗺️ Region
**Sicily, Italy**

## 🧩 Usage
1. Update the file paths at the top of `failur.py`.
2. Run the script:
   ```bash
   python failur.py
