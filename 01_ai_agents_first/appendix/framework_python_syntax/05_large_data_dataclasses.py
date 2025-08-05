"""
05_large_data_dataclasses.py - Using dataclasses with large datasets

This file demonstrates both good and bad practices when using dataclasses with large amounts of data.
"""

from dataclasses import dataclass, field, astuple, asdict
import time
import sys
from typing import List, Dict, Any, Optional
import json
from functools import lru_cache
import random


# GOOD EXAMPLE 1: Efficient dataclass for large data
@dataclass
class Record:
    """Dataclass for individual records."""
    id: str
    timestamp: float
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Using slots can reduce memory usage significantly for large numbers of instances
    __slots__ = ('id', 'timestamp', 'value', 'metadata')


# GOOD EXAMPLE 2: Dataclass with responsible handling of large data
@dataclass
class DatasetStats:
    """Statistics about a dataset, not containing the full data."""
    count: int
    min_value: float
    max_value: float
    avg_value: float
    last_updated: float


@dataclass
class Dataset:
    """A dataset class that manages records efficiently."""
    name: str
    description: Optional[str] = None
    # We don't store all records in memory by default
    _stats: Optional[DatasetStats] = None
    # Reference to where data is stored, not the data itself
    _data_path: Optional[str] = None
    
    @property
    def stats(self) -> DatasetStats:
        """Get statistics about the dataset without loading all records."""
        if self._stats is None:
            # In a real application, this might compute stats from a database or file
            # For demo purposes, we'll create dummy stats
            self._stats = DatasetStats(
                count=1000,
                min_value=0.0,
                max_value=100.0,
                avg_value=50.0,
                last_updated=time.time()
            )
        return self._stats
    
    def get_record_batch(self, start: int, limit: int) -> List[Record]:
        """Get a batch of records, loading only what's needed."""
        # In a real app, this would fetch from a database or file
        # For demo purposes, we'll generate some dummy records
        return [
            Record(
                id=f"rec_{i}",
                timestamp=time.time() - (1000 - i),
                value=random.uniform(0, 100),
                metadata={"batch": f"{start}-{start+limit}"}
            )
            for i in range(start, min(start + limit, 1000))
        ]
    
    @lru_cache(maxsize=100)
    def get_record(self, record_id: str) -> Optional[Record]:
        """Get a single record by ID with caching for frequently accessed records."""
        # In a real app, this would do a targeted query/lookup
        # For demo purposes, we'll just check if the ID matches our pattern
        if not record_id.startswith("rec_"):
            return None
        
        try:
            num = int(record_id.split("_")[1])
            if 0 <= num < 1000:
                return Record(
                    id=record_id,
                    timestamp=time.time() - (1000 - num),
                    value=random.uniform(0, 100),
                    metadata={"lookup": "direct"}
                )
        except (IndexError, ValueError):
            pass
        
        return None


def demo_good_large_data():
    # Create a dataset
    dataset = Dataset(
        name="sensor_data",
        description="Temperature readings from sensors"
    )
    
    # Get statistics without loading all data
    stats = dataset.stats
    print(f"Dataset: {dataset.name}")
    print(f"Stats: {stats}")
    
    # Load only a small batch of records
    batch = dataset.get_record_batch(0, 5)
    print(f"First 5 records: {batch}")
    
    # Lookup a specific record with caching
    record = dataset.get_record("rec_42")
    print(f"Record 42: {record}")
    
    # Second lookup of the same record (will use cache)
    start_time = time.time()
    record_again = dataset.get_record("rec_42")
    end_time = time.time()
    print(f"Record 42 (cached): {record_again}")
    print(f"Cached lookup time: {(end_time - start_time)*1000:.2f} ms")


# BAD EXAMPLE 1: Loading all data into memory
@dataclass
class LargeDatasetBad:
    """A dataset that inefficiently loads all records into memory."""
    name: str
    # This will consume a lot of memory for large datasets
    records: List[Record] = field(default_factory=list)
    
    def load_all_data(self, num_records: int = 1000000):
        """Load a large number of records into memory."""
        print(f"Loading {num_records} records into memory...")
        start_time = time.time()
        
        # This would overwhelm memory for truly large datasets
        self.records = [
            Record(
                id=f"rec_{i}",
                timestamp=time.time(),
                value=random.uniform(0, 100),
                metadata={"batch": "full_load"}
            )
            for i in range(num_records)
        ]
        
        end_time = time.time()
        print(f"Loaded {len(self.records)} records in {end_time - start_time:.2f} seconds")
        
        # Calculate memory usage
        record_size = sys.getsizeof(self.records[0]) if self.records else 0
        estimated_size = record_size * len(self.records) / (1024 * 1024)  # in MB
        print(f"Estimated memory usage: {estimated_size:.2f} MB")


# BAD EXAMPLE 2: Inefficient nested dataclasses
@dataclass
class MetadataBad:
    """Inefficient metadata with redundancy."""
    created_by: str
    created_at: float
    updated_by: str
    updated_at: float
    description: str = ""


