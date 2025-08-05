"""
03_simple_inheritance.py - Simplified inheritance with dataclasses

This file demonstrates how to properly use inheritance with dataclasses.
"""

from dataclasses import dataclass, field, fields
from typing import List, Optional
from datetime import date


# Base class - no default values to avoid inheritance issues
@dataclass
class Person:
    """Base class for people."""
    name: str
    age: int
    
    def greet(self) -> str:
        """Simple greeting method."""
        return f"Hello, my name is {self.name}."


# Derived class with fields from both classes
@dataclass
class Employee(Person):
    """Employee class that inherits from Person."""
    # First all required fields (both from parent and this class)
    employee_id: str
    department: str
    # Then all optional fields
    email: Optional[str] = None
    salary: float = 0.0
    skills: List[str] = field(default_factory=list)
    
    def work(self) -> str:
        """What the employee does."""
        return f"{self.name} is working in {self.department}."
    
    def add_skill(self, skill: str) -> None:
        """Add a skill to the employee's skill list."""
        if skill not in self.skills:
            self.skills.append(skill)


def demo_good_inheritance():
    print("\nDemonstrating dataclass inheritance:")
    # Create an employee
    employee = Employee(
        name="John Doe",
        age=30,
        employee_id="E12345",
        department="Engineering",
        email="john@example.com",
        salary=75000.0,
        skills=["Python", "Data Analysis"]
    )
    
    # Use inherited methods and properties
    print(f"Employee: {employee}")
    print(f"Name: {employee.name}")
    print(f"Age: {employee.age}")
    print(f"Email: {employee.email}")
    print(f"Employee ID: {employee.employee_id}")
    print(f"Department: {employee.department}")
    print(f"Greeting: {employee.greet()}")
    print(f"Working: {employee.work()}")
    
    # Add a skill
    employee.add_skill("Machine Learning")
    print(f"Skills: {employee.skills}")
    
    # Show all fields (including inherited ones)
    all_fields = fields(Employee)
    print("\nAll fields in Employee class:")
    for f in all_fields:
        print(f"  {f.name}: {f.type}")


# Alternative approach using composition instead of inheritance
@dataclass
class PersonInfo:
    """Personal information."""
    name: str
    age: int
    email: Optional[str] = None


@dataclass
class EmployeeComposition:
    """Employee using composition instead of inheritance."""
    # Contain a PersonInfo object rather than inheriting
    person: PersonInfo
    employee_id: str
    department: str
    salary: float = 0.0
    skills: List[str] = field(default_factory=list)
    
    def greet(self) -> str:
        """Forward to the person's greet method."""
        return f"Hello, my name is {self.person.name}."
    
    def work(self) -> str:
        """What the employee does."""
        return f"{self.person.name} is working in {self.department}."
    
    def add_skill(self, skill: str) -> None:
        """Add a skill to the employee's skill list."""
        if skill not in self.skills:
            self.skills.append(skill)


def demo_composition():
    print("\nDemonstrating composition as an alternative to inheritance:")
    # Create a person
    person = PersonInfo(
        name="Jane Smith",
        age=35,
        email="jane@example.com"
    )
    
    # Create an employee with the person
    employee = EmployeeComposition(
        person=person,
        employee_id="E67890",
        department="Management",
        salary=85000.0,
        skills=["Leadership", "Communication"]
    )
    
    print("\n=== COMPOSITION EXAMPLE ===")
    print(f"Employee: {employee}")
    print(f"Employee's name via person: {employee.person.name}")
    print(f"Employee's age via person: {employee.person.age}")
    print(f"Greeting: {employee.greet()}")
    print(f"Working: {employee.work()}")
    
    # Access person's attributes through the composition
    print(f"Person's email: {employee.person.email}")


if __name__ == "__main__":
    print("=== DATACLASS INHERITANCE EXAMPLE ===")
    demo_good_inheritance()
    
    print("\n=== COMPOSITION ALTERNATIVE ===")
    demo_composition() 