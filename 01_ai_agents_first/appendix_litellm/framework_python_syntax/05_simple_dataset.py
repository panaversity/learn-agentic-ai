"""
05_simple_dataset.py - Simplified example for large datasets

This file demonstrates good and bad practices when using dataclasses with large datasets.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import time
import random


# Good approach: Use slots to reduce memory footprint
@dataclass
class RecordWithSlots:
    """Record class with memory optimization using slots."""
    id: str
    value: float
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict, repr=True)
    
    # __slots__ must not include fields defined by dataclass
    __slots__ = ()


# Good approach: Limit what's stored in memory
@dataclass
class DatasetStats:
    """Statistics about a dataset - stored instead of all records."""
    count: int
    min_value: float
    max_value: float
    avg_value: float
    last_updated: float


class EfficientDataset:
    """A dataset that doesn't keep all records in memory."""
    
    def __init__(self, name: str):
        self.name = name
        self.stats = DatasetStats(0, float('inf'), float('-inf'), 0.0, time.time())
        self._sum = 0.0  # For calculating average
        
    def add_record(self, record_id: str, value: float):
        """Add a record, updating stats but not storing the record."""
        # Update statistics
        self.stats.count += 1
        self.stats.min_value = min(self.stats.min_value, value)
        self.stats.max_value = max(self.stats.max_value, value)
        self._sum += value
        self.stats.avg_value = self._sum / self.stats.count
        self.stats.last_updated = time.time()
        
        # In real app, would save to database/file here
        print(f"Added record {record_id} with value {value}")
    
    def get_stats(self):
        """Return current statistics without loading all records."""
        return self.stats


# Bad approach: Store everything in memory
@dataclass
class IneffcientDataset:
    """A dataset that inefficiently stores all records in memory."""
    name: str
    records: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_record(self, record_id: str, value: float):
        """Add a record to the in-memory list."""
        self.records.append({
            "id": record_id,
            "value": value,
            "timestamp": time.time()
        })
    
    def get_stats(self):
        """Calculate statistics by iterating through all records."""
        if not self.records:
            return None
        
        count = len(self.records)
        min_value = min(r["value"] for r in self.records)
        max_value = max(r["value"] for r in self.records)
        avg_value = sum(r["value"] for r in self.records) / count
        
        return {
            "count": count,
            "min_value": min_value,
            "max_value": max_value,
            "avg_value": avg_value
        }


def demo_efficient():
    print("=== EFFICIENT DATASET APPROACH ===")
    
    # Create dataset that doesn't store records
    dataset = EfficientDataset("temperature_data")
    
    # Add some records
    for i in range(10):
        dataset.add_record(f"temp_{i}", random.uniform(20, 30))
    
    # Get statistics without loading all records
    stats = dataset.get_stats()
    print(f"\nDataset stats:")
    print(f"  Count: {stats.count}")
    print(f"  Min: {stats.min_value:.2f}")
    print(f"  Max: {stats.max_value:.2f}")
    print(f"  Average: {stats.avg_value:.2f}")


def demo_inefficient():
    print("\n=== INEFFICIENT DATASET APPROACH ===")
    
    # Create dataset that stores all records in memory
    dataset = IneffcientDataset("temperature_data")
    
    # Add same records
    for i in range(10):
        dataset.add_record(f"temp_{i}", random.uniform(20, 30))
    
    # Get statistics by processing all records
    stats = dataset.get_stats()
    print(f"\nDataset stats:")
    print(f"  Count: {stats['count']}")
    print(f"  Min: {stats['min_value']:.2f}")
    print(f"  Max: {stats['max_value']:.2f}")
    print(f"  Average: {stats['avg_value']:.2f}")
    
    # Show memory issue
    print(f"\nStoring all records in memory:")
    print(f"  Total records stored: {len(dataset.records)}")
    print(f"  First few records: {dataset.records[:3]}")
    print("This approach doesn't scale for large datasets!")


if __name__ == "__main__":
    demo_efficient()
    demo_inefficient() 