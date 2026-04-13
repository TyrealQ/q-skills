# Multi-Key Management — Detailed Reference

Each `GOOGLE_API_KEY{N}` maps to a separate Google Cloud project with an independent 20 GB File API storage quota (18 GB usable for media; 2 GB reserved for JSONL uploads). Four keys = 72 GB effective media capacity.

## Key Assignment

Key assignment happens at upload time (`--key N`). All downstream scripts auto-detect `key_id` from URI maps and CSV, ensuring the correct API client is used per job.

## Distribution Strategy for Large Datasets

```bash
python 0uploadMedia.py --players-file splits/key1.txt --key 1
python 0uploadMedia.py --players-file splits/key2.txt --key 2
python 0uploadMedia.py --players-file splits/key3.txt --key 3
python 0uploadMedia.py --players-file splits/key4.txt --key 4
```

Or let `0uploadMedia.py` auto-stop at quota and re-run with the next key.

## Retry Threshold Decision

Run `--preview` to count total failed rows across all subjects.

| Total failed rows | Strategy | Reason |
|-------------------|----------|--------|
| > 500 | Batch retry (`--submit`) | 50% cost discount |
| <= 500 | Standard (`--standard`) | Speed, simpler |
| After 3 batch attempts | Standard fallback | Batch retry exhausted |

The threshold is the combined sum across all subjects, not per-subject (e.g., 5 subjects with 50, 100, 200, 300, 250 failures = 900 total -> use batch).
