#!/usr/bin/env python3
"""Test the similarity calculation with actual distances from ChromaDB."""

import math

# Actual distances from our debug output
distances = [163.86, 276.71, 294.40, 437.54]

print("Testing similarity calculation with exponential decay:")
print("Formula: similarity = exp(-0.01 * distance)")
print("-" * 60)

for distance in distances:
    similarity = math.exp(-0.01 * distance)
    print(f"Distance: {distance:8.2f} -> Similarity: {similarity:.6f}")

print("\n" + "=" * 60)
print("Testing different thresholds:")
print("-" * 60)

thresholds = [0.3, 0.5, 0.7, 0.9]
for threshold in thresholds:
    passing = [d for d in distances if math.exp(-0.01 * d) >= threshold]
    print(f"Threshold {threshold}: {len(passing)} results pass")

print("\n" + "=" * 60)
print("Alternative: Using a different decay factor")
print("-" * 60)

# Try different decay factors
decay_factors = [0.001, 0.005, 0.01, 0.02]
for factor in decay_factors:
    print(f"\nDecay factor: {factor}")
    for distance in distances[:2]:  # Show first 2
        similarity = math.exp(-factor * distance)
        print(f"  Distance {distance:.2f} -> Similarity: {similarity:.6f}")