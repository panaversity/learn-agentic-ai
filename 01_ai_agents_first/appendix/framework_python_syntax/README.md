# Python Dataclasses Examples

This repository contains practical examples of how to use Python's `dataclasses` module effectively. Each example demonstrates different aspects of dataclasses with good practices and common pitfalls to avoid.

## Overview

Dataclasses, introduced in Python 3.7 (PEP 557), provide a way to create classes that are primarily used to store data. They automatically generate special methods like `__init__()`, `__repr__()`, and `__eq__()` based on the class attributes, reducing boilerplate code and making your code more readable and maintainable.

## Example Files

1. **[01_basic_dataclasses.py](01_basic_dataclasses.py)**: Basic usage of dataclasses
   - Simple dataclass definition
   - Type hints
   - Default values
   - Using `field()` for mutable defaults
   - Comparing with traditional classes

2. **[02_nested_dataclasses.py](02_nested_dataclasses.py)**: Working with nested dataclasses
   - Proper nesting structure
   - Serialization to JSON
   - Common pitfalls with flat structures
   - Problems with dictionary-based approaches

3. **[03_inheritance_dataclasses.py](03_inheritance_dataclasses.py)**: Inheritance with dataclasses
   - Proper inheritance patterns
   - Avoiding type conflicts in inherited fields
   - Issues with default values in inheritance
   - Mixing regular classes with dataclasses

4. **[04_immutable_dataclasses.py](04_immutable_dataclasses.py)**: Immutable dataclasses with frozen=True
   - Creating immutable objects
   - Factory methods for creating new instances
   - Pitfalls with mutable objects in immutable dataclasses
   - Initialization tricks with `__post_init__`

5. **[05_large_data_dataclasses.py](05_large_data_dataclasses.py)**: Dataclasses with large datasets
   - Efficient dataclass design
   - Using slots for memory optimization
   - Lazy loading patterns
   - Performance considerations
   - When not to use dataclasses

6. **[06_dataclass_utilities.py](06_dataclass_utilities.py)**: Utility functions for dataclasses
   - Using `asdict()` and `astuple()`
   - The `replace()` function
   - Checking if an object is a dataclass with `is_dataclass()`
   - Introspecting dataclasses with `fields()`

7. **[07_dataclass_with_pydantic.py](07_dataclass_with_pydantic.py)**: Dataclasses with Pydantic for validation
   - Pydantic dataclasses
   - Advanced validation patterns
   - Mixing standard dataclasses with Pydantic
   - Data transformation and serialization

## Best Practices

### When to Use Dataclasses

✅ **Good Use Cases**:
- Data containers with little or no behavior
- Value objects and DTOs (Data Transfer Objects)
- Configuration settings
- API request/response models
- Immutable data structures (with `frozen=True`)

❌ **Avoid Using For**:
- Classes with complex behavior and little data
- Very large datasets where memory usage is critical (unless using `__slots__`)
- When needing complete control over object creation process

### Dataclass Design Guidelines

1. **Use Type Annotations**
   - Make your code more readable and enable static type checking
   - Helps with IDE autocompletion and documentation

2. **Handle Mutable Defaults Properly**
   - Always use `field(default_factory=list)` for mutable defaults
   - Avoid using empty lists or dicts as default values

3. **Consider Immutability**
   - Use `frozen=True` for immutable data
   - Be aware of mutable objects inside frozen dataclasses

4. **Structure Properly**
   - Prefer nested dataclasses over flat structures for complex data
   - Don't go overboard with nesting (3-4 levels max)

5. **Use Helper Functions**
   - `asdict()` and `astuple()` for serialization
   - `replace()` for creating modified copies
   - `fields()` for introspection

6. **Add Validation When Needed**
   - Use `__post_init__` for simple validation
   - Consider Pydantic for complex validation requirements

## Performance Considerations

- Standard dataclasses have minimal overhead
- For very large numbers of instances, consider using `__slots__`
- For extremely performance-critical code, benchmark dataclasses vs. regular classes or named tuples

## Further Reading

- [Python Documentation: dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [PEP 557 -- Data Classes](https://www.python.org/dev/peps/pep-0557/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## Running the Examples

Each file can be run directly to see the examples in action:

```bash
python 01_basic_dataclasses.py
python 02_nested_dataclasses.py
# ... and so on
```

## Requirements

- Python 3.7 or newer
- Pydantic (for the Pydantic examples): `pip install pydantic` 