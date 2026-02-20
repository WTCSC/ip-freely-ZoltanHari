import sys
import ipaddress
import subprocess
import re


def ping_host(ip):
    """
    Pings a single IP address and returns:
    - Status ("UP", "DOWN", or "ERROR")
    - Response time (if available)
    - Error message (if any)
    """

    # Build ping command 
    # -c 1 → send 1 packet
    # -W 1 → wait 1 second for response (can be adjusted if 1 second is too short or too long)
    command = ["ping", "-c", "1", "-W", "1", str(ip)]


    try:
        # Run the ping command
        # stdout=subprocess.PIPE → capture normal output
        # stderr=subprocess.PIPE → capture error output
        # text=True → return output as string instead of bytes
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode == 0:
            # Use re to extract response time (e.g., time=12.3 ms)
            time_match = re.search(r'time[=<]\s?(\d+\.?\d*)', result.stdout)
            if time_match:
                # If time found, return it
                return "UP", f"{time_match.group(1)} ms", None
            # If ping succeeded but time not found, return UP with unknown time
            else:
                return "UP", "Unknown", None
        else:
            # If ping failed, return DOWN with error message
            return "DOWN", None, result.stderr.strip()

    except Exception as e:
        # Catch errors
        return "ERROR", None, str(e)


def main():
    """
    Main function:
    - Validates user input
    - Parses CIDR
    - Scans each host
    """
    # Ensure user provided exactly one arg (CIDR block)
    if len(sys.argv) != 2:
        # If not, print usage instructions and exit
        print("Error: Too many or too few arguments")
        print("Usage: python3 ip_freely.py <CIDR>")
        print("Example: python3 ip_freely.py 192.168.1.0/24")
        sys.exit(1)

    # Get CIDR input from command line
    cidr_input = sys.argv[1]

    try:
        # Convert CIDR string into an IP network object
        # strict=False allows non-network base addresses
        network = ipaddress.ip_network(cidr_input, strict=False)
    except ValueError as e:
        # If invalid CIDR format
        print(f"Invalid CIDR notation: {e}")
        sys.exit(1)

    # Print network information 
    print(f"\nScanning network: {network}")
    print(f"Network address: {network.network_address}")
    print(f"Broadcast address: {network.broadcast_address}")
    print(f"Total hosts: {network.num_addresses - 2}\n")

    # Loop through each host in the network
    for ip in network.hosts():
        print(f"Scanning {ip}...")

        # Pings current IP and retrieves status, response time, and error message(if any)
        status, response_time, error = ping_host(ip)
        
        # Display status results
        if status == "UP":
            print(f"[+] {ip} is UP | Response Time: {response_time}")
        elif status == "DOWN":
            print(f"[-] {ip} is DOWN | Error: {error if error else 'No response'}")
        else:
            print(f"[!] {ip} ERROR | {error}")

    print("\nScan complete.")

# Ensures main() only runs if the script is executed directly
# (not if imported as a module)
if __name__ == "__main__":
    main()