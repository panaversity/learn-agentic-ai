"""
02_nested_dataclasses.py - Working with nested dataclasses

This file demonstrates how to properly structure and work with nested dataclasses.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
import json


# GOOD EXAMPLE: Well-structured nested dataclasses
@dataclass
class Address:
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"


@dataclass
class Contact:
    email: str
    phone: Optional[str] = None
    

@dataclass
class Employee:
    id: int
    name: str
    department: str
    # Nested dataclass as a field
    address: Address
    # Another nested dataclass
    contact: Contact
    # List of another dataclass type
    skills: List[str] = field(default_factory=list)
    
    def to_json(self) -> str:
        """Convert the employee data to JSON string."""
        # asdict recursively converts dataclasses to dictionaries
        return json.dumps(asdict(self), indent=2)
    
    def add_skill(self, skill: str) -> None:
        """Add a skill to the employee's skill list."""
        if skill not in self.skills:
            self.skills.append(skill)


# Usage example - Good pattern
def demo_good_nested():
    # Create nested dataclass instances
    address = Address(
        street="123 Tech Lane",
        city="San Francisco",
        state="CA",
        zip_code="94107"
    )
    
    contact = Contact(
        email="john.doe@example.com",
        phone="555-123-4567"
    )
    
    # Create the parent dataclass with nested instances
    employee = Employee(
        id=1001,
        name="John Doe",
        department="Engineering",
        address=address,
        contact=contact,
        skills=["Python", "Data Science"]
    )
    
    # Access nested attributes with proper dot notation
    print(f"Employee: {employee.name}")
    print(f"City: {employee.address.city}")
    print(f"Email: {employee.contact.email}")
    
    # Add a skill
    employee.add_skill("Machine Learning")
    print(f"Skills: {employee.skills}")
    
    # Convert to JSON
    print("\nEmployee JSON:")
    print(employee.to_json())


# BAD EXAMPLE: Poorly structured data without proper nesting
@dataclass
class EmployeeBad:
    id: int
    name: str
    department: str
    # Flat structure instead of proper nesting
    street: str
    city: str
    state: str
    zip_code: str
    email: str
    # Fields with default values must come after required fields
    phone: Optional[str] = None
    country: str = "USA"
    skills: List[str] = field(default_factory=list)


# Even worse example: using dictionaries instead of proper dataclasses
class EmployeeWorse:
    def __init__(self, id, name, department, address_dict, contact_dict, skills=None):
        self.id = id
        self.name = name
        self.department = department
        # Using dictionaries instead of proper dataclasses
        self.address = address_dict  # {"street": "...", "city": "...", ...}
        self.contact = contact_dict  # {"email": "...", "phone": "..."}
        self.skills = skills or []


def demo_bad_nested():
    # Flat structure makes it harder to organize and maintain
    employee_bad = EmployeeBad(
        id=1001,
        name="John Doe",
        department="Engineering",
        street="123 Tech Lane",
        city="San Francisco",
        state="CA",
        zip_code="94107",
        email="john.doe@example.com",
        phone="555-123-4567",
        skills=["Python", "Data Science"]
    )
    
    print("\n=== BAD FLAT STRUCTURE ===")
    print(f"Employee: {employee_bad}")
    
    # Using dictionaries is even worse
    employee_worse = EmployeeWorse(
        id=1001,
        name="John Doe",
        department="Engineering",
        address_dict={
            "street": "123 Tech Lane",
            "city": "San Francisco",
            "state": "CA",
            "zip_code": "94107"
        },
        contact_dict={
            "email": "john.doe@example.com",
            "phone": "555-123-4567"
        },
        skills=["Python", "Data Science"]
    )
    
    print("\n=== WORSE DICTIONARY APPROACH ===")
    # No nice string representation
    print(f"Employee: {employee_worse.__dict__}")
    # Error-prone access to nested data
    print(f"City: {employee_worse.address['city']}")


if __name__ == "__main__":
    print("=== GOOD NESTED DATACLASS EXAMPLE ===")
    demo_good_nested()
    
    print("\n=== BAD NESTED DATACLASS EXAMPLES ===")
    demo_bad_nested() 