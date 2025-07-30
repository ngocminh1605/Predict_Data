import numpy as np
from tempfile import TemporaryDirectory
import warnings
from utils import FilePath
from custom_types import *
from utils import (
    get_single_value_from_file,
    get_multiple_values_from_file,
    read_file_contents,
)
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform

from predict.iqtree import IQTree


def get_iqtree_llh(iqtree_file: str) -> float:
    STR = "Optimal log-likelihood:"
    return get_single_value_from_file(iqtree_file, STR)


def get_iqtree_starting_llh(iqtree_file: str) -> float:
    try:
        return get_single_value_from_file(iqtree_file, "Initial log-likelihood:")
    except ValueError:
        warnings.warn("The given file does not contain the starting LLH: " + iqtree_file)
        return -np.inf

def get_all_iqtree_llhs(iqtree_file: str) -> List[float]:
    STR = "Optimal log-likelihood:"
    return get_multiple_values_from_file(iqtree_file, STR)


def get_best_iqtree_llh(iqtree_file: str) -> float:
    all_llhs = get_all_iqtree_llhs(iqtree_file)
    return max(all_llhs)


# def get_iqtree_time_from_line(line: str) -> float:
    

# def get_iqtree_elapsed_time(log_file: str) -> float:
#     content = read_file_contents(log_file)

#     for line in content:
#         if "Elapsed time:" not in line:
#             continue
#         else:
#             return get_iqtree_time_from_line(line)

#     raise ValueError(
#         f"The given input file {log_file} does not contain the elapsed time."
#     )


# def get_iqtree_runtimes(log_file: str) -> List[float]:
#     content = read_file_contents(log_file)

#     all_times = []

#     for line in content:
#         if "Elapsed time:" not in line:
#             continue
#         else:
#             all_times.append(get_iqtree_time_from_line(line))

#     if not all_times:
#         raise ValueError(
#             f"The given input file {log_file} does not contain the elapsed time."
#         )

#     return all_times
def get_iqtree_elapsed_times(log_file: str) -> List[float]:
    """
    Extract all elapsed times (in seconds) from IQ-TREE log file.
    This handles both:
    - "Elapsed time: 63514.086 seconds"
    - "Total wall-clock time used: 0.124 sec"
    """
    content = read_file_contents(log_file)
    times = []
    for line in content:
        if "Elapsed time:" in line and "seconds" in line:
            try:
                times.append(get_value_from_line(line, "Elapsed time:"))
            except:
                continue
        elif "Total wall-clock time used:" in line:
            try:
                times.append(get_value_from_line(line, "Total wall-clock time used:"))
            except:
                continue
    return times

def get_iqtree_elapsed_time(log_file: str) -> float:
    times = get_iqtree_elapsed_times(log_file)
    if times:
        return times[0]
    raise ValueError(f"The given input file {log_file} does not contain the elapsed time.")


def get_iqtree_runtimes(log_file: str) -> List[float]:
    times = get_iqtree_elapsed_times(log_file)
    if not times:
        raise ValueError(f"The given input file {log_file} does not contain the elapsed time.")
    return times


def rel_rfdistance_starting_final(
    newick_starting: str,
    newick_final: str,
    iqtree_executable: str = "iqtree",
) -> float:

    with TemporaryDirectory() as tmpdir:
        iqtree_runner = IQTree(iqtree_executable)
        trees_file = tmpdir + "/input.trees"
        with open(trees_file, "w") as f:
            f.write(newick_starting.strip() + "\n" + newick_final.strip())

        _, rel_rfdist, _ = iqtree_runner.get_rfdistance_results(trees_file)

        return rel_rfdist


def get_model_parameter_estimates(iqtree_file: str) -> Tuple[str, str, str]:
    """
    For now just store everyting as string, different models result in different strings
    and I don't want to commit to parsing just yet
    TODO: adapt this for multiple partitions, in this case return a dict instead of a string with the partition name as key and the corresponding string as value
    """
    content = read_file_contents(iqtree_file)

    rate_het = None
    base_freq = None
    subst_rates = None

    for line in content:
        if line.startswith("Rate heterogeneity"):
            _, res = line.split(":", 1)
            rate_het = res.strip()
        if line.startswith("Base frequencies"):
            _, res = line.split(":", 1)
            base_freq = res.strip()

    return rate_het, base_freq, subst_rates


