import os
import argparse
import shutil


def fetch_filenames(directory):
    """
    Fetch all filenames in the given directory.

    :param directory: Directory path as a string
    :return: List of filenames
    """
    if os.path.exists(directory):
        print(f"Fetching files from",directory)
    else:
        print(f"File {directory} does not exist and cannot be fetched. Recheck the 2ab folder path")

    # Use a set to store filenames to ensure uniqueness
    # list of failed files to be reconverted
    failed_list = set()
    # 2ab files that are failed
    failed_list_2ab = set()
    all_files = []

    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        all_files = files
        for file in files:
            if ".txt" in file:
                truncated_name = file.split('_')[0]
                failed_list.add(truncated_name + ".pdf")
                failed_list_2ab.add(truncated_name + "_2ab.pdf")
                failed_list_2ab.add(truncated_name + "_2ab_report.txt")

    return list(failed_list), list(failed_list_2ab)


def move_files(filenames, source_directory, destination_directory):
    """
    Move files from source_directory to destination_directory based on the filenames list.
    If the destination_directory doesn't exist, it will be created.

    :param filenames: List of filenames to move
    :param source_directory: Source directory path as a string
    :param destination_directory: Destination directory path as a string
    """
    # Create destination directory if it doesn't exist
    os.makedirs(destination_directory, exist_ok=True)

    for filename in filenames:
        source_path = os.path.join(source_directory, filename)
        destination_path = os.path.join(destination_directory, filename)

        # Check if the file exists in the source directory before moving
        if os.path.exists(source_path):
            shutil.move(source_path, destination_path)
            print(f"Moved {source_path} to {destination_path}")
        else:
            print(f"File {source_path} does not exist and cannot be moved.")


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Fetch all filenames in a given directory, truncate them at the first underscore, append .pdf to each truncated name, and move them from source to destination directory.')
    parser.add_argument('a2b_directory', type=str, help='The path to the 2ab and failure text directory')
    parser.add_argument('source_directory', type=str, help='The path to the source pdf directory')
    # parser.add_argument('destination_directory', type=str, help='The path to the destination directory for separating the failed pdfs')

    # Parse the arguments
    args = parser.parse_args()
    a2b_directory = args.a2b_directory
    source_directory = args.source_directory
    # destination_directory = args.destination_directory

    print(f"a2b_directory: {a2b_directory}\nsource_directory: {source_directory}\ndestination_directory: ")

    # Fetch the list of modified filenames and failed 2ab and error files
    file_list, failed_list = fetch_filenames(a2b_directory)
    print(f"File list: ", file_list)

    # Move the files
    move_files(file_list, source_directory, a2b_directory.rstrip("/")+"/reconvert/")
    move_files(failed_list, a2b_directory, a2b_directory.rstrip("/")+"/failed/")

'''
python seperateFailedPDFs.py /path/to/2ab_directory /path/to/source_directory
'''
if __name__ == "__main__":
    print("Starting separation program")
    main()