@dataclass
class LocationBad:
    """Inefficient location data."""
    latitude: float
    longitude: float
    altitude: float
    accuracy: float
    # Nested dataclass with redundant data
    metadata: MetadataBad = field(default_factory=lambda: MetadataBad(
        created_by="system",
        created_at=time.time(),
        updated_by="system",
        updated_at=time.time()
    ))


@dataclass
class SensorReadingBad:
    """Inefficient sensor reading with deeply nested dataclasses."""
    id: str
    sensor_type: str
    value: float
    timestamp: float
    # Nested dataclass with more nested dataclasses
    location: LocationBad
    # More metadata (duplicating the pattern)
    metadata: MetadataBad = field(default_factory=lambda: MetadataBad(
        created_by="system",
        created_at=time.time(),
        updated_by="system",
        updated_at=time.time()
    ))


@dataclass
class SensorDatasetBad:
    """Inefficient dataset with deep nesting."""
    name: str
    # Deep nesting with many redundant fields
    readings: List[SensorReadingBad] = field(default_factory=list)
    # Yet another metadata instance
    metadata: MetadataBad = field(default_factory=lambda: MetadataBad(
        created_by="system",
        created_at=time.time(),
        updated_by="system",
        updated_at=time.time()
    ))
    
    def to_json(self) -> str:
        """Convert the entire dataset to JSON (inefficient for large datasets)."""
        # This will be very slow and memory intensive for large datasets
        return json.dumps(asdict(self), indent=2)


def demo_bad_large_data():
    print("\n=== BAD EXAMPLES WITH LARGE DATA ===")
    
    # Example with loading too much data
    large_dataset = LargeDatasetBad("too_much_data")
    large_dataset.load_all_data(10000)  # Try with 10K instead of 1M for the demo
    
    # Example with inefficient nesting
    bad_dataset = SensorDatasetBad(name="bad_nested_data")
    
    # Add some readings with deep nesting
    for i in range(5):
        bad_dataset.readings.append(
            SensorReadingBad(
                id=f"reading_{i}",
                sensor_type="temperature",
                value=random.uniform(20, 30),
                timestamp=time.time(),
                location=LocationBad(
                    latitude=37.7749,
                    longitude=-122.4194,
                    altitude=10,
                    accuracy=5.0
                )
            )
        )
    
    # Convert to JSON (inefficient for large datasets)
    print("Converting nested dataset to JSON...")
    start_time = time.time()
    json_data = bad_dataset.to_json()
    end_time = time.time()
    
    print(f"JSON conversion time: {end_time - start_time:.4f} seconds")
    print(f"JSON data size: {len(json_data)} bytes")
    print("First 200 characters of JSON:")
    print(json_data[:200] + "...")


# SOLUTION FOR LARGE DATASETS
@dataclass(slots=True)
class EfficientReading:
    """Efficient reading with flat structure and slots."""
    id: str
    sensor_type: str
    value: float
    timestamp: float
    # Flat structure instead of nesting
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    # Only essential metadata
    created_at: float = field(default_factory=time.time)
    # Use a simple dict for optional metadata
    tags: Dict[str, Any] = field(default_factory=dict)


class EfficientDataset:
    """Non-dataclass for very large datasets."""
    def __init__(self, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description
        self._stats = {
            "count": 0,
            "min_value": float('inf'),
            "max_value": float('-inf'),
            "sum_value": 0,
        }
        # Don't store all readings in memory
        self._storage_path = f"data/{name}.jsonl"
    
    def add_reading(self, reading: EfficientReading) -> None:
        """Add a reading and update stats without storing all in memory."""
        # Update stats
        self._stats["count"] += 1
        self._stats["min_value"] = min(self._stats["min_value"], reading.value)
        self._stats["max_value"] = max(self._stats["max_value"], reading.value)
        self._stats["sum_value"] += reading.value
        
        # In a real implementation, we would append to storage (file, database)
        # For demo purposes, we'll just print
        print(f"Added reading {reading.id} to storage")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics."""
        stats = dict(self._stats)
        if stats["count"] > 0:
            stats["avg_value"] = stats["sum_value"] / stats["count"]
        return stats


def demo_efficient_large_data():
    print("\n=== EFFICIENT SOLUTION FOR LARGE DATA ===")
    
    # Create an efficient dataset that doesn't load everything into memory
    dataset = EfficientDataset("efficient_sensor_data", "Temperature readings")
    
    # Add readings one by one
    for i in range(10):
        reading = EfficientReading(
            id=f"eff_reading_{i}",
            sensor_type="temperature",
            value=random.uniform(20, 30),
            timestamp=time.time(),
            latitude=37.7749,
            longitude=-122.4194,
            tags={"location": "San Francisco", "unit": "Celsius"}
        )
        dataset.add_reading(reading)
    
    # Get statistics without loading all data
    stats = dataset.get_stats()
    print(f"Dataset Stats: {stats}")


if __name__ == "__main__":
    print("=== GOOD LARGE DATA EXAMPLES ===")
    demo_good_large_data()
    
    demo_bad_large_data()
    
    demo_efficient_large_data() 