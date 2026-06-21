import os
import csv
import argparse

TIMEOUT = 180

def main():
    parser = argparse.ArgumentParser(description='Count solved instances in CSV files.')
    parser.add_argument('directory', help='Path to the directory containing CSV files')
    args = parser.parse_args()

    directory = args.directory
    results = []
    number_instances = 0

    for filename in os.listdir(directory):
        if not filename.endswith('.csv'):
            raise ValueError(f'Unexpected file format: {filename}')
        filepath = os.path.join(directory, filename)
        solved = 0
        duration = 0.0
        if number_instances == 0:
            with open(filepath) as f:
                number_instances = sum(1 for _ in f) - 1
        with open(filepath, newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header
            for row in reader:
                status = row[6].strip().upper()
                if status != "UNKNOWN":
                    solved += 1
                    duration += float(row[4].strip())
        results.append((filename, solved, duration))

    # Sort files by solved count descending
    results.sort(key=lambda x: (x[1], -x[2]), reverse=True)

    output_results(results, number_instances)
    plot_results(results, number_instances)

def output_results(results, number_instances):
    # Print summary
    print("Order, Solved, Solved %, Time")
    for i, (filename, solved, duration) in enumerate(results):
        order = "(" + filename.replace('order-', '').replace('.csv', '').replace('_', ',') + ")"
        print(order, solved, f"{(solved / number_instances * 100):.2f}%", f"{duration:.2f}s")

def plot_results(results, number_instances):
    import matplotlib.pyplot as plt
    x_vals = [r[1] for r in results]
    y_vals = [r[2] for r in results]

    plt.figure(figsize=(8, 5))
    plt.scatter(x_vals, y_vals, color='steelblue')

    x_unique = sorted(set(x_vals))
    plt.xticks(x_unique, [f"{x} ({(x/number_instances*100):.2f}%)" for x in x_unique])
    plt.title("Solved Instances vs Cumulative Time")
    plt.xlabel("Number of Instances Solved")
    plt.ylabel("Cumulative Time (s)")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()
