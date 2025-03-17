# Lab WiFi for the WD2DCS course

![Polito Logo](resources/logo_polito.jpg)

This repository contains all the materials and documentation for the WiFi lab experiment conducted as part of the **Wireless and Device-to-Device Communication Security** course.

## Overview

In this lab, we evaluated the performance of WiFi networks by measuring goodput in different scenarios using tools like `iperf/iperf3`, `Wireshark`, and other network utilities.

The lab required setting up a testbed to perform multiple experiments including:
- **Both Hosts Connected via Ethernet**
- **Both Hosts Connected via WiFi**
- **Mixed Mode (one host on Ethernet and one on WiFi)**

For each scenario, tests were repeated (e.g., 10 times) to capture statistical metrics such as the minimum, maximum, average, and standard deviation of the measured goodput. In addition, traffic captures were used to analyze sequence numbers, round-trip times, and throughput variations.

> [!NOTE]
> The detailed lab report, including all experimental results and analysis, can be found [here](Report/LabWiFi.pdf).

## Lab Objectives & Requirements

The primary objectives of the lab were to:
- **Measure Network Goodput:** Calculate the efficiency of data transfer by accounting for protocol overheads.
- **Test Different Configurations:** Compare performance over Ethernet, WiFi, and mixed configurations.
- **Analyze Results:** Use tools such as Wireshark to validate results, visualize TCP sequence graphs, and understand packet-level behavior.

**Tools:**
  - [**`iperf`**](https://sourceforge.net/projects/iperf2/) | [**`iperf3`**](https://iperf.fr)**:** To run throughput tests
  - [**`Wireshark`**](https://www.wireshark.org)**:** For packet capture and analysis  
  - [**`tcpdump`**](https://www.tcpdump.org)**:** To enforce monitor mode on WiFi when necessary  
  - [**`zizzania`**](https://github.com/cyrus-and/zizzania)**:** Additional tool for testing (may be optional)  

## Experiment Procedure

1. **Testbed Setup:** Configure two hosts under three scenarios (Ethernet, WiFi, Mixed).
2. **Goodput Measurement:** Use `iperf/iperf3` to test data transfer.
3. **Data Collection & Analysis:** Capture traffic using Wireshark.
4. **Report Preparation:** Prepare a detailed lab report using LaTeX.

For detailed instructions, please refer to the dedicated `README.md` files in the subdirectories:
- [**`Lab-Material/README.md`**](Lab-Material/README.md)
- [**`Report/README.md`**](Report/README.md)

## Authors

| Name              | GitHub                                                                                                               | LinkedIn                                                                                                                                  | Email                                                                                                            |
| ----------------- | -------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Andrea Botticella | [![GitHub](https://img.shields.io/badge/GitHub-Profile-informational?logo=github)](https://github.com/Botti01)       | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?logo=linkedin)](https://www.linkedin.com/in/andrea-botticella-353169293/) | [![Email](https://img.shields.io/badge/Email-Send-blue?logo=gmail)](mailto:andrea.botticella@studenti.polito.it) |
| Elia Innocenti    | [![GitHub](https://img.shields.io/badge/GitHub-Profile-informational?logo=github)](https://github.com/eliainnocenti) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?logo=linkedin)](https://www.linkedin.com/in/eliainnocenti/)               | [![Email](https://img.shields.io/badge/Email-Send-blue?logo=gmail)](mailto:elia.innocenti@studenti.polito.it)    |
| Renato Mignone    | [![GitHub](https://img.shields.io/badge/GitHub-Profile-informational?logo=github)](https://github.com/RenatoMignone) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?logo=linkedin)](https://www.linkedin.com/in/renato-mignone/)              | [![Email](https://img.shields.io/badge/Email-Send-blue?logo=gmail)](mailto:renato.mignone@studenti.polito.it)    |
| Simone Romano     | [![GitHub](https://img.shields.io/badge/GitHub-Profile-informational?logo=github)](https://github.com/sroman0)       | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?logo=linkedin)](https://www.linkedin.com/in/simone-romano-383277307/)     | [![Email](https://img.shields.io/badge/Email-Send-blue?logo=gmail)](mailto:simone.romano@studenti.polito.it)     |
