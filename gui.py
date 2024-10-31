import customtkinter as ctk
import tkinter as tk
import json
import threading
import signal
import sys
import webbrowser
from datetime import datetime

# Constants for pagination
BATCH_SIZE = 20
SCROLL_THRESHOLD = 0.8  # Load more data when scrollbar is within 20% of the bottom

# Sample data loading function (replace with JSON file loading if needed)
def load_car_data():
    return load_crawl_data()

def load_crawl_data(filepath="./logs/crawl_data.json"):
    with open(filepath, "r") as file:
        data = json.load(file)
    return data

# Initialize the main application window
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Car Listings Viewer")
        self.geometry("1400x800")
        
        # Stop flag for controlled exit
        self.stop_flag = threading.Event()
        
        # Title and Search Area (Top)
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(self, textvariable=self.search_var, width=400, placeholder_text="Search by title")
        self.search_entry.grid(row=0, column=1, padx=(20, 10), pady=20, sticky="w")

        self.search_button = ctk.CTkButton(self, text="Search", command=self.search, width=100)
        self.search_button.grid(row=0, column=2, padx=10, pady=20, sticky="w")

        # Filters Section (Left Side)
        self.filter_frame = ctk.CTkFrame(self, width=200)
        self.filter_frame.grid(row=1, column=0, rowspan=2, padx=20, pady=10, sticky="nsw")

        self.self_driving_var = ctk.BooleanVar(value=True)
        self.self_driving_checkbox = ctk.CTkCheckBox(self.filter_frame, text="Self-Driving", variable=self.self_driving_var, command=self.apply_filters)
        self.self_driving_checkbox.pack(pady=(10, 5), anchor="w")

        self.model_x_var = ctk.BooleanVar(value=True)
        self.model_x_checkbox = ctk.CTkCheckBox(self.filter_frame, text="Model X", variable=self.model_x_var, command=self.apply_filters)
        self.model_x_checkbox.pack(pady=(5, 5), anchor="w")

        self.long_range_var = ctk.BooleanVar(value=True)
        self.long_range_checkbox = ctk.CTkCheckBox(self.filter_frame, text="Long Range", variable=self.long_range_var, command=self.apply_filters)
        self.long_range_checkbox.pack(pady=(5, 15), anchor="w")

        # Year Filter Dropdown
        self.year_label = ctk.CTkLabel(self.filter_frame, text="Newer than:")
        self.year_label.pack(anchor="w")

        years = [str(year) for year in range(2000, datetime.now().year + 1)]
        self.year_var = ctk.StringVar(value="2022")
        self.year_dropdown = ctk.CTkComboBox(self.filter_frame, values=years, variable=self.year_var, command=self.apply_filters)
        self.year_dropdown.pack(anchor="w", pady=(0, 20))

        # Sorting Dropdown
        self.sort_var = ctk.StringVar(value="Sort by Price")
        self.sort_dropdown = ctk.CTkComboBox(self.filter_frame, values=["Lowest to Highest", "Highest to Lowest"], 
                                             command=self.sort_by_price_dropdown, variable=self.sort_var)
        self.sort_dropdown.pack(anchor="w")

        # Data Display Frame (Center)
        self.data_frame = ctk.CTkScrollableFrame(self, width=1000, height=600)
        self.data_frame.grid(row=1, column=1, rowspan=2, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Scrollbar (Right Side)
        self.scrollbar = tk.Scrollbar(self, orient="vertical")
        self.scrollbar.grid(row=1, column=3, rowspan=2, sticky="ns", padx=(5, 20))  # Positioned at far right

        # Configure scrollbar to work with data_frame
        self.scrollbar.config(command=self.data_frame._parent_canvas.yview)
        self.data_frame._parent_canvas.config(yscrollcommand=self.scrollbar.set)
        
        # Bind scrollbar to trigger on_scroll when moving close to the bottom
        self.scrollbar.bind("<B1-Motion>", self.on_scroll)
        self.scrollbar.bind("<ButtonRelease-1>", self.on_scroll)
        
        # Load initial data
        self.car_data = load_car_data()
        self.filtered_data = self.remove_duplicates(self.car_data)  # Remove duplicates initially
        self.display_data = []  # Stores currently displayed data
        self.current_batch = 0  # Track the current batch for pagination
        self.apply_filters()  # Apply initial filters

    def remove_duplicates(self, data):
        """Remove duplicates based on the URL field."""
        unique_data = []
        seen_urls = set()
        for entry in data:
            url = entry.get("url")
            if url and url not in seen_urls:
                unique_data.append(entry)
                seen_urls.add(url)
        return unique_data

    def apply_filters(self, _=None):
        """Apply filters based on user-selected criteria."""
        year_threshold = int(self.year_var.get())
        self.filtered_data = [
            entry for entry in self.car_data
            if (not self.self_driving_var.get() or self.is_self_driving(entry["title"])) and
               (not self.model_x_var.get() or "model x" in entry["title"].lower()) and
               (not self.long_range_var.get() or "long range" in entry["title"].lower()) and
               (int(entry.get("year", 0)) >= year_threshold)
        ]
        self.current_batch = 0
        self.display_data = []
        self.load_data()

    def is_self_driving(self, title):
        """Check for self-driving keywords in the title."""
        keywords = ["fsd", "self driving", "self-driving", "autopilot"]
        return any(keyword in title.lower() for keyword in keywords)

    def load_data(self, append=False):
        """Load a batch of data for display."""
        start_index = self.current_batch * BATCH_SIZE
        end_index = start_index + BATCH_SIZE
        batch = self.filtered_data[start_index:end_index]

        if not append:
            for widget in self.data_frame.winfo_children():
                widget.destroy()
            self.display_data = []
        
        colors = ["#2E2E2E", "#393939"]
        
        for index, entry in enumerate(batch):
            entry_frame = ctk.CTkFrame(self.data_frame, corner_radius=10, fg_color=colors[(index + len(self.display_data)) % 2])
            entry_frame.pack(fill="x", padx=5, pady=5)
            
            # Display entry data in two rows
            title_label = ctk.CTkLabel(entry_frame, text=f"Title: {entry.get('title', 'N/A')}", font=("Arial", 14, "bold"))
            title_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

            price_label = ctk.CTkLabel(entry_frame, text=f"Price: ${entry.get('price', 'N/A')}", font=("Arial", 12))
            price_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

            year_label = ctk.CTkLabel(entry_frame, text=f"Year: {entry.get('year', 'N/A')}", font=("Arial", 12))
            year_label.grid(row=0, column=2, padx=10, pady=5, sticky="w")

            # Second row for additional data
            body_type_label = ctk.CTkLabel(entry_frame, text=f"Body Type: {entry.get('Body Type', 'N/A')}", font=("Arial", 12))
            body_type_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

            drivetrain_label = ctk.CTkLabel(entry_frame, text=f"Drivetrain: {entry.get('Drivetrain', 'N/A')}", font=("Arial", 12))
            drivetrain_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")

            engine_label = ctk.CTkLabel(entry_frame, text=f"Engine: {entry.get('Engine', 'N/A')}", font=("Arial", 12))
            engine_label.grid(row=1, column=2, padx=10, pady=5, sticky="w")

            # Clickable URL
            url = entry.get('url', 'N/A')
            url_label = ctk.CTkLabel(entry_frame, text="Link", font=("Arial", 12), fg_color="blue")
            url_label.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky="w")
            url_label.bind("<Button-1>", lambda e, url=url: webbrowser.open(url))

            self.display_data.append(entry)
        
        self.current_batch += 1  # Update the batch counter

    def on_scroll(self, event):
        """Load the next batch of data when close to the bottom."""
        if self.scrollbar.get()[1] >= SCROLL_THRESHOLD:
            if self.current_batch * BATCH_SIZE < len(self.filtered_data):
                self.load_data(append=True)

    def sort_by_price_dropdown(self, selection):
        """Sort data by price based on dropdown selection."""
        reverse = True if selection == "Highest to Lowest" else False
        try:
            self.filtered_data.sort(key=lambda x: int(x["price"]), reverse=reverse)
            self.current_batch = 0  # Reset batch for new sort order
            self.load_data()
        except Exception as e:
            print(f"Sorting error: {e}")

    def search(self):
        search_term = self.search_var.get().lower()
        self.filtered_data = [entry for entry in self.car_data if search_term in entry.get("title", "").lower()]
        self.apply_filters()

    def cleanup(self):
        print("Stopping crawling process...")
        self.stop_flag.set()
        self.quit()
        self.destroy()

# Signal handler for graceful shutdown on Ctrl-C
def signal_handler(signal, frame):
    print("\nCtrl-C detected. Exiting gracefully...")
    app.cleanup()
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

# Run the app
if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.cleanup)
    app.mainloop()
