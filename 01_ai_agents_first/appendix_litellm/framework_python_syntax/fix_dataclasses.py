"""
fix_dataclasses.py - A simple example of working dataclasses
"""

from dataclasses import dataclass, field
from typing import List, Optional
import sys

# Set buffer for print statements to avoid buffering issues
print("Python Version:", sys.version)
print("Output is unbuffered")


# Simple dataclass with no inheritance
@dataclass
class Person:
    name: str
    age: int
    email: Optional[str] = None


@dataclass
class Student:
    name: str
    age: int
    student_id: str
    gpa: float = 0.0
    courses: List[str] = field(default_factory=list)
    
    def add_course(self, course):
        self.courses.append(course)


def main():
    # Create and print a person
    print("Creating person...")
    person = Person(name="John Doe", age=30)
    print(f"Person created: {person}")
    
    # Create and print a student
    print("\nCreating student...")
    student = Student(
        name="Alice Smith", 
        age=20, 
        student_id="S12345"
    )
    print(f"Student created: {student}")
    
    # Add courses to the student
    student.add_course("Python Programming")
    student.add_course("Data Structures")
    print(f"Student with courses: {student}")


if __name__ == "__main__":
    print("===== DATACLASS DEMO =====")
    main()
    print("===== DEMO COMPLETED =====") 