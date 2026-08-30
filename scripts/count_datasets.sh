#!/bin/bash

# Directory can be passed as argument, defaulting to '../datasets' if run from inside scripts/
DIR=${1:-../datasets}

# Fallback to local 'datasets' if run from project root
if [ ! -d "$DIR" ] && [ -d "datasets" ]; then
    DIR="datasets"
fi

if [ ! -d "$DIR" ]; then
    echo "Error: Directory '$DIR' not found."
    exit 1
fi

csv_count=0
png_count=0
missing_pairs=0

echo "🔍 Analyzing files in $DIR..."

# Count absolute totals
csv_count=$(find "$DIR" -maxdepth 1 -name "*.csv" | wc -l | tr -d ' ')
png_count=$(find "$DIR" -maxdepth 1 -name "*.png" | wc -l | tr -d ' ')

echo "Total CSV files: $csv_count"
echo "Total PNG files: $png_count"
echo "------------------------------------------------"

# Write found pairs to a temporary file for AWK to process
tmp_file=$(mktemp)

for csv_file in "$DIR"/*.csv; do
    [ -e "$csv_file" ] || continue
    
    basename=$(basename "$csv_file" .csv)
    png_file="$DIR/$basename.png"
    
    if [ ! -f "$png_file" ]; then
        echo "⚠️ Missing PNG pair for: $basename"
        ((missing_pairs++))
    fi
    
    # Parse the new format: dataset_mode_label_annotator_timestamp
    IFS='_' read -r dataset mode label annotator timestamp <<< "$basename"
    
    echo "$dataset|$mode|$label|$annotator" >> "$tmp_file"
done

echo "------------------------------------------------"
if [ "$missing_pairs" -eq 0 ]; then
    if [ "$csv_count" -eq 0 ]; then
        echo "No data files found yet."
    else
        echo " All CSV files have a matching PNG pair."
    fi
else
    echo " Missing PNG pairs: $missing_pairs"
fi
echo ""
echo "📋 Summary by Dataset, Mode, Label & Annotator:"
echo "--------------------------------------------------------------------------------"
printf "%-15s | %-10s | %-15s | %-15s | %s\n" "Dataset" "Mode" "Label" "Annotator" "Count"
echo "--------------------------------------------------------------------------------"

# Group and count using AWK
if [ -s "$tmp_file" ]; then
    awk -F'|' '{
        count[$1 "|" $2 "|" $3 "|" $4]++
    } END {
        for (key in count) {
            split(key, arr, "|")
            printf "%-15s | %-10s | %-15s | %-15s | %d\n", arr[1], arr[2], arr[3], arr[4], count[key]
        }
    }' "$tmp_file" | sort
fi

rm -f "$tmp_file"