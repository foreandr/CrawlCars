import threading
import signal
import sys
import hyperSel
import hyperSel.sniffer_utilities
import site_autotrader
import site_caravana
import time

# List to keep track of threads
threads = []

# Flag to indicate when to stop threads
stop_flag = threading.Event()

def run_in_thread(target, name):
    """
    Wraps the target function to stop it gracefully if stop_flag is set.
    """
    def wrapper():
        try:
            print(f"Starting thread: {name}")
            target()
        except Exception as e:
            if not stop_flag.is_set():
                print(f"Error in thread {name}: {e}")
        finally:
            print(f"Thread {name} completed.")

    thread = threading.Thread(target=wrapper, name=name)
    threads.append(thread)
    thread.start()

def main():
    # Start site threads using lambda syntax
    run_in_thread(lambda: site_autotrader.main(), "Autotrader Thread")
    run_in_thread(lambda: site_caravana.main(), "Carvana Thread")
    # Add more sites as needed
    # run_in_thread(lambda: other_site.main(), "Other Site Thread")

def stop_all_threads():
    """Stops all threads by setting the stop flag and joining each thread."""
    print("\nStopping all threads...")
    stop_flag.set()
    for thread in threads:
        thread.join()
    print("All threads stopped.")
    sys.exit(0)

def signal_handler(signal, frame):
    """Signal handler for Ctrl-C."""
    print("\nCtrl-C detected. Exiting gracefully...")
    stop_all_threads()

# Register the signal handler for Ctrl-C
signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    main()
    # Keep the main thread running and waiting for Ctrl-C
    print("Press Ctrl-C to stop.")
    try:
        while not stop_flag.is_set():
            time.sleep(0.1)  # Wait briefly and check stop_flag
    except KeyboardInterrupt:
        stop_all_threads()
