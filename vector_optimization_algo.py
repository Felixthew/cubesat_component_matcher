# doublecheck the math, I relied on the internet on how to do weighted euclidian distance.
# claude helped a lot on this
import random
import timeit
import numpy as np
from scipy.spatial.distance import cdist
from typing import Dict, Tuple, List


def compute(vectors: Dict[str, List[float]], query: List[float], weights: List[float]) -> list[
    tuple[str, float]]:
    """
    Computes a relevance score between each vector and the query vector, weighted by the weights.
    This relevance score is calculated by weighted euclidian distance. The lower score (distance)
    means higher relevance.

    :param vectors: A dictionary mapping vector name to vector value.
    :param query: The query vector.
    :param weights: The weights vector.
    :return: A list of tuples containing the name and the relevance score, sorted from most relevant
    to least relevant.
    """
    # Your data with string labels
    labels = list(vectors.keys())
    vector_list = np.array(list(vectors.values()))
    query_vector = np.array(query)
    weights_vector = np.array(weights)

    weighted_vectors = vector_list * weights_vector
    query_weighted = query_vector * weights_vector

    # Compute all distances
    distances = cdist([query_weighted], weighted_vectors, metric='euclidean')[0]

    # Or if you want them sorted by distance
    sorted_pairs = sorted(zip(labels, distances), key=lambda x: x[1])
    print("Nearest to farthest:")
    for label, dist in sorted_pairs:
        print(f"{label}: {dist:.3f}")

    return sorted_pairs


def create_test_input(n: int) -> Tuple[Dict[str, List[float]], List[float], List[float]]:
    """Create test input with n vectors for the compute function"""

    random.seed(42)
    vector_size = 10

    # Create 100 vectors
    vectors = {}
    for i in range(n):
        vector = [round(random.uniform(-5.0, 5.0), 3) for _ in range(vector_size)]
        vectors[f"vector_{i:03d}"] = vector

    # Create query and weights
    query = [round(random.uniform(-5.0, 5.0), 3) for _ in range(vector_size)]
    weights = [round(random.uniform(0.1, 1.0), 3) for _ in range(vector_size)]

    return vectors, query, weights


def main():
    # took my pc 6 seconds for 1_000_000
    vectors, query, weights = create_test_input(100)
    time_taken = timeit.timeit(
        lambda: compute(vectors, query, weights),
        number=1
    )
    print("Took", time_taken, "seconds")


main()
