#!/bin/bash

DIR=${1:-../datasets}
if [ ! -d "$DIR" ] && [ -d "datasets" ]; then
    DIR="datasets"
fi

csv_count=0
png_count=0
missing_pairs=0

typical_count=0
atypical_count=0

echo "Analyzing files in $DIR..."

csv_count=$(find "$DIR" -maxdepth 1 -name "*.csv" | wc -l | tr -d ' ')
png_count=$(find "$DIR" -maxdepth 1 -name "*.png" | wc -l | tr -d ' ')

echo "Total CSV files: $csv_count"
echo "Total PNG files: $png_count"
echo "------------------------------------------------"

tmp_file=$(mktemp)

for csv_file in "$DIR"/*.csv; do
    [ -e "$csv_file" ] || continue
    
    basename=$(basename "$csv_file" .csv)
    png_file="$DIR/$basename.png"
    
    if [ ! -f "$png_file" ]; then
        ((missing_pairs++))
    fi
    
    IFS='_' read -r dataset mode label annotator timestamp <<< "$basename"
    
    # The 'normal' or 'dyslexia' tag is actually in the $mode variable!
    if echo "$mode" | grep -qi "normal"; then
        ((typical_count++))
    elif echo "$mode" | grep -qi -e "dyslexia" -e "dysgraphia"; then
        ((atypical_count++))
    fi
    
    echo "$dataset|$mode|$label|$annotator" >> "$tmp_file"
done

echo "------------------------------------------------"
if [ "$missing_pairs" -eq 0 ]; then
    echo "All CSV files have a matching PNG pair."
else
    echo "Missing PNG pairs: $missing_pairs"
fi
echo ""

echo "Paper Summary Breakdown (Class 0 vs Class 1):"
echo "--------------------------------------------------------------------------------"
echo "   -> Typical (Normal): $typical_count"
echo "   -> Atypical (Dysgraphia/Dyslexia): $atypical_count"
echo "--------------------------------------------------------------------------------"
echo ""

echo "Detailed Summary by Dataset, Mode, Label & Annotator:"
echo "--------------------------------------------------------------------------------"
printf "%-15s | %-10s | %-15s | %-15s | %s\n" "Dataset" "Mode" "Label" "Annotator" "Count"
echo "--------------------------------------------------------------------------------"

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
