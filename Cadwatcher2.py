import os
import subprocess
import json
import sys
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import logging
import threading  # Make sure threading is imported

config_file = "path_config.json"
error_log_file = "errors.log"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler("app.log"),
    logging.StreamHandler(sys.stdout)
])

# Configure error logging
error_logger = logging.getLogger('error_logger')
error_logger.setLevel(logging.ERROR)
error_handler = logging.FileHandler(error_log_file)
error_handler.setLevel(logging.ERROR)
error_logger.addHandler(error_handler)

def get_full_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def load_config():
    full_path = get_full_path(config_file)
    if os.path.exists(full_path):
        with open(full_path, 'r') as f:
            return json.load(f)
    else:
        return {
            "blender_path": "",
            "temp_blender_script": "",
            "export_folder": ""
        }

config = load_config()

def save_config(config):
    full_path = get_full_path(config_file)
    with open(full_path, 'w') as f:
        json.dump(config, f, indent=4)

def log_error(error_message):
    error_logger.error(error_message)
    logging.error(error_message)




def generate_blender_script(filepaths):
    blender_script_content = """
import bpy
import os

# Clear the default objects in the current scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Import and process each file
"""
    for filepath in filepaths:
        filename = os.path.basename(filepath)
        base_filename = os.path.splitext(filename)[0]
        export_filepath = os.path.join(get_full_path(config['export_folder']), f"{base_filename}.glb")
        blender_script_content += f"""
# Import the STEP file: {filename}
bpy.ops.import_scene.occ_import_step(filepath="{filepath}", override_file="{filename}", hierarchy_types="EMPTIES")
# Set mesh detail to 100
bpy.context.preferences.addons['STEPper'].preferences.mesh_detail = 100
# Export as GLB with Y-Up orientation
bpy.ops.export_scene.gltf(filepath="{export_filepath}", export_format='GLB', export_colors=False, export_yup=True)
print("GLB file exported successfully:", "{export_filepath}")
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
        """

    with open(get_full_path(config['temp_blender_script']), 'w') as file:
        file.write(blender_script_content)






def execute_blender_script(filepaths):
    try:
        if not os.path.exists(config['blender_path']):
            raise FileNotFoundError(f"Blender executable '{config['blender_path']}' not found.")

        generate_blender_script(filepaths)

        process = subprocess.Popen(
            [config['blender_path'], "--background", "--python", get_full_path(config['temp_blender_script'])],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout_lines = []
        stderr_lines = []

        for stdout_line in iter(process.stdout.readline, ''):
            logging.info(stdout_line.strip())
            stdout_lines.append(stdout_line)
        for stderr_line in iter(process.stderr.readline, ''):
            logging.error(stderr_line.strip())
            stderr_lines.append(stderr_line)
            log_error(stderr_line.strip())

        process.stdout.close()
        process.stderr.close()
        process.wait()

        if process.returncode != 0:
            error_message = f"Blender process failed with return code {process.returncode}\n"
            error_message += ''.join(stderr_lines)
            raise RuntimeError(error_message)

        logging.info(f"Conversion executed in Blender and exported to {get_full_path(config['export_folder'])}.")

    except Exception as e:
        error_message = f"Error processing files: {str(e)}"
        log_error(error_message)

class ConfigGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RHP Blender Converter Settings and Logs")
        self.geometry("600x500")

        self.log_messages = []

        self.create_entry_field("Blender Path:", "blender_path", config)
        self.create_entry_field("Temp Blender Script:", "temp_blender_script", config)
        self.create_entry_field("Export Folder:", "export_folder", config)

        tk.Button(self, text="Save", command=self.save_settings).grid(row=7, column=1, pady=10)

        tk.Button(self, text="Select STEP Files", command=self.select_files).grid(row=8, column=1, pady=10)

        tk.Label(self, text="Console Log:").grid(row=9, column=0, pady=(20, 0))
        self.log_display = scrolledtext.ScrolledText(self, width=70, height=10)
        self.log_display.grid(row=10, column=0, columnspan=3, pady=(0, 20))
        self.log_display.config(state=tk.NORMAL)

        sys.stdout = StreamRedirector(self.log_display, self.log_messages)
        sys.stderr = StreamRedirector(self.log_display, self.log_messages)

        logger = logging.getLogger()
        logger.addHandler(logging.StreamHandler(sys.stdout))

    def create_entry_field(self, label, config_key, config):
        row = len(self.grid_slaves()) // 2

        tk.Label(self, text=label).grid(row=row, column=0, sticky="e")
        entry = tk.Entry(self, width=50)
        entry.grid(row=row, column=1)
        entry.insert(0, get_full_path(config[config_key]))

        def browse():
            if "directory" in label.lower() or "folder" in label.lower():
                selected = filedialog.askdirectory(initialdir=get_full_path(config[config_key]))
            else:
                selected = filedialog.askopenfilename(initialdir=os.path.dirname(get_full_path(config[config_key])))
            if selected:
                entry.delete(0, tk.END)
                entry.insert(0, selected)

        tk.Button(self, text="Browse", command=browse).grid(row=row, column=2)
        self.__dict__[f"{config_key}_entry"] = entry

    def save_settings(self):
        config['blender_path'] = self.blender_path_entry.get()
        config['temp_blender_script'] = self.temp_blender_script_entry.get()
        config['export_folder'] = self.export_folder_entry.get()

        os.makedirs(get_full_path(config['export_folder']), exist_ok=True)
        save_config(config)
        logging.info("Settings saved successfully.")

    def select_files(self):
        filepaths = filedialog.askopenfilenames(filetypes=[("STEP files", "*.stp"), ("All files", "*.*")])
        if filepaths:
            self.process_files(filepaths)

    def process_files(self, filepaths):
        threading.Thread(target=execute_blender_script, args=(filepaths,)).start()

class StreamRedirector:
    def __init__(self, text_widget, log_messages):
        self.text_widget = text_widget
        self.log_messages = log_messages

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)
        self.log_messages.append(message)

    def flush(self):
        pass

# Initialize GUI
app = ConfigGUI()
app.mainloop()