# def get_all_parsimony_scores(log_file: str) -> List[float]:
#     content = read_file_contents(log_file)

#     scores = []

#     for line in content:
#         if "Parsimony score" not in line:
#             continue

#         _, score = line.split(":")
#         score = int(score.strip())
#         scores.append(score)

#     return scores


def get_patterns_gaps_invariant(log_file: str) -> Tuple[int, float, float]:
    content = read_file_contents(log_file)
    patterns = None
    gaps = None
    invariant = None

    for line in content:
        if "Alignment has" in line:
            parts = line.strip().split(",")
            for p in parts:
                if "distinct patterns" in p:
                    patterns = int(p.strip().split(" ")[0])
        elif "Gap/Ambiguity" in line:
            continue
        elif "TOTAL" in line:
            gaps = float(line.strip().split()[1].replace('%', '')) / 100.0
        elif "constant sites" in line:
            tokens = line.strip().split(",")
            for token in tokens:
                if "constant sites" in token:
                    num_constant = int(token.strip().split(" ")[0])
                    for l in content:
                        if "Alignment has" in l:
                            total_sites = int(l.split("with")[1].split("columns")[0].strip())
                            invariant = num_constant / total_sites
                            break

    if None in (patterns, gaps, invariant):
        raise ValueError("Error parsing patterns/gaps/invariant from IQ-TREE log: " + log_file)
    return patterns, gaps, invariant



# def get_iqtree_rfdist_results(rfdist_file: FilePath) -> Tuple[int, float]:
#     """
#     Parse IQ-TREE RF distance matrix file to compute:
#     - Number of unique topologies (số cây)
#     - Average normalized RF distance

#     Args:
#         rfdist_file (str): Path to .rfdist file

#     Returns:
#         Tuple[int, float]: (number of trees, average RF distance)
#     """
#     with open(rfdist_file) as f:
#         lines = f.readlines()
#     n = int(lines[0].split()[0])
#     if n < 2:
#         raise ValueError("Không đủ cây để tính RF")
#     # Đọc ma trận
#     matrix = [
#         list(map(float, line.strip().split()[1:]))  # Bỏ tên Tree0, Tree1...
#         for line in lines[1:]
#     ]

#     # Tính trung bình RF trên tam giác trên
#     total = 0.0
#     count = 0
#     for i in range(n):
#         for j in range(i + 1, n):
#             total += matrix[i][j]
#             count += 1

#     avg_rf = total / count if count > 0 else 0.0
#     return n, avg_rf

def get_iqtree_rfdist_results(rfdist_file: FilePath, threshold: float = 0.1) -> Tuple[int, float, list]:
    """
    Parse IQ-TREE RF distance matrix (.rf.dist) để:
    - Đếm số topology khác biệt (số cluster)
    - Tính RF trung bình
    - Trả về danh sách cluster (danh sách index cây)

    Returns:
        Tuple[int, float, list[set[int]]]: (num_topo, avg_rf, clusters)
    """
    with open(rfdist_file) as f:
        lines = f.readlines()

    n = int(lines[0].split()[0])
    if n < 2:
        return 1, 0.0, [set([0])]

    # Parse ma trận RF
    matrix = [
        list(map(float, line.strip().split()[1:]))  # bỏ tên Tree0,...
        for line in lines[1:]
    ]

    # Tính trung bình RF trên tam giác trên
    total = 0.0
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            total += matrix[i][j]
            count += 1
    avg_rf = total / count if count > 0 else 0.0

    # Dùng clustering
    dist_array = squareform(np.array(matrix))
    Z = linkage(dist_array, method="average")
    labels = fcluster(Z, t=threshold, criterion="distance")

    clusters = {}
    for i, label in enumerate(labels):
        clusters.setdefault(label, set()).add(i)

    return len(clusters), avg_rf, list(clusters.values())