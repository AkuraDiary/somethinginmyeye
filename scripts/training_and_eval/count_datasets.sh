#!/bin/bash
# =============================================================================
# Dataset Multi-Folder Census & Recount Utility
# Audits CSV/PNG pair integrity, class balance (DSM-5 Typical vs Atypical),
# and split distribution across one or more dataset directories.
# =============================================================================

set -e

# -----------------------------------------------------------------------------
# CONFIGURATION: Dataset Directories Array
# Add, remove, or reorder target directories as needed.
# Paths can be relative to the repository root or absolute paths.
# -----------------------------------------------------------------------------
DATASET_DIRS=(
    "datasets"
    "huawei_datasets"
    # "dhrc_train_datasets"
    # "dhrc_val_datasets"
    # "elkinematics_train_datasets"
    # "elkinematics_val_datasets"
)

# Determine project root and script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Allow command-line arguments to override the default array if supplied
if [ "$#" -gt 0 ]; then
    TARGET_DIRS=("$@")
else
    TARGET_DIRS=("${DATASET_DIRS[@]}")
fi

# Temporary storage for detailed aggregation
AGG_FILE=$(mktemp)
FOLDER_STATS_FILE=$(mktemp)
trap 'rm -f "$AGG_FILE" "$FOLDER_STATS_FILE"' EXIT

# Grand total accumulator variables
GRAND_CSV=0
GRAND_PNG=0
GRAND_MISSING_PAIRS=0
GRAND_TYPICAL=0
GRAND_DYSLEXIA=0
GRAND_DYSGRAPHIA=0
GRAND_ATYPICAL=0
GRAND_TRAIN=0
GRAND_VALIDATION=0

resolve_dir() {
    local target="$1"
    if [ -d "$target" ]; then
        echo "$target"
    elif [ -d "$PROJECT_ROOT/$target" ]; then
        echo "$PROJECT_ROOT/$target"
    elif [ -d "$SCRIPT_DIR/$target" ]; then
        echo "$SCRIPT_DIR/$target"
    else
        echo ""
    fi
}

echo "================================================================================"
echo "                   ELKINEMATICS MULTI-DATASET RECAP REPORT                      "
echo "================================================================================"
echo "Active Directories Configured: ${#TARGET_DIRS[@]}"
for d in "${TARGET_DIRS[@]}"; do
    echo "  - $d"
done
echo "================================================================================"
echo ""

