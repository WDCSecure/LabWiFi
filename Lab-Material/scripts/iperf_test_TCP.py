#!/usr/bin/env python3

import subprocess
import time
import json
import statistics
import csv
import argparse

def main():
    # Set up command-line arguments
    parser = argparse.ArgumentParser(
        description="Run iperf3 tests against a given server, parse results, and save them to a CSV file."
    )
    parser.add_argument(
        "server_ip",
        help="IP address or hostname of the iperf3 server. (e.g., 127.0.0.1, 192.168.1.10, etc.)"
    )
    parser.add_argument(
        "--num-tests",
        type=int,
        default=10,
        help="Number of times to run the iperf3 client test (default: 10)."
    )
    parser.add_argument(
        "--out-csv",
        default="iperf_results.csv",
        help="Name of the CSV file where results will be saved (default: iperf_results.csv)."
    )

    args = parser.parse_args()
    
    server_ip = args.server_ip
    num_tests = args.num_tests
    csv_filename = args.out_csv

    print(f"Server IP: {server_ip}")
    print(f"Number of tests: {num_tests}")
    print(f"Output CSV file: {csv_filename}")

    # 1. Start the iperf3 server in the background
    print("Starting iperf3 server...")
    server_proc = subprocess.Popen(
        ["iperf3", "-s"], 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL
    )
    
    # Wait a couple seconds for the server to start
    time.sleep(2)
    
    # 2. Run client tests and collect results
    bandwidth_results = []
    for i in range(num_tests):
        print(f"Running iperf3 test #{i+1}")
        try:
            # Run iperf3 client in JSON mode
            client_cmd = ["iperf3", "-c", server_ip, "-J"]
            result = subprocess.run(
                client_cmd, 
                capture_output=True, 
                text=True, 
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Error running iperf3 client (test #{i+1}): {e}")
            continue
        
        # 3. Parse JSON output to extract bandwidth
        try:
            output_json = json.loads(result.stdout)
            # Typically for client->server throughput, we look at "sum_sent"
            bps = output_json["end"]["sum_sent"]["bits_per_second"]
            # Convert to Mbps
            mbps = bps / 1e6
            print(f"  Bandwidth: {mbps:.2f} Mbps")
            bandwidth_results.append(mbps)
        except (KeyError, json.JSONDecodeError) as e:
            print(f"  Could not parse iperf3 JSON output (test #{i+1}): {e}")
    
    # 4. Stop the server
    print("Stopping iperf3 server...")
    server_proc.terminate()
    try:
        server_proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        server_proc.kill()

    if not bandwidth_results:
        print("No valid results collected.")
        return

    # 5. Compute statistics
    mn = min(bandwidth_results)
    mx = max(bandwidth_results)
    avg = statistics.mean(bandwidth_results)
    # If you consider all tests to be the "population," use pstdev. If it's just a sample, use stdev.
    stdev = statistics.pstdev(bandwidth_results)

    print("\n=== Statistics ===")
    print(f"Min bandwidth : {mn:.2f} Mbps")
    print(f"Max bandwidth : {mx:.2f} Mbps")
    print(f"Avg bandwidth : {avg:.2f} Mbps")
    print(f"Std bandwidth : {stdev:.2f} Mbps")

    # 6. Save results to a CSV file
    with open(csv_filename, mode="w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Test #", "Bandwidth (Mbps)"])
        for i, val in enumerate(bandwidth_results, start=1):
            writer.writerow([i, val])
        
        # Write summary stats at the end
        writer.writerow([])
        writer.writerow(["Min (Mbps)", "Max (Mbps)", "Avg (Mbps)", "Std (Mbps)"])
        writer.writerow([mn, mx, avg, stdev])
    
    print(f"\nResults saved to {csv_filename}")

if __name__ == "__main__":
    main()

