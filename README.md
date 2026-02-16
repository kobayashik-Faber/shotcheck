# shotcheck

A tool that compares images from two directories and generates side-by-side difference visualizations. It matches images by their filename prefix (ignoring timestamp suffixes) and highlights the differences.

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
uv sync
```

## Usage

```bash
uv run python shotcheck.py <dir1> <dir2> <output_dir>
```

### Example

```bash
uv run python shotcheck.py screenshots/before screenshots/after output
```

### Arguments

| Argument     | Description                                      |
| ------------ | ------------------------------------------------ |
| `<dir1>`     | Path to the first directory containing PNG images |
| `<dir2>`     | Path to the second directory containing PNG images |
| `<output_dir>` | Path to the output directory for results        |

## Output

For each matching image pair, the tool generates:

- **Difference image** (`<prefix>_diff.png`): A side-by-side view of Image 1, Image 2, and the difference overlay. Identical areas are shown in grayscale, and differences are highlighted in red.
- **Difference report** (`difference_report.txt`): A summary listing which images have differences and which are identical.
