"""
dataclass_file_output.py - Demonstration of working dataclasses with file output
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict


# A simple dataclass with no inheritance
@dataclass
class Person:
    name: str  # Required field
    age: int   # Required field
    email: Optional[str] = None  # Optional field with default


# A dataclass with more fields and a method
@dataclass
class Student:
    # Required fields first
    name: str
    age: int
    student_id: str
    # Optional fields with defaults
    gpa: float = 0.0
    courses: List[str] = field(default_factory=list)
    
    def add_course(self, course: str) -> None:
        """Add a course to student's list"""
        self.courses.append(course)


def main():
    # Open a file for writing results
    with open('dataclass_output.txt', 'w') as f:
        f.write("===== DATACLASS DEMONSTRATION =====\n\n")
        
        # Create a person
        f.write("1. Creating a Person instance\n")
        person = Person(name="John Smith", age=35, email="john@example.com")
        f.write(f"   Person: {person}\n")
        f.write(f"   Accessing attributes - Name: {person.name}, Age: {person.age}, Email: {person.email}\n\n")
        
        # Create a student
        f.write("2. Creating a Student instance\n")
        student = Student(
            name="Alice Johnson",
            age=20,
            student_id="S12345",
            gpa=3.8
        )
        f.write(f"   Student: {student}\n")
        
        # Add courses
        f.write("\n3. Adding courses to student\n")
        student.add_course("Python Programming")
        student.add_course("Data Structures")
        student.add_course("Algorithms")
        f.write(f"   Student after adding courses: {student}\n")
        f.write(f"   Courses: {student.courses}\n\n")
        
        # Demonstrate replacing a mutable field
        f.write("4. Replacing a mutable field (courses)\n")
        new_courses = ["Advanced Python", "Machine Learning", "AI"]
        student.courses = new_courses
        f.write(f"   Student with replaced courses: {student}\n\n")
        
        # Create a student with initial courses
        f.write("5. Creating a student with initial courses\n")
        student2 = Student(
            name="Bob Williams",
            age=22,
            student_id="S67890",
            courses=["Calculus", "Physics"]
        )
        f.write(f"   Student with initial courses: {student2}\n\n")
        
        f.write("===== DEMONSTRATION COMPLETED =====\n")


# Run the main function
if __name__ == "__main__":
    main()
    print("Demonstration completed. Check dataclass_output.txt for results.") 