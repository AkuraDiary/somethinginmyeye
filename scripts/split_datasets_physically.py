import os
import glob
import shutil
import random

def split_physically():
    source_dir = "../datasets"
    val_dir = "../val_datasets"
    
    os.makedirs(val_dir, exist_ok=True)
    
    # Get all files
    all_files = glob.glob(os.path.join(source_dir, "*.csv"))
    
    typical_files = []
    atypical_files = []
    
    for f in all_files:
        if "normal" in f.lower():
            typical_files.append(f)
        else:
            atypical_files.append(f)
            
    # Calculate 20%
    num_typical_val = int(len(typical_files) * 0.2)
    num_atypical_val = int(len(atypical_files) * 0.2)
    
    print(f"Total Typical: {len(typical_files)} | Total Atypical: {len(atypical_files)}")
    print(f"Moving {num_typical_val} Typical and {num_atypical_val} Atypical to {val_dir}/...")
    
    # Shuffle and pick
    random.seed(42)
    random.shuffle(typical_files)
    random.shuffle(atypical_files)
    
    val_files = typical_files[:num_typical_val] + atypical_files[:num_atypical_val]
    
    for f in val_files:
        filename = os.path.basename(f)
        dest = os.path.join(val_dir, filename)
        shutil.move(f, dest)
        
    print(f"✅ Successfully moved {len(val_files)} files to {val_dir}/")
    print(f"✅ {len(all_files) - len(val_files)} files remaining in {source_dir}/")

if __name__ == "__main__":
    split_physically()
