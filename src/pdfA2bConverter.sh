#!/bin/bash

# Function to display usage information
usage() {
    echo "Usage: $0 -i <input_directory> -o <output_directory>"
    exit 1
}

# Parse command-line arguments
while getopts ":i:o:" opt; do
  case $opt in
    i)
      input_dir="$OPTARG"
      ;;
    o)
      output_dir="$OPTARG"
      ;;
    *)
      usage
      ;;
  esac
done

# Check if input and output directories are set
if [ -z "$input_dir" ] || [ -z "$output_dir" ]; then
    usage
fi

# Ensure the input directory ends with a slash
input_dir="${input_dir%/}/"

# Create output directory if it doesn't exist
mkdir -p "$output_dir"

# Loop over all PDF files in the input directory
for input_file in "$input_dir"*.pdf; do
    # Get the base name of the file (without directory and extension)
    base_name=$(basename "$input_file" .pdf)
    
    # Set the output file path
    output_file="$output_dir${base_name}_2ab.pdf"
    
    # Run the Ghostscript command
    gs -sDEVICE=pdfwrite \
       -dPDFA=2 \
       -dPDFACompatibilityPolicy=1 \
       -sColorConversionStrategy=UseDeviceIndependentColor \
       -o "$output_file" \
       -f "$input_file"
    
    echo "Converted $input_file to $output_file"
done

echo "All PDF files have been converted."
