import json
import os

def combine_json_files(source_directory, file_names, output_file_name):
    """
    Reads multiple JSON files from a source directory, combines their
    contents (assuming each is a list of objects), and writes the
    result to a new JSON file in the same directory.
    """
    combined_data = []
    
    # Ensure the source directory exists before trying to read from or write to it
    if not os.path.isdir(source_directory):
        print(f"Error: Source directory not found at '{source_directory}'")
        return

    for file_name in file_names:
        file_path = os.path.join(source_directory, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    combined_data.extend(data)
                else:
                    print(f"Warning: {file_name} does not contain a JSON list. Skipping.")
        except FileNotFoundError:
            print(f"Warning: {file_name} not found. Skipping.")
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON from {file_name}. Skipping.")

    output_path = os.path.join(source_directory, output_file_name)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2)
        print(f"Successfully combined {len(file_names)} files into {output_path}")
        print(f"Total records: {len(combined_data)}")
    except IOError as e:
        print(f"Error writing to {output_path}: {e}")


if __name__ == "__main__":
    # Get the absolute path to the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # The source directory is named "Source" and is in the same directory as the script
    source_dir_path = os.path.join(script_dir, "Source")
    
    # List of JSON files to combine
    files_to_combine = [
        "the_sales_process_chunks.json",
        "selling_basics_chunks.json",
        "understanding_the_buyer_chunks.json"
    ]
    
    # Name of the final combined file
    output_file = "trainer_source_data.json"
    
    combine_json_files(source_dir_path, files_to_combine, output_file)