# Lab WiFi Material

This directory contains all the resources needed to complete the WiFi lab assignment for the **Wireless and Device-to-Device Communication Security** course.

## Contents

- **data/**  
  Contains experimental data:
  - **graphs/**: Graphical outputs for various test scenarios (e.g., WiFi-TCP, WiFi-UDP, ETH-TCP, Mixed modes).
  - **output/**: Logs, raw outputs, and statistical summaries from multiple test runs.

- **scripts/**  
  Contains utility scripts such as [`network_goodput_tool.py`](scripts/network_goodput_tool.py) which can be used to automate tests and process the output data.

## Experiment Procedure

1. **Testbed Setup:**
   - Configure two hosts under three scenarios:
     - **Scenario 1:** Both hosts connected via Ethernet.
     - **Scenario 2:** Both hosts connected via WiFi.
     - **Scenario 3:** Mixed mode – one host on Ethernet, the other on WiFi.
   - Verify network configurations with:
     - **Linux:** `ethtool` (Ethernet) and `iw`/`iwconfig` (WiFi).
     - **MacOS:** `ifconfig` and `sudo wdutil info`.
     - **Windows:** PowerShell commands like `Get-NetAdapter` and `netsh wlan show interfaces`.

2. **Goodput Measurement:**
   - Use iperf/iperf3 to test data transfer. For example:
     ```bash
     iperf -c <Server_IP> -i 1
     ```
   - Repeat tests (e.g., 10 iterations) to compute statistical measures:
     - **Average, Minimum, Maximum, Standard Deviation.**
   - Account for protocol overheads:
     - Typical Ethernet TCP efficiency is around 94.9% and UDP around 95.7%, whereas WiFi scenarios show lower performance due to additional overheads.

3. **Data Collection & Analysis:**
   - Capture traffic using Wireshark to analyze:
     - TCP sequence evolution.
     - Round-trip times.
     - Throughput variations.
   - Compare experimental results with theoretical predictions and discuss any discrepancies (e.g., impact of interference or changing channel conditions).

This directory is your go-to location for all materials related to the experimental side of the lab.
