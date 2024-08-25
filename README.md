# Blender 3D File Converter

This Python project features a Tkinter UI where users can select a folder to monitor for any newly created `.stp` files. When a `.stp` file is detected, it is automatically sent to Blender for conversion into a `.glb` file with predefined settings applied through code. This process requires the STEP plugin for Blender.

## Features

- **Folder Monitoring:** Automatically watches a selected folder for any new `.stp` files.
- **Automated Conversion:** Converts `.stp` files to `.glb` files using Blender with predefined settings.
- **STEP Plugin Requirement:** Requires the STEP plugin for Blender to function properly.
- **Error Logging:** Logs any errors encountered during the conversion process.
- **File Management:** Automatically deletes the original `.stp` file after successful conversion.

## Usage

1. **Set Up the Environment:**
   - Ensure Blender is installed and the STEP plugin is configured.

2. **Run the Application:**
   - Launch the Python script to open the Tkinter UI.

3. **Select a Folder:**
   - Use the UI to select the folder you want to monitor for `.stp` files.

4. **Conversion Process:**
   - The application will automatically detect new `.stp` files, convert them to `.glb` using Blender, and delete the original `.stp` files.

5. **Check Logs:**
   - Review the log file for any errors encountered during the conversion.

## Dependencies

- **Python 3.x**
- **Tkinter** (for the UI)
- **Blender** (with STEP plugin installed)
- **Logging** (for error management)
