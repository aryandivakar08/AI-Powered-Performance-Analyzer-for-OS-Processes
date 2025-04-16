import psutil
import pandas as pd
import time
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from joblib import dump

# Setup live plotting
plt.ion()

def collect_process_data():
    print("⏳ Collecting system process data (every 5 seconds)...")
    data = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            data.append(proc.info)
        except psutil.NoSuchProcess:
            continue
    return pd.DataFrame(data)

def visualize(df):
    plt.clf()
    df_grouped = df.groupby('name').agg({'cpu_percent': 'mean', 'memory_percent': 'mean'}).reset_index()

    sns.lineplot(x='cpu_percent', y='memory_percent', data=df_grouped, marker="o")
    plt.title('Live CPU vs Memory Usage per Process (Average)')
    plt.xlabel('CPU Usage (%)')
    plt.ylabel('Memory Usage (%)')
    plt.tight_layout()
    plt.pause(0.1)

def detect_anomalies(df):
    features = df[['cpu_percent', 'memory_percent']].fillna(0)
    model = IsolationForest(contamination=0.05, random_state=42)
    df['anomaly'] = model.fit_predict(features)
    return df, model

def run_analyzer():
    print("⌛ Waiting 3 seconds before starting live monitoring...")
    time.sleep(3)
    
    while True:
        try:
            df = collect_process_data()
            df, model = detect_anomalies(df)
            visualize(df)

            print("\n🚨 Anomalous Processes Detected:")
            anomalies = df[df['anomaly'] == -1][['pid', 'name', 'cpu_percent', 'memory_percent']]
            print(anomalies if not anomalies.empty else "✅ No anomalies detected.")

            time.sleep(5)
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user.")
            break

if _name_ == "_main_":
    run_analyzer()
