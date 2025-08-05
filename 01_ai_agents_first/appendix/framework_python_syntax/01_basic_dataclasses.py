"""
01_basic_dataclasses.py - Basic usage of dataclasses

This file demonstrates the proper use of dataclasses for simple data structures.
"""

from dataclasses import dataclass, field
from typing import List, Optional


# GOOD EXAMPLE: Simple dataclass with type hints
@dataclass
class Person:
    name: str
    age: int
    email: Optional[str] = None
    # Using field() with default_factory for mutable default values
    tags: List[str] = field(default_factory=list)
    
    def is_adult(self) -> bool:
        """Example method that uses the dataclass attributes."""
        return self.age >= 18


# Usage example
def demo_good_usage():
    # Creating instances
    person1 = Person(name="Alice", age=30, email="alice@example.com")
    person2 = Person(name="Bob", age=25)
    person3 = Person(name="Charlie", age=17, tags=["student", "part-time"])
    
    # Adding to a mutable field
    person1.tags.append("developer")
    
    # Using the built-in string representation
    print(f"Person 1: {person1}")
    print(f"Person 2: {person2}")
    print(f"Person 3: {person3}")
    
    # Using the instance method
    print(f"Is {person1.name} an adult? {person1.is_adult()}")
    print(f"Is {person3.name} an adult? {person3.is_adult()}")


# BAD EXAMPLE: Class without dataclass
class PersonBad:
    def __init__(self, name, age, email=None, tags=None):
        self.name = name
        self.age = age
        self.email = email
        # Common mistake: mutable default
        self.tags = tags if tags is not None else []
    
    # Have to manually define string representation
    def __repr__(self):
        return f"PersonBad(name={self.name}, age={self.age}, email={self.email}, tags={self.tags})"
    
    # Have to manually define equality
    def __eq__(self, other):
        if not isinstance(other, PersonBad):
            return False
        return (self.name == other.name and 
                self.age == other.age and 
                self.email == other.email and 
                self.tags == other.tags)


def demo_bad_usage():
    # More verbose and error-prone without dataclasses
    person1 = PersonBad("Alice", 30, "alice@example.com")
    person2 = PersonBad("Bob", 25)
    
    print(f"PersonBad 1: {person1}")
    print(f"PersonBad 2: {person2}")


if __name__ == "__main__":
    print("=== GOOD DATACLASS EXAMPLES ===")
    demo_good_usage()
    
    print("\n=== BAD REGULAR CLASS EXAMPLES ===")
    demo_bad_usage() 