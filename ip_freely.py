import sys
import ipaddress
import subprocess
import re


def ping_host(ip):
    command = ["ping", "-c", "1", "-W", "1", str(ip)]

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode == 0:
            time_match = re.search(r'time[=<]\s?(\d+\.?\d*)', result.stdout)
            if time_match:
                return "UP", f"{time_match.group(1)} ms", None
            else:
                return "UP", "Unknown", None
        else:
            return "DOWN", None, result.stderr.strip()

    except Exception as e:
        return "ERROR", None, str(e)


def main():
    if len(sys.argv) != 2:
        print("Usage: python ip_freely.py <CIDR>")
        print("Example: python ip_freely.py 192.168.1.0/24")
        sys.exit(1)

    cidr_input = sys.argv[1]

    try:
        network = ipaddress.ip_network(cidr_input, strict=False)
    except ValueError as e:
        print(f"Invalid CIDR notation: {e}")
        sys.exit(1)

    print(f"\nScanning network: {network}")
    print(f"Network address: {network.network_address}")
    print(f"Broadcast address: {network.broadcast_address}")
    print(f"Total hosts: {network.num_addresses - 2}\n")

    for ip in network.hosts():
        print(f"Scanning {ip}...")

        status, response_time, error = ping_host(ip)

        if status == "UP":
            print(f"[+] {ip} is UP | Response Time: {response_time}")
        elif status == "DOWN":
            print(f"[-] {ip} is DOWN | Error: {error if error else 'No response'}")
        else:
            print(f"[!] {ip} ERROR | {error}")

    print("\nScan complete.")


if __name__ == "__main__":
    main()