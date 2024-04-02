#!/usr/bin/env python3
"""
This script converts a Notion export to a Joplin import (MD - Markdown directory).
"""

import argparse
import zipfile
import glob
import shutil
import os
import ntpath
import urllib.parse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to extract the provided zip file
def extract_zip(input_zip, extract_to):
    with zipfile.ZipFile(input_zip, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

# Function to rename markdown files based on their heading
def rename_md_files_and_fix_links(folder_extraction, markdown_extension):
    path_to_files = os.path.join(folder_extraction, '**/*.' + markdown_extension)
    for filename in glob.iglob(path_to_files, recursive=True):
        with open(filename, 'r', encoding='utf-8') as file:
            first_line = file.readline()
            heading = first_line.replace('# ', '').strip().replace('/', '-')
            lines_without_heading = file.readlines()

        new_filename = os.path.join(os.path.dirname(filename), heading + '.' + markdown_extension)
        with open(new_filename, 'w', encoding='utf-8') as file:
            file.writelines(lines_without_heading)

        os.remove(filename)
        update_links(folder_extraction, ntpath.basename(filename), heading + '.' + markdown_extension)

# Function to update all links in markdown files after a file or folder rename
def update_links(folder_extraction, old_name, new_name):
    path_to_files = os.path.join(folder_extraction, '**/*.md')
    old_name_encoded = urllib.parse.quote(old_name)
    new_name_encoded = urllib.parse.quote(new_name)

    for filename_to_fix in glob.iglob(path_to_files, recursive=True):
        with open(filename_to_fix, 'r', encoding='utf-8') as file:
            content = file.read()

        content = content.replace(old_name_encoded, new_name_encoded)

        with open(filename_to_fix, 'w', encoding='utf-8') as file:
            file.write(content)

# Function to rename folders by removing hash from the end of the folder name
def rename_folders(folder_extraction):
    path_of_folders = os.path.join(folder_extraction, '**/*')
    for folder in glob.iglob(path_of_folders, recursive=True):
        if os.path.isdir(folder):
            folder_name = os.path.basename(folder)
            new_folder_name = " ".join(folder_name.split(" ")[:-1])
            new_folder_path = os.path.join(os.path.dirname(folder), new_folder_name)
            shutil.move(folder, new_folder_path)
            update_links(folder_extraction, folder_name, new_folder_name)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Convert Notion export to Joplin import.')
    parser.add_argument('-f', '--file', help='File to be processed', required=True)
    args = parser.parse_args()

    folder_extraction = "import_to_joplin"
    markdown_extension = "md"

    # Step 1: Delete the folder if it exists
    if os.path.exists(folder_extraction):
        shutil.rmtree(folder_extraction)
        logging.info(f"Existing extraction folder '{folder_extraction}' removed.")

    # Step 2: Unzip the file
    logging.info("Unzipping backup file...")
    extract_zip(args.file, folder_extraction)
    logging.info("Unzipping done.")

    # Step 3: Rename every file with a .md extension with the heading of the file and fix all the links
    logging.info("Renaming files and fixing links...")
    rename_md_files_and_fix_links(folder_extraction, markdown_extension)
    logging.info("Renaming files and fixing links done.")

    # Step 4: Rename all folders and fix all the links
    logging.info("Renaming folders...")
    rename_folders(folder_extraction)
    logging.info("Renaming folders done.")

    logging.info(f"All done. You can now import the folder '{folder_extraction}' into Joplin (File > Import > MD - Markdown directory).")

if __name__ == "__main__":
    main()
