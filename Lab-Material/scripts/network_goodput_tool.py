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
import threading
import signal

# Create output directory structure with timestamp
session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
base_output_dir = os.path.join("../data1", "output", session_timestamp)
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

client_logger = setup_logger(CLIENT_LOG_FILE, "client")
server_logger = setup_logger(SERVER_LOG_FILE, "server")


def run_server():
    """Run iperf3 server with clean output handling."""
    server_logger.info("Starting iperf3 server...")
    
    def handler(signum, frame):
        server_logger.info("Shutting down server...")
        proc.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, handler)

    with open(JSON_LOG_SERVER, 'a') as f_json:
        proc = subprocess.Popen(
            ["iperf3", "-s", "-J"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        server_logger.info(f"Server PID: {proc.pid}")

        def handle_stderr(stderr):
            while True:
                line = stderr.readline()
                if not line: break
                server_logger.error(line.strip())

        stderr_thread = threading.Thread(target=handle_stderr, args=(proc.stderr,))
        stderr_thread.daemon = True
        stderr_thread.start()

        try:
            while True:
                line = proc.stdout.readline()
                if not line: 
                    time.sleep(0.1)
                    continue
                
                # Write raw JSON to file
                f_json.write(line)
                f_json.flush()
                
                # Parse and display clean output
                try:
                    data = json.loads(line)
                    if 'start' in data:
                        print(f"\n📡 Test started from {data['start']['connecting_to']['host']}")
                    if 'end' in data:
                        sum_sent = data['end']['sum_sent']
                        sum_recv = data['end']['sum_received']
                        print(f"✅ Test completed - Sent: {sum_sent['bits_per_second']/1e6:.2f} Mbps | Received: {sum_recv['bits_per_second']/1e6:.2f} Mbps")
                except json.JSONDecodeError:
                    pass

        except KeyboardInterrupt:
            handler(signal.SIGINT, None)

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
            
            # Print clean output to terminal
            data = json.loads(result.stdout)
            print(f"\n🔁 Test {i+1}/{iterations}")
            
            if udp:
                stats = data['end']['sum']
                print(f"📤 Sent: {stats['bits_per_second']/1e6:.2f} Mbps")
                print(f"📥 Received: {stats['bits_per_second']/1e6:.2f} Mbps")
                print(f"📡 Jitter: {stats['jitter_ms']:.2f} ms")
                print(f"🛑 Packet Loss: {stats['lost_percent']:.2f}%")
                
                test_data = {
                    "timestamp": datetime.now().isoformat(),
                    "protocol": "UDP",
                    "bitrate": bitrate,
                    "statistic": "",
                    "bandwidth": stats['bits_per_second'] / 1e6,
                    "jitter": stats['jitter_ms'],
                    "packet_loss": stats['lost_percent']
                }
            else:
                sent = data['end']['sum_sent']
                received = data['end']['sum_received']
                print(f"📤 Sent: {sent['bits_per_second']/1e6:.2f} Mbps")
                print(f"📥 Received: {received['bits_per_second']/1e6:.2f} Mbps")
                
                test_data = {
                    "timestamp": datetime.now().isoformat(),
                    "protocol": "TCP",
                    "bitrate": "",
                    "statistic": "",
                    "bandwidth": sent['bits_per_second'] / 1e6,
                    "jitter": "",
                    "packet_loss": ""
                }
            
            # Append to results list
            results.append(test_data)
            
            # Log raw data to files
            with open(RAW_OUTPUT_FILE, 'a') as f_raw:
                f_raw.write(f"\n--- Test {i+1} ---\n")
                f_raw.write(result.stdout)
                
            with open(JSON_LOG_CLIENT, 'a') as f_json:
                json.dump(data, f_json)
                f_json.write('\n')
            
            client_logger.info(f"Test {i+1} Bandwidth: {test_data['bandwidth']:.2f} Mbps")

        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
            error_msg = f"Test {i+1} failed: {str(e)}"
            print(f"❌ {error_msg}")
            client_logger.error(error_msg)
            continue  # Skip to next iteration

    # Generate CSV report only if we have results
    if results:
        # [Keep existing CSV generation code]
        # Generate CSV Report with test results and summary statistics
        with open(CSV_REPORT, 'w', newline='') as csvfile:
            fieldnames = ["timestamp", "protocol", "bitrate", "statistic", "bandwidth", "jitter", "packet_loss"]
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
                jitters = [x['jitter'] for x in results if x['jitter'] != ""]
                losses = [x['packet_loss'] for x in results if x['packet_loss'] != ""]
                stats["avg_jitter"] = statistics.mean(jitters) if jitters else 0
                stats["avg_loss"] = statistics.mean(losses) if losses else 0
            
            # Write summary statistics into the CSV
            writer.writerow({})  # Blank row for separation
            summary_base = {
                "timestamp": "Summary",
                "protocol": "UDP" if udp else "TCP",
                "bitrate": bitrate if udp else ""
            }
            writer.writerow({**summary_base, "statistic": "min", "bandwidth": stats["min"]})
            writer.writerow({**summary_base, "statistic": "max", "bandwidth": stats["max"]})
            avg_row = {**summary_base, "statistic": "avg", "bandwidth": stats["avg"]}
            if udp:
                avg_row.update({"jitter": stats["avg_jitter"], "packet_loss": stats["avg_loss"]})
            writer.writerow(avg_row)
            writer.writerow({**summary_base, "statistic": "std", "bandwidth": stats["std"]})
        
        # Print final summary to terminal
        print("\n📊 Final Summary:")
        print(f"  Bandwidth (Mbps): Min={stats['min']:.2f}, Max={stats['max']:.2f}, Avg={stats['avg']:.2f}, Std={stats['std']:.2f}")
        if udp:
            print(f"  Jitter (ms): Avg={stats['avg_jitter']:.2f}")
            print(f"  Packet Loss (%): Avg={stats['avg_loss']:.2f}")
    else:
        print("⚠️  No successful tests to report")



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