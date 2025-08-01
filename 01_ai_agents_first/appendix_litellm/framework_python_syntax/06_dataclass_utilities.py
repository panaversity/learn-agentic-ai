"""
06_dataclass_utilities.py - Utility functions and advanced features for dataclasses

This file demonstrates how to use utility functions that come with the dataclasses module.
"""

from dataclasses import dataclass, field, asdict, astuple, replace, is_dataclass, fields
from typing import List, Dict, Any, Optional
from pprint import pprint
import json
import copy


# Sample dataclasses for demonstrating utilities
@dataclass
class Address:
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"


@dataclass
class Person:
    name: str
    age: int
    email: Optional[str] = None
    addresses: List[Address] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


def demo_asdict():
    """Demonstrate converting dataclasses to dictionaries with asdict()."""
    print("\n=== USING asdict() ===")
    
    # Create a person with nested dataclass
    person = Person(
        name="Alice Johnson",
        age=32,
        email="alice@example.com",
        addresses=[
            Address("123 Main St", "Springfield", "IL", "62701"),
            Address("456 Oak Ave", "Chicago", "IL", "60601")
        ],
        metadata={"department": "Engineering", "employee_id": "E12345"}
    )
    
    # Convert to a dictionary
    person_dict = asdict(person)
    
    print("Person dataclass as dictionary:")
    pprint(person_dict)
    
    # The dictionary can be used for serialization
    json_data = json.dumps(person_dict, indent=2)
    print("\nJSON representation:")
    print(json_data)
    
    # You can also reconstruct a dataclass from a dictionary
    # (though this isn't built-in - you'd need to implement it)
    def dict_to_dataclass(data_dict, cls):
        """Convert a dictionary back to a dataclass instance."""
        # Handle nested dataclasses
        kwargs = {}
        
        for field_name, field_value in data_dict.items():
            field_type = None
            
            # Find the field type for this field name
            for f in fields(cls):
                if f.name == field_name:
                    field_type = f.type
                    break
            
            # Handle nested dataclasses or lists of dataclasses
            if field_type and isinstance(field_value, dict) and hasattr(field_type, "__annotations__"):
                # Nested dataclass
                kwargs[field_name] = dict_to_dataclass(field_value, field_type)
            elif field_type and isinstance(field_value, list) and hasattr(field_type, "__origin__") and field_type.__origin__ is list:
                # List of dataclasses
                item_type = field_type.__args__[0]
                if hasattr(item_type, "__annotations__"):
                    kwargs[field_name] = [dict_to_dataclass(item, item_type) for item in field_value]
                else:
                    kwargs[field_name] = field_value
            else:
                kwargs[field_name] = field_value
        
        return cls(**kwargs)
    
    # For simple cases, unpacking works
    new_address = Address(**person_dict["addresses"][0])
    print("\nReconstructed address:")
    print(new_address)


def demo_astuple():
    """Demonstrate converting dataclasses to tuples with astuple()."""
    print("\n=== USING astuple() ===")
    
    address = Address("123 Main St", "Springfield", "IL", "62701")
    address_tuple = astuple(address)
    
    print(f"Address: {address}")
    print(f"As tuple: {address_tuple}")
    
    # You can use tuple unpacking
    street, city, state, zip_code, country = address_tuple
    print(f"Unpacked street: {street}")
    print(f"Unpacked city: {city}")
    
    # Tuples are useful for comparing and hashing
    address1 = Address("123 Main St", "Springfield", "IL", "62701")
    address2 = Address("123 Main St", "Springfield", "IL", "62701")
    
    print(f"Tuples equal? {astuple(address1) == astuple(address2)}")
    print(f"Tuple hash: {hash(astuple(address1))}")


def demo_replace():
    """Demonstrate creating new instances with changes using replace()."""
    print("\n=== USING replace() ===")
    
    original = Person(
        name="Bob Smith",
        age=45,
        email="bob@example.com"
    )
    
    # Create a copy with just the email changed
    updated = replace(original, email="bob.smith@newdomain.com")
    
    print(f"Original: {original}")
    print(f"Updated: {updated}")
    
    # Replace multiple fields
    promoted = replace(original, age=46, metadata={"title": "Senior Developer"})
    print(f"Promoted: {promoted}")
    
    # Creating variations is easy
    variations = [
        replace(original, age=original.age + i)
        for i in range(5)
    ]
    print("\nAge variations:")
    for v in variations:
        print(f"  {v}")
    
    # CAUTION: replace() does a shallow copy, not a deep copy
    address = Address("123 Main St", "Springfield", "IL", "62701")
    person = Person(
        name="Carol Davis",
        age=28,
        addresses=[address]
    )
    
    # Change reference address after creating person
    address.street = "Changed Street"
    
    # The person's address is also changed because it's the same object
    print(f"\nPerson's address after changing original: {person.addresses[0]}")
    
    # To avoid this, use deep copy when needed
    address = Address("123 Main St", "Springfield", "IL", "62701")
    person = Person(
        name="Carol Davis",
        age=28,
        addresses=[copy.deepcopy(address)]
    )
    
    # Now changing the original won't affect the person's copy
    address.street = "Changed Street Again"
    print(f"Original address: {address}")
    print(f"Person's address (deep copy): {person.addresses[0]}")


def demo_is_dataclass():
    """Demonstrate using is_dataclass() to check if an object is a dataclass."""
    print("\n=== USING is_dataclass() ===")
    
    # Define a regular class
    class RegularClass:
        def __init__(self, name):
            self.name = name
    
    # Create instances
    person = Person("Test", 30)
    regular = RegularClass("Test")
    
    # Check which are dataclasses
    print(f"Is Person a dataclass? {is_dataclass(Person)}")
    print(f"Is person instance a dataclass? {is_dataclass(person)}")
    print(f"Is RegularClass a dataclass? {is_dataclass(RegularClass)}")
    print(f"Is regular instance a dataclass? {is_dataclass(regular)}")
    
    # You could use this in a function to handle different types
    def process_object(obj):
        if is_dataclass(obj):
            print(f"Processing dataclass: {asdict(obj)}")
        else:
            print(f"Processing regular object: {vars(obj)}")
    
    process_object(person)
    process_object(regular)


def demo_fields():
    """Demonstrate using fields() to inspect dataclass fields."""
    print("\n=== USING fields() ===")
    
    # Get all fields from a dataclass
    person_fields = fields(Person)
    
    print("Person fields:")
    for f in person_fields:
        print(f"  {f.name}: {f.type} (default: {f.default})")
    
    # You can use this for dynamic operations
    def create_form_fields(cls):
        """Example: create HTML form fields based on dataclass fields."""
        result = []
        for f in fields(cls):
            field_type = "text"
            if f.type is int:
                field_type = "number"
            elif f.type is bool:
                field_type = "checkbox"
            
            result.append(f'<input type="{field_type}" name="{f.name}" placeholder="{f.name}">')
        
        return "\n".join(result)
    
    print("\nGenerated form fields for Address:")
    print(create_form_fields(Address))


if __name__ == "__main__":
    print("=== DATACLASS UTILITY FUNCTIONS ===")
    
    demo_asdict()
    demo_astuple()
    demo_replace()
    demo_is_dataclass()
    demo_fields() 