import csv
import sys
import os

def analyze_battery_discharge(file_path: str, target_voltage: float) -> None:
    """
    Analyzes battery discharge data from a CSV file to find the remaining 
    capacity percentage when a specific target voltage is reached.
    """
    total_capacity_ah = 0.0
    cap_at_target = None
    voltage_at_target = None
    
    prev_time = None

    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' was not found.")
        sys.exit(1)

    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    current_time = float(row['Time(s)'])
                    voltage = float(row['Voltage(V)'])
                    current = float(row['Current(A)'])
                except (ValueError, KeyError):
                    continue  # Skip rows with missing or malformed data

                # Calculate delta time (dt)
                if prev_time is None:
                    dt = 0.0
                else:
                    dt = current_time - prev_time
                
                prev_time = current_time

                # Accumulate discharged capacity (Ah)
                # Ah = Current (A) * Time (hours)
                total_capacity_ah += (current * dt) / 3600.0

                # Check if we hit the target voltage for the first time
                if cap_at_target is None and voltage <= target_voltage:
                    cap_at_target = total_capacity_ah
                    voltage_at_target = voltage

    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        sys.exit(1)

    # Print results
    if total_capacity_ah > 0:
        if cap_at_target is not None:
            perc_remaining = (1 - (cap_at_target / total_capacity_ah)) * 100
            
            print(f"File: {file_path}")
            print(f"Total Capacity: {total_capacity_ah:.4f} Ah ({total_capacity_ah * 1000:.1f} mAh)")
            print(f"Capacity discharged at {target_voltage}V: {cap_at_target:.4f} Ah ({cap_at_target * 1000:.1f} mAh)")
            print(f"Voltage at that point: {voltage_at_target:.4f} V")
            print(f"Percentage remaining: {perc_remaining:.2f}%")
        else:
            print(f"File: {file_path}")
            print(f"Voltage never dropped to or below {target_voltage}V.")
            print(f"Total Capacity measured: {total_capacity_ah:.4f} Ah ({total_capacity_ah * 1000:.1f} mAh)")
    else:
        print("No valid capacity data could be calculated.")

if __name__ == "__main__":
    # Ensure at least the filename is provided
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <path_to_csv_file> [target_voltage]")
        print(f"Example: python {sys.argv[0]} cameron_sino_850mah.csv 3.63")
        sys.exit(1)
        
    csv_file = sys.argv[1]
    
    # Allow overriding the target voltage via a second argument (defaults to 3.63)
    threshold_voltage = 3.63
    if len(sys.argv) >= 3:
        try:
            threshold_voltage = float(sys.argv[2])
        except ValueError:
            print("Error: target_voltage must be a valid number.")
            sys.exit(1)
            
    analyze_battery_discharge(csv_file, threshold_voltage)
