#!/usr/bin/env python3

import re
import sys
import pandas as pd
import numpy as np

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <logfile>", file=sys.stderr)
    sys.exit(1)

pattern = re.compile(
    r"wasmtime compiled contract "
    r"original_size=(\d+) prepared_size=(\d+) compiled_size=(\d+)"
)

rows = []
with open(sys.argv[1]) as f:
    for line in f:
        m = pattern.search(line)
        if m:
            rows.append(tuple(int(x) for x in m.groups()))

if not rows:
    print("No matching lines found.", file=sys.stderr)
    sys.exit(1)

df = pd.DataFrame(rows, columns=["original_size", "prepared_size", "compiled_size"])
df["prepared/original"] = df["prepared_size"] / df["original_size"]
df["compiled/original"] = df["compiled_size"] / df["original_size"]
df["compiled/prepared"] = df["compiled_size"] / df["prepared_size"]

print("=== Raw data ===")
print(df[["original_size", "prepared_size", "compiled_size"]].to_string(index=False))
print()

print("=== Statistics ===")
count_over_32 = (df["compiled/original"] > 32).sum()
count_over_64 = (df["compiled/original"] > 64).sum()
count_over_128 = (df["compiled/original"] > 128).sum()
count_over_256 = (df["compiled/original"] > 256).sum()
count_over_512 = (df["compiled/original"] > 512).sum()
print(f"""total of {len(df)} contracts, 
    {count_over_32} with compiled/original > 32, 
    {count_over_64} with compiled/original > 64, 
    {count_over_128} with compiled/original > 128,
    {count_over_256} with compiled/original > 256,
    {count_over_512} with compiled/original > 512,
    """)
stats = df.agg(
    ["mean",
     lambda x: np.percentile(x, 95),
     lambda x: np.percentile(x, 99),
     "max"])
stats.index = ["avg", "p95", "p99", "max"]
print(stats.to_string())
