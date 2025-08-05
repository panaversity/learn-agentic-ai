"""
03_alt_inheritance.py - Alternative approaches to inheritance with dataclasses

This file demonstrates better approaches for relating dataclasses without 
running into parameter ordering issues.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date


# APPROACH 1: Base class with only required fields
@dataclass
class Person:
    """Base class with only required fields."""
    name: str
    birth_date: date
    
    @property
    def age(self) -> int:
        """Calculate age based on birth date."""
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
        

# Child classes can add optional fields
@dataclass
class PersonWithEmail(Person):
    """Person with optional email field."""
    email: Optional[str] = None


@dataclass
class Student:
    """Student as a standalone class (not using inheritance)."""
    name: str
    birth_date: date
    student_id: str
    major: str
    email: Optional[str] = None
    gpa: float = 0.0
    courses: List[str] = field(default_factory=list)
    
    @property
    def age(self) -> int:
        """Calculate age based on birth date."""
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
    
    def add_course(self, course: str) -> None:
        """Add a course to the student's course list."""
        if course not in self.courses:
            self.courses.append(course)
    
    def is_honors(self) -> bool:
        """Check if the student qualifies for honors."""
        return self.gpa >= 3.5


# APPROACH 2: Composition pattern
@dataclass
class PersonInfo:
    """Personal information as a component."""
    name: str
    birth_date: date
    email: Optional[str] = None
    
    @property
    def age(self) -> int:
        """Calculate age based on birth date."""
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )


@dataclass
class TeachingStaff:
    """Teaching staff using composition."""
    person: PersonInfo  # Composition instead of inheritance
    employee_id: str
    department: str
    courses_taught: List[str] = field(default_factory=list)
    salary: float = 0.0
    
    # Delegate common attributes to the person component
    @property
    def name(self) -> str:
        return self.person.name
    
    @property
    def age(self) -> int:
        return self.person.age
    
    @property
    def email(self) -> Optional[str]:
        return self.person.email
    
    def add_course(self, course: str) -> None:
        """Add a course to teaching list."""
        if course not in self.courses_taught:
            self.courses_taught.append(course)


# APPROACH 3: Using composition with delegation
@dataclass
class BaseWithDefaults:
    """Base class with a mix of required and optional fields."""
    name: str
    # Optional field with default
    description: Optional[str] = None


@dataclass
class CompositionBased:
    """Using composition instead of inheritance."""
    # Embed the base class as a field
    base: BaseWithDefaults
    # Add our own required fields
    required_id: str
    # Add our own optional fields
    optional_value: int = 0
    
    # Delegate properties to base
    @property
    def name(self) -> str:
        return self.base.name
    
    @property
    def description(self) -> Optional[str]:
        return self.base.description
    
    def __post_init__(self):
        """Validation after initialization."""
        if not self.required_id.strip():
            raise ValueError("required_id cannot be empty")


def demo_no_inheritance():
    """Demonstrate the standalone approach."""
    student = Student(
        name="Alice Johnson",
        birth_date=date(2000, 5, 15),
        student_id="S12345",
        major="Computer Science",
        email="alice@university.edu",
        gpa=3.8,
        courses=["Python Programming", "Data Structures"]
    )
    
    print("=== APPROACH 1: STANDALONE CLASSES ===")
    print(f"Student: {student.name}, Age: {student.age}, Major: {student.major}")
    student.add_course("Algorithms")
    print(f"Student courses: {student.courses}")
    print(f"Is honors student? {student.is_honors()}")


def demo_composition():
    """Demonstrate the composition approach."""
    # Create personal info
    person_info = PersonInfo(
        name="Dr. Jane Smith",
        birth_date=date(1980, 3, 15),
        email="jane.smith@university.edu"
    )
    
    # Create teaching staff with this person info
    instructor = TeachingStaff(
        person=person_info,
        employee_id="E54321",
        department="Mathematics",
        courses_taught=["Calculus", "Linear Algebra"],
        salary=78000.0
    )
    
    print("\n=== APPROACH 2: COMPOSITION ===")
    print(f"Instructor: {instructor.name}, Age: {instructor.age}")
    print(f"Department: {instructor.department}")
    print(f"Email: {instructor.email}")
    instructor.add_course("Statistics")
    print(f"Courses taught: {instructor.courses_taught}")


def demo_composition_delegation():
    """Demonstrate the composition with delegation approach."""
    try:
        # Create the base object
        base = BaseWithDefaults(
            name="Test Name",
            description="Optional description"
        )
        
        # Create the composed object
        valid = CompositionBased(
            base=base,
            required_id="12345"
        )
        
        print("\n=== APPROACH 3: COMPOSITION WITH DELEGATION ===")
        print(f"Composed object: {valid}")
        print(f"Accessing delegated properties - Name: {valid.name}, Description: {valid.description}")
        
        # This will fail validation in __post_init__
        invalid = CompositionBased(
            base=BaseWithDefaults(name="Invalid"),
            required_id="",  # Empty ID will fail validation
        )
        print(f"Invalid instance: {invalid}")  # Should not reach here
    except ValueError as e:
        print(f"Validation error: {e}")


if __name__ == "__main__":
    demo_no_inheritance()
    demo_composition()
    demo_composition_delegation() 