for raw_dir in "${TARGET_DIRS[@]}"; do
    DIR=$(resolve_dir "$raw_dir")

    if [ -z "$DIR" ] || [ ! -d "$DIR" ]; then
        echo "[WARNING] Directory not found: '$raw_dir' (Skipping)"
        echo ""
        continue
    fi

    dir_display_name=$(basename "$DIR")
    csv_count=$(find "$DIR" -maxdepth 1 -name "*.csv" | wc -l | tr -d ' ')
    png_count=$(find "$DIR" -maxdepth 1 -name "*.png" | wc -l | tr -d ' ')

    dir_typical=0
    dir_dyslexia=0
    dir_dysgraphia=0
    dir_missing_pairs=0
    dir_train=0
    dir_val=0

    for csv_file in "$DIR"/*.csv; do
        [ -e "$csv_file" ] || continue

        basename=$(basename "$csv_file" .csv)
        png_file="$DIR/$basename.png"

        if [ ! -f "$png_file" ]; then
            ((dir_missing_pairs++))
        fi

        # Robust filename decomposition:
        # ${dataset}_${mode}_${label}_${annotator}_${client_ts}_${server_ts}
        IFS='_' read -ra P <<< "$basename"
        n=${#P[@]}

        if [ "$n" -lt 4 ]; then
            continue
        fi

        dataset="${P[0]}"
        mode="${P[1]}"
        annotator=""
        label=""

        if [[ "${P[n-1]}" =~ ^[0-9]+$ ]] && [[ "${P[n-2]}" =~ ^[0-9]+$ ]]; then
            annotator="${P[n-3]}"
            lbl_len=$((n - 5))
            label=$(IFS="_"; echo "${P[*]:2:lbl_len}")
        elif [[ "${P[n-1]}" =~ ^[0-9]+$ ]]; then
            annotator="${P[n-2]}"
            lbl_len=$((n - 4))
            label=$(IFS="_"; echo "${P[*]:2:lbl_len}")
        else
            annotator="${P[n-1]}"
            lbl_len=$((n - 3))
            label=$(IFS="_"; echo "${P[*]:2:lbl_len}")
        fi

        # Mode classification
        mode_lower=$(echo "$mode" | tr '[:upper:]' '[:lower:]')
        if echo "$mode_lower" | grep -q "normal"; then
            ((dir_typical++))
        elif echo "$mode_lower" | grep -q "dyslexia"; then
            ((dir_dyslexia++))
        elif echo "$mode_lower" | grep -q "dysgraphia"; then
            ((dir_dysgraphia++))
        fi

        # Split classification
        dataset_lower=$(echo "$dataset" | tr '[:upper:]' '[:lower:]')
        if echo "$dataset_lower" | grep -q "train"; then
            ((dir_train++))
        elif echo "$dataset_lower" | grep -q -e "val" -e "test"; then
            ((dir_val++))
        fi

        # Save record for detailed recap
        echo "$dir_display_name|$dataset|$mode|$label|$annotator" >> "$AGG_FILE"
    done

    dir_atypical=$((dir_dyslexia + dir_dysgraphia))

    # Accumulate into grand totals
    GRAND_CSV=$((GRAND_CSV + csv_count))
    GRAND_PNG=$((GRAND_PNG + png_count))
    GRAND_MISSING_PAIRS=$((GRAND_MISSING_PAIRS + dir_missing_pairs))
    GRAND_TYPICAL=$((GRAND_TYPICAL + dir_typical))
    GRAND_DYSLEXIA=$((GRAND_DYSLEXIA + dir_dyslexia))
    GRAND_DYSGRAPHIA=$((GRAND_DYSGRAPHIA + dir_dysgraphia))
    GRAND_ATYPICAL=$((GRAND_ATYPICAL + dir_atypical))
    GRAND_TRAIN=$((GRAND_TRAIN + dir_train))
    GRAND_VALIDATION=$((GRAND_VALIDATION + dir_val))

    # Record folder summary row
    echo "$dir_display_name|$csv_count|$png_count|$dir_missing_pairs|$dir_train|$dir_val|$dir_typical|$dir_atypical" >> "$FOLDER_STATS_FILE"
done

# -----------------------------------------------------------------------------
# SUMMARY TABLE ACROSS FOLDERS
# -----------------------------------------------------------------------------
echo "DIRECTORY COHORT BREAKDOWN:"
echo "--------------------------------------------------------------------------------"
printf "%-18s | %-6s | %-6s | %-8s | %-6s | %-6s | %-8s | %-8s\n" \
    "Folder" "CSV" "PNG" "Missing" "Train" "Val" "Typical" "Atypical"
echo "--------------------------------------------------------------------------------"

if [ -s "$FOLDER_STATS_FILE" ]; then
    while IFS='|' read -r fname fcsv fpng fmissing ftrain fval ftyp fatyp; do
        printf "%-18s | %-6d | %-6d | %-8d | %-6d | %-6d | %-8d | %-8d\n" \
            "$fname" "$fcsv" "$fpng" "$fmissing" "$ftrain" "$fval" "$ftyp" "$fatyp"
    done < "$FOLDER_STATS_FILE"
fi

echo "--------------------------------------------------------------------------------"
printf "%-18s | %-6d | %-6d | %-8d | %-6d | %-6d | %-8d | %-8d\n" \
    "GRAND TOTAL" "$GRAND_CSV" "$GRAND_PNG" "$GRAND_MISSING_PAIRS" "$GRAND_TRAIN" "$GRAND_VALIDATION" "$GRAND_TYPICAL" "$GRAND_ATYPICAL"
echo "================================================================================"
echo ""

# -----------------------------------------------------------------------------
# GRAND TOTAL CLINICAL & STATISTICAL METRICS
# -----------------------------------------------------------------------------
echo "COMBINED DATASET RECAP (Paper & Modeling Summary):"
echo "--------------------------------------------------------------------------------"
echo "  Total Recorded CSV Sequences:  $GRAND_CSV"
echo "  Total Rendered PNG Images:     $GRAND_PNG"
if [ "$GRAND_MISSING_PAIRS" -eq 0 ]; then
    echo "  Pair Integrity Status:         100% Complete (0 missing pairs)"
else
    echo "  Pair Integrity Status:         WARNING: $GRAND_MISSING_PAIRS unmatched files"
fi
echo ""
echo "  Split Distribution:"
echo "    -> Train Split:              $GRAND_TRAIN"
echo "    -> Validation Split:         $GRAND_VALIDATION"
echo ""
echo "  Binary Diagnosis Breakdown (DSM-5 Diagnostic Standard):"
echo "    -> Class 0: Typical (Normal):                  $GRAND_TYPICAL"
echo "    -> Class 1: Atypical (Neurodevelopmental SLD): $GRAND_ATYPICAL"
echo "       * Dyslexia Manifestations:    $GRAND_DYSLEXIA"
echo "       * Dysgraphia Manifestations:  $GRAND_DYSGRAPHIA"
echo "--------------------------------------------------------------------------------"
echo ""

# -----------------------------------------------------------------------------
# DETAILED PER-LABEL & ANNOTATOR SUMMARY
# -----------------------------------------------------------------------------
echo "DETAILED SUMMARY BY FOLDER, DATASET, MODE, LABEL & ANNOTATOR:"
echo "--------------------------------------------------------------------------------"
printf "%-16s | %-12s | %-11s | %-20s | %-10s | %s\n" \
    "Folder" "Dataset" "Mode" "Label" "Annotator" "Count"
echo "--------------------------------------------------------------------------------"

if [ -s "$AGG_FILE" ]; then
    awk -F'|' '{
        count[$1 "|" $2 "|" $3 "|" $4 "|" $5]++
    } END {
        for (key in count) {
            split(key, arr, "|")
            printf "%-16s | %-12s | %-11s | %-20s | %-10s | %d\n", \
                arr[1], arr[2], arr[3], arr[4], arr[5], count[key]
        }
    }' "$AGG_FILE" | sort
fi
echo "================================================================================"
