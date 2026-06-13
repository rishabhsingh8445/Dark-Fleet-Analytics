import pandas as pd

print("Starting Anomaly Detection on REAL AIS Data (Dark Fleet Tracker)...")

input_file = "C:\\Users\\rshbh\\downloads\\processed_AIS_dataset.csv"
output_file = "C:\\Users\\rshbh\\downloads\\final_dark_fleet_powerbi.csv"

# 1. Load the raw AIS data (Only loading necessary columns to save RAM)
print("Loading 1 Million+ rows of REAL AIS data...")
df = pd.read_csv(input_file, usecols=['MMSI', 'BaseDateTime', 'LAT', 'LON', 'SOG', 'VesselName'])

# Ensure Timestamp is datetime
df['BaseDateTime'] = pd.to_datetime(df['BaseDateTime'])

# 2. Sort data by Ship (MMSI) and Time
print("Sorting data to track individual ship journeys...")
df = df.sort_values(by=['MMSI', 'BaseDateTime'])

# 3. Calculate Time Gap (Difference between current ping and previous ping)
print("Calculating geospatial time-gaps...")
df['Previous_Timestamp'] = df.groupby('MMSI')['BaseDateTime'].shift(1)
df['Time_Gap_Hours'] = (df['BaseDateTime'] - df['Previous_Timestamp']).dt.total_seconds() / 3600

df['Time_Gap_Hours'] = df['Time_Gap_Hours'].fillna(0)

# 4. Define Dark Fleet Logic
# Flag a ship if the gap between radar pings is greater than 12 hours AND they are moving (SOG > 0.5)
# (If SOG is 0, they might just be anchored/parked and turned off AIS to save power)
print("Applying Anomaly Detection Algorithm...")
df['Is_Dark_Activity'] = ((df['Time_Gap_Hours'] >= 12) & (df['SOG'] > 0.5)).astype(int)

# To keep the Power BI file extremely fast but still realistic, 
# we keep ALL dark fleet events, but randomly downsample the normal pings.
dark_df = df[df['Is_Dark_Activity'] == 1]
normal_df = df[df['Is_Dark_Activity'] == 0].sample(frac=0.10, random_state=42) # Keep 10% of normal traffic

final_df = pd.concat([dark_df, normal_df]).sort_values(by=['MMSI', 'BaseDateTime'])

# 5. Export processed data for Power BI
print("Exporting cleaned dataset...")
final_df.to_csv(output_file, index=False)

dark_events = dark_df.shape[0]
print(f"Data Engineering complete! Found {dark_events} REAL 'Dark Fleet' anomalies out of 1.1 Million records.")
print(f"Cleaned dataset saved for Power BI at: {output_file}")
