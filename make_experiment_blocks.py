from pathlib import Path
import csv
import random


BASE_DIR = Path(__file__).parent
STIM_DIR = BASE_DIR / "stim"
OUTPUT_CSV = BASE_DIR / "test_split.csv"

N_BLOCKS = 8
BLOCK_SIZE = 84
OLD_PER_BLOCK = 56
NEW_PER_BLOCK = 28
RANDOM_SEED = None


def load_image_names(stim_dir):
    return sorted(path.name for path in stim_dir.glob("*.jpg") if path.is_file())


def make_image_block_rows(image_names, random_seed=RANDOM_SEED):
    expected_count = N_BLOCKS * BLOCK_SIZE

    if len(image_names) != expected_count:
        raise ValueError("size not match")

    rng = random.Random(random_seed)
    shuffled_names = image_names.copy()
    rng.shuffle(shuffled_names)

    rows = []

    for block_idx in range(N_BLOCKS):
        start = block_idx * BLOCK_SIZE
        end = start + BLOCK_SIZE
        block_names = shuffled_names[start:end]

        labels = ["old"] * OLD_PER_BLOCK + ["new"] * NEW_PER_BLOCK
        rng.shuffle(labels)

        for file_name, label in zip(block_names, labels):
            rows.append(
                {
                    "file_name": file_name,
                    "block": block_idx + 1,
                    "label": label,
                }
            )

    return rows


def save_rows_to_csv(rows, output_csv):
    with output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["file_name", "block", "label"])
        writer.writeheader()
        writer.writerows(rows)


def main():
    image_names = load_image_names(STIM_DIR)
    rows = make_image_block_rows(image_names)
    save_rows_to_csv(rows, OUTPUT_CSV)

    for block in range(1, N_BLOCKS + 1):
        block_rows = [row for row in rows if row["block"] == block]
        n_old = sum(row["label"] == "old" for row in block_rows)
        n_new = sum(row["label"] == "new" for row in block_rows)
        print(f"block {block}: total={len(block_rows)}, old={n_old}, new={n_new}")


if __name__ == "__main__":
    main()
