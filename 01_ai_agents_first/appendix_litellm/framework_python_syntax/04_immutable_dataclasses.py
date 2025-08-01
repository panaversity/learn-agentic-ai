"""
04_immutable_dataclasses.py - Immutable dataclasses with frozen=True

This file demonstrates how to use frozen dataclasses for immutability.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, FrozenSet
import hashlib


# GOOD EXAMPLE: Immutable dataclass
@dataclass(frozen=True)
class Point:
    """An immutable 2D point."""
    x: float
    y: float
    
    def distance_from_origin(self) -> float:
        """Calculate distance from origin (0, 0)."""
        return (self.x ** 2 + self.y ** 2) ** 0.5


@dataclass(frozen=True)
class Rectangle:
    """An immutable rectangle defined by two points."""
    top_left: Point
    bottom_right: Point
    
    @property
    def width(self) -> float:
        """Calculate width of the rectangle."""
        return abs(self.bottom_right.x - self.top_left.x)
    
    @property
    def height(self) -> float:
        """Calculate height of the rectangle."""
        return abs(self.top_left.y - self.bottom_right.y)
    
    @property
    def area(self) -> float:
        """Calculate area of the rectangle."""
        return self.width * self.height
    
    # Factory method pattern for creating new instances
    def translate(self, dx: float, dy: float) -> 'Rectangle':
        """Return a new rectangle translated by (dx, dy)."""
        new_top_left = Point(self.top_left.x + dx, self.top_left.y + dy)
        new_bottom_right = Point(self.bottom_right.x + dx, self.bottom_right.y + dy)
        return Rectangle(new_top_left, new_bottom_right)


@dataclass(frozen=True)
class ImmutableConfig:
    """Configuration that cannot be changed after creation."""
    app_name: str
    version: str
    max_connections: int
    # Using immutable types for collections
    allowed_paths: Tuple[str, ...] = field(default_factory=tuple)
    feature_flags: FrozenSet[str] = field(default_factory=frozenset)
    
    def __post_init__(self):
        """Validate the configuration after initialization."""
        # Since we can't modify self directly in a frozen dataclass, this only validates
        if not self.app_name:
            raise ValueError("App name cannot be empty")
        if self.max_connections <= 0:
            raise ValueError("Max connections must be positive")


def demo_good_immutable():
    # Create immutable point objects
    p1 = Point(3, 4)
    p2 = Point(8, 2)
    
    # Create an immutable rectangle
    rect = Rectangle(p1, p2)
    
    print(f"Rectangle: top_left={rect.top_left}, bottom_right={rect.bottom_right}")
    print(f"Width: {rect.width}, Height: {rect.height}, Area: {rect.area}")
    
    # Create a new rectangle by translation (doesn't modify the original)
    moved_rect = rect.translate(2, 3)
    print(f"Moved Rectangle: top_left={moved_rect.top_left}, bottom_right={moved_rect.bottom_right}")
    
    # Trying to modify will raise an exception
    try:
        rect.top_left = Point(1, 1)
    except Exception as e:
        print(f"Cannot modify frozen dataclass: {e}")
        
    # Create an immutable configuration
    config = ImmutableConfig(
        app_name="MyApp",
        version="1.0.0",
        max_connections=100,
        allowed_paths=("/api", "/public", "/assets"),
        feature_flags=frozenset({"dark_mode", "new_ui"})
    )
    
    print(f"Config: {config}")
    
    # Attempt to create an invalid config
    try:
        invalid_config = ImmutableConfig(
            app_name="",  # Empty name, should fail validation
            version="1.0.0",
            max_connections=100
        )
    except ValueError as e:
        print(f"Validation error: {e}")


# BAD EXAMPLE 1: Mutable attributes in immutable dataclass
@dataclass(frozen=True)
class BadImmutable:
    name: str
    # A mutable list in an "immutable" class
    values: List[int] = field(default_factory=list)
    # A mutable dict in an "immutable" class
    metadata: Dict[str, str] = field(default_factory=dict)


def demo_bad_immutable():
    # Create a supposedly immutable object
    bad = BadImmutable("example", [1, 2, 3], {"key": "value"})
    
    print("\n=== BAD IMMUTABLE DATACLASS EXAMPLE ===")
    print(f"Original: {bad}")
    
    # The object itself is immutable (can't reassign attributes)
    try:
        bad.name = "new_name"
    except Exception as e:
        print(f"Cannot modify attribute: {e}")
    
    # But you can modify the mutable contents!
    bad.values.append(4)
    bad.metadata["new_key"] = "new_value"
    
    print(f"After modifications to internal mutable objects: {bad}")
    print("This breaks immutability expectations!")


# BAD EXAMPLE 2: Trying to use __init__ to modify a frozen dataclass
@dataclass(frozen=True)
class BadInitImmutable:
    value: int
    squared: int = None  # We want to compute this in init
    
    def __init__(self, value: int):
        # This will fail!
        self.value = value
        self.squared = value ** 2


# FIXED EXAMPLE: Using __post_init__ and object.__setattr__ for initialization
@dataclass(frozen=True)
class GoodInitImmutable:
    value: int
    squared: int = field(init=False)  # Don't include in init parameters
    
    def __post_init__(self):
        # Use object.__setattr__ to bypass the frozen restriction during initialization
        object.__setattr__(self, "squared", self.value ** 2)


def demo_init_issues():
    print("\n=== ISSUES WITH INITIALIZING FROZEN DATACLASSES ===")
    
    # This will fail
    try:
        bad_init = BadInitImmutable(5)
        print(f"BadInitImmutable: {bad_init}")
    except Exception as e:
        print(f"BadInitImmutable error: {e}")
    
    # This works correctly
    good_init = GoodInitImmutable(5)
    print(f"GoodInitImmutable: {good_init}")


if __name__ == "__main__":
    print("=== GOOD IMMUTABLE DATACLASS EXAMPLES ===")
    demo_good_immutable()
    
    print("\n=== BAD IMMUTABLE DATACLASS EXAMPLES ===")
    demo_bad_immutable()
    
    demo_init_issues() 