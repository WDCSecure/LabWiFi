#!/usr/bin/env python3
"""
Network Goodput Measurement Tool (TCP/UDP)
Usage:
  Server Mode: ./network_goodput_tool.py --server
  Client Mode: ./network_goodput_tool.py <SERVER_IP> [--udp] [--bitrate 10M] [--iter 10]
"""

import argparse
import subprocess
import time
import json
import statistics
import csv
from datetime import datetime
import logging
import sys
import os

# Create output directory structure with timestamp
session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
base_output_dir = os.path.join("../data", "output", session_timestamp)
client_output_dir = os.path.join(base_output_dir, "client")
server_output_dir = os.path.join(base_output_dir, "server")
os.makedirs(client_output_dir, exist_ok=True)
os.makedirs(server_output_dir, exist_ok=True)

# File paths for client and server logs and reports
CLIENT_LOG_FILE = os.path.join(client_output_dir, "client.log")
SERVER_LOG_FILE = os.path.join(server_output_dir, "server.log")
JSON_LOG_CLIENT = os.path.join(client_output_dir, "client_log.json")
JSON_LOG_SERVER = os.path.join(server_output_dir, "server_log.json")
CSV_REPORT = os.path.join(client_output_dir, "goodput_summary.csv")
RAW_OUTPUT_FILE = os.path.join(client_output_dir, "raw_output.txt")

def setup_logger(log_file, name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

# Client Logger
client_logger = setup_logger(CLIENT_LOG_FILE, "client")
# Server Logger
server_logger = setup_logger(SERVER_LOG_FILE, "server")

def run_server():
    """Run iperf3 server and log output."""
    server_logger.info("Starting iperf3 server...")
    with open(JSON_LOG_SERVER, 'w') as f_json:
        proc = subprocess.Popen(
            ["iperf3", "-s", "-J"],
            stdout=f_json,
            stderr=subprocess.PIPE,
            text=True
        )
    server_logger.info(f"Server PID: {proc.pid}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server_logger.info("Stopping server...")
        proc.terminate()

def run_client(server_ip, udp=False, bitrate="1M", iterations=10):
    """Run iperf3 client tests and generate reports."""
    client_logger.info(f"Starting client tests (UDP={udp}, Bitrate={bitrate})...")
    results = []
    
    for i in range(iterations):
        client_logger.info(f"Test {i+1}/{iterations}")
        cmd = [
            "iperf3", "-c", server_ip,
            "-J", "-t", "10", "-i", "1"
        ]
        if udp:
            cmd.extend(["-u", "-b", bitrate])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            # Print iperf3 output to the console
            print(f"--- Test {i+1} Output ---")
            print(result.stdout)
            
            # Save the raw iperf3 output into a text file
            with open(RAW_OUTPUT_FILE, 'a') as f_raw:
                f_raw.write(f"--- Test {i+1} Raw Output ---\n")
                f_raw.write(result.stdout)
                f_raw.write("\n")
            
            data = json.loads(result.stdout)
            # Append JSON data to the client JSON log
            with open(JSON_LOG_CLIENT, 'a') as f:
                json.dump(data, f)
                f.write('\n')
            
            # Always include the target bitrate in the CSV (even though TCP ignores it)
            test_data = {
                "timestamp": datetime.now().isoformat(),
                "protocol": "UDP" if udp else "TCP",
                "bitrate": bitrate,
            }
            
            if udp:
                test_data.update({
                    "bandwidth": data['end']['sum']['bits_per_second'] / 1e6,
                    "jitter": data['end']['sum']['jitter_ms'],
                    "packet_loss": data['end']['sum']['lost_percent']
                })
            else:
                test_data["bandwidth"] = data['end']['sum_sent']['bits_per_second'] / 1e6
                # For TCP, jitter and packet_loss are not applicable
                test_data["jitter"] = ""
                test_data["packet_loss"] = ""
            
            results.append(test_data)
            client_logger.info(f"Test {i+1} Bandwidth: {test_data['bandwidth']:.2f} Mbps")
        
        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
            client_logger.error(f"Test {i+1} failed: {str(e)}")
    
    # Generate CSV Report with test results and summary statistics
    if results:
        with open(CSV_REPORT, 'w', newline='') as csvfile:
            fieldnames = ["timestamp", "protocol", "bitrate", "bandwidth", "jitter", "packet_loss"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in results:
                writer.writerow(row)
            
            # Compute statistics for bandwidth (only numbers)
            bandwidths = [x['bandwidth'] for x in results if isinstance(x['bandwidth'], (int, float))]
            stats = {
                "min": min(bandwidths),
                "max": max(bandwidths),
                "avg": statistics.mean(bandwidths),
                "std": statistics.stdev(bandwidths) if len(bandwidths) > 1 else 0,
            }
            if udp:
                stats["avg_jitter"] = statistics.mean([x['jitter'] for x in results if x['jitter'] != ""])
                stats["avg_loss"] = statistics.mean([x['packet_loss'] for x in results if x['packet_loss'] != ""])
            
            # Write summary statistics into the CSV as additional rows
            writer.writerow({})  # blank row for separation
            writer.writerow({"timestamp": "Summary", "protocol": "min", "bandwidth": stats["min"]})
            writer.writerow({"timestamp": "Summary", "protocol": "max", "bandwidth": stats["max"]})
            summary_avg = {"timestamp": "Summary", "protocol": "avg", "bandwidth": stats["avg"]}
            if udp:
                summary_avg["jitter"] = stats["avg_jitter"]
                summary_avg["packet_loss"] = stats["avg_loss"]
            writer.writerow(summary_avg)
            writer.writerow({"timestamp": "Summary", "protocol": "std", "bandwidth": stats["std"]})
        
        client_logger.info("\n=== Statistics ===")
        client_logger.info(f"Bandwidth (Mbps): Min={stats['min']:.2f}, Max={stats['max']:.2f}, Avg={stats['avg']:.2f}, Std={stats['std']:.2f}")
        if udp:
            client_logger.info(f"Jitter (ms): Avg={stats['avg_jitter']:.2f}")
            client_logger.info(f"Packet Loss (%): Avg={stats['avg_loss']:.2f}")

def main():
    parser = argparse.ArgumentParser(description="Network Goodput Measurement Tool")
    parser.add_argument("server_ip", nargs='?', help="Server IP address (required for client mode)")
    parser.add_argument("--server", action="store_true", help="Run in server mode")
    parser.add_argument("--udp", action="store_true", help="Use UDP instead of TCP")
    parser.add_argument("--bitrate", default="10M", help="Target bitrate for UDP (e.g., 10M, 500K)")
    parser.add_argument("--iter", type=int, default=10, help="Number of test iterations")
    args = parser.parse_args()
    
    if args.server:
        run_server()
    else:
        if not args.server_ip:
            print("Error: Server IP required in client mode.")
            sys.exit(1)
        run_client(args.server_ip, args.udp, args.bitrate, args.iter)

if __name__ == "__main__":
    main()
