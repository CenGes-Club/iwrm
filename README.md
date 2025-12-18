
# Overview
Integrated Water Reading Management—an embedded systems project for monitoring flood levels in rivers.

## Setup

---
### SSH
First, in order to access the device without using a monitor, we have to setup the SSH connection. To do so, follow these steps:
1. Create AP Point with the following ssid and password:
    ```
   SSID: Postee
   Password: dashiel089
   ```
   Once the AP Point is created, the device will automatically connect to it.
2. Find the IP address of the device by using a network scanner (e.g., arp).
    ```bash
    arp -a
    ```
   It should display a list of connected devices along with their IP addresses. Look for the device with a mac address of  `e4:5f:01:dc:68:9f`:
    ```
    ? (xxx.xxx.xxx.xxx) at e4:5f:01:dc:68:9f on ...
    ```
3. Use SSH to connect to the device using the found IP address:
    ```bash
    ssh postekit@xxx.xxx.xxx.xxx
    ```
    You should know the password.

### Code
1. Clone the repository:
   ```bash
   git clone https://github.com/CenGes-Club/iwrm.git
   ```
2. Run the main file:
    ```bash
    python main.py
    ```