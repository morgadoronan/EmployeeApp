import cv2
import numpy as np
import json
import os
import datetime
import time

# Global variables
drawing = False
ix, iy = -1, -1
zones = [] # List to store zones: [(x, y, w, h, "type")]
current_zone_type = "operator" # 'operator' or 'drawer'
CONFIG_FILE = "zones_config.json"
LOG_FILE = "security_log.txt"
last_log_time = 0
LOG_COOLDOWN = 2 # Seconds between logs to avoid flooding

def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing, zones, current_zone_type

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img_copy = param.copy()
            cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 2)
            cv2.imshow("Security Feed", img_copy)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.rectangle(param, (ix, iy), (x, y), (0, 255, 0), 2)
        
        # Save zone coordinates
        x_start = min(ix, x)
        y_start = min(iy, y)
        w = abs(x - ix)
        h = abs(y - iy)
        
        # Only add valid zones
        if w > 10 and h > 10:
            zones.append((x_start, y_start, w, h, current_zone_type))
            print(f"Zone '{current_zone_type}' added!")
            
            # Switch to next zone type automatically for convenience
            if current_zone_type == "operator":
                current_zone_type = "drawer"
                print("Now draw the DRAWER zone.")
            else:
                current_zone_type = "drawer" # Keep adding drawers or switch to done? Original logic had 'drawer' then loop/finish.
                # Let's keep it simple: Operator -> Drawer -> Done (user presses Q)
                print("Setup step complete. Press 'q' to finish or draw another Drawer zone.")

def check_motion(fg_mask, zone):
    x, y, w, h, _ = zone
    roi = fg_mask[y:y+h, x:x+w]
    count = cv2.countNonZero(roi)
    # Sensitivity threshold: adjusts how much motion triggers "presence"
    return count > 500 

def save_config(url, zones_data):
    try:
        data = {
            "rtsp_url": url,
            "zones": zones_data
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        print(f"Error saving config: {e}")

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return None, []
    try:
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            # Check if it's the new dictionary format or old list format
            if isinstance(data, list):
                return "", [tuple(z) for z in data] # Old format, no URL
            else:
                return data.get("rtsp_url", ""), [tuple(z) for z in data.get("zones", [])]
    except Exception as e:
        print(f"Error loading config: {e}")
        return None, []

def log_alert():
    global last_log_time
    current_time = time.time()
    
    if current_time - last_log_time > LOG_COOLDOWN:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(LOG_FILE, "a") as f:
                f.write(f"[{timestamp}] ALERT: Unauthorized Access Detected!\n")
            # print(f"Log written: {timestamp}") 
            last_log_time = current_time
        except Exception as e:
            print(f"Error writing log: {e}")

def main():
    global current_zone_type, zones
    
    cv2.namedWindow("Security Feed")
    
    # Check for existing config
    loaded_url, loaded_zones = load_config()
    setup_needed = True
    rtsp_url = ""

    if loaded_zones: # If we have zones, we consider it a valid config
        print(f"\nFound existing configuration with {len(loaded_zones)} zones.")
        if loaded_url:
            print(f"Saved Camera URL: {loaded_url}")
        
        choice = input("Do you want to use the saved configuration? (y/n): ").strip().lower()
        if choice == 'y':
            zones = loaded_zones
            rtsp_url = loaded_url
            setup_needed = False
            print("Configuration loaded. Starting monitoring...")
        else:
            print("Starting new configuration setup...")

    if setup_needed:
        url_input = input("\nEnter the RTSP URL (or press Enter for default webcam): ").strip()
        if url_input:
            rtsp_url = url_input
        else:
            rtsp_url = 0 # Default webcam index if empty

    # Initialize Camera
    print(f"Connecting to camera: {rtsp_url if rtsp_url != 0 else 'Default Webcam'}...")
    cap = cv2.VideoCapture(rtsp_url)
    
    if not cap.isOpened():
        print("Error: Could not open camera source.")
        return

    # Background subtractor
    backSub = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=True)

    # Read first frame for setup if needed
    if setup_needed:
        ret, initial_frame = cap.read()
        if not ret:
            print("Error reading video.")
            return
            
        cv2.setMouseCallback("Security Feed", draw_rectangle, initial_frame)
        
        print("--- SETUP MODE ---")
        print("1. Draw a rectangle over the OPERATOR area (where the person stands).")
        print("2. Draw a rectangle over the DRAWER area (the cash drawer).")
        print("3. Press 'r' to reset zones, 'q' to finish setup.")

        # Setup Loop
        while True:
            temp_frame = initial_frame.copy()
            for z in zones:
                x, y, w, h, ztype = z
                color = (0, 255, 0) if ztype == "operator" else (0, 0, 255)
                cv2.rectangle(temp_frame, (x, y), (x+w, y+h), color, 2)
                cv2.putText(temp_frame, ztype.upper(), (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
            cv2.imshow("Security Feed", temp_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                zones.clear()
                current_zone_type = "operator"
                print("Zones reset. Draw OPERATOR zone again.")
        
        # Save after setup
        if zones:
            save_config(rtsp_url if rtsp_url != 0 else "", zones)

    # Monitoring Loop
    print("--- MONITORING STARTED ---")
    
    # If we skipped setup, we haven't read a frame yet (or we discarded initial_frame)
    # Just enter the loop.
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Apply Background Subtraction
        fgMask = backSub.apply(frame)
        
        # Remove shadows (gray color) to keep only hard white (moving objects)
        _, fgMask = cv2.threshold(fgMask, 200, 255, cv2.THRESH_BINARY)
        
        operator_present = False
        drawer_access = False
        
        for z in zones:
            x, y, w, h, ztype = z
            has_motion = check_motion(fgMask, z)
            
            # Draw zones
            color = (0, 255, 0) if ztype == "operator" else (0, 0, 255)
            thickness = 2
            
            if has_motion:
                thickness = 4 # Highlight moving zones
                if ztype == "operator":
                    operator_present = True
                elif ztype == "drawer":
                    drawer_access = True
            
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, thickness)
            cv2.putText(frame, ztype.upper(), (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # LOGIC: ALERT if Drawer Access AND NO Operator
        alert_status = "SECURE"
        alert_color = (0, 255, 0)
        
        if drawer_access and not operator_present:
            alert_status = "ALERT: UNAUTHORIZED ACCESS!"
            alert_color = (0, 0, 255)
            log_alert() # Log the event
            # You could play a sound here
            
        elif drawer_access and operator_present:
            alert_status = "Authorized Access"
            alert_color = (0, 255, 255) # Yellow

        # Display Status overlay
        cv2.putText(frame, f"STATUS: {alert_status}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, alert_color, 3)
        
        # Show debug windows
        cv2.imshow("Security Feed", frame)
        cv2.imshow("Motion Mask", fgMask) # Useful for debugging ROI sensitivity
        
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

import traceback

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        error_msg = traceback.format_exc()
        print("\n\nCRITICAL ERROR OCCURRED:")
        print(error_msg)
        
        with open("crash_log.txt", "w") as f:
            f.write(error_msg)
        print("\nError info saved to 'crash_log.txt'.")
        
    input("\nPress Enter to exit...")
