import pandas as pd
import numpy as np
import glob

def parse_time(time_str: str) -> float:
    return -1.0 if time_str == 't.o.' else float(time_str)

def output_variance_results(file_pattern: str):
    files = glob.glob(file_pattern)
    if not files:
        print(f"No files found matching pattern: {file_pattern}")
        return
    print(f"Found {len(files)} files matching pattern.")
    dfs = [pd.read_csv(f) for f in files]
    num_instances = len(dfs[0])
    stats = []

    print("| ID |   Instance   | Mean Solve Time | Std. Solve Time | Coef. of Variation | # Timeouts |")
    print("|----|--------------|-----------------|-----------------|--------------------|------------|")

    for idx in range(num_instances):
        statuses = np.array([df.iloc[idx]['Status'] for df in dfs], dtype=np.str_)
        unknown_mask = (statuses == 'UNKNOWN')
        times = np.array([np.float64(parse_time(df.iloc[idx]['Time (s)'])) for df in dfs], dtype=np.float64)
        # We are only interested in 'solving' runtimes. Filter out UNKNOWNs due to timeouts.
        valid_times = times[~unknown_mask]
        timeout_count = np.count_nonzero(unknown_mask)
        mean, std, cv = "-".rjust(15), "-".rjust(15), "-".rjust(18)
        if valid_times.size > 0:
            mean = f"{np.mean(valid_times):.4f}".rjust(15)
            std = f"{np.std(valid_times):.4f}".rjust(15)
            cv = f"{(float(std) / float(mean) * 100):.4f}".rjust(18)

        id = str(idx + 1).rjust(2)
        instance = f"{dfs[0].iloc[idx]['Variant']}-{dfs[0].iloc[idx]['Model']}".ljust(12)
        timeout_count = str(timeout_count).rjust(10)

        stats = f"| {id} | {instance} | {mean} | {std} | {cv} | {timeout_count} |"
        print(stats)

    # stats_df = pd.DataFrame(stats)
    # print(stats_df)

if '__main__' == __name__:
    import sys

    if len(sys.argv) < 2:
        print("Usage: python dynamic_solvers/runtime_variance_results.py '<file_pattern>'")
        print("Note: This assumes all result files contain the benchmark for the same list of OOP instances.")
        sys.exit(1)

    output_variance_results(sys.argv[1])
