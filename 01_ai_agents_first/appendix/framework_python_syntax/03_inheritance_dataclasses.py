"""
03_inheritance_dataclasses.py - Simplified example of working with dataclasses
"""

from dataclasses import dataclass, field
from typing import List, Optional


# Simple standalone dataclasses - no inheritance to avoid any ordering issues
@dataclass
class Person:
    """Base class for people."""
    name: str
    age: int
    # Fields with defaults must come after required fields
    email: Optional[str] = None


@dataclass
class Student:
    """Simple student dataclass."""
    # All required fields first
    name: str
    age: int
    student_id: str
    # Then all default fields
    email: Optional[str] = None
    courses: List[str] = field(default_factory=list)
    
    def add_course(self, course: str) -> None:
        """Add a course to the student's course list."""
        if course not in self.courses:
            self.courses.append(course)


def main():
    # Print debug info
    print("Creating a person...")
    try:
        person = Person(name="John Doe", age=30, email="john@example.com")
        print(f"Person created: {person}")
    except Exception as e:
        print(f"Error creating person: {e}")
    
    print("\nCreating a student...")
    try:
        student = Student(
            name="Alice Johnson",
            age=20,
            student_id="S12345",
            courses=["Python Programming", "Data Structures"]
        )
        print(f"Student created: {student}")
        
        student.add_course("Algorithms")
        print(f"Student courses after adding: {student.courses}")
    except Exception as e:
        print(f"Error creating student: {e}")


if __name__ == "__main__":
    print("=== SIMPLIFIED DATACLASS EXAMPLE ===")
    main()
    print("\nProgram completed successfully") 