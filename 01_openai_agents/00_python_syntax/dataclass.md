When you use `@dataclass`, Python **automatically generates** several special methods for your class. These include:

### **Methods Automatically Created by `@dataclass`**
| **Method**       | **Purpose** |
|------------------|------------|
| `__init__`       | Creates an **initializer (constructor)** that assigns values to attributes. |
| `__repr__`       | Generates a **string representation** of the object for debugging (`print(obj)`). |
| `__eq__`         | Adds **equality comparison** (`==` operator) between instances. |
| `__ne__`         | Adds **inequality comparison** (`!=` operator) automatically. |
| `__lt__`, `__le__`, `__gt__`, `__ge__` | If `order=True`, these enable **sorting** by comparing attributes. |
| `__hash__`       | If `frozen=True`, makes the object **hashable** (usable as dictionary keys). |
| `__post_init__`  | Allows custom **post-processing logic** after initialization. |

---

## **1. Example: Default `@dataclass` Methods**
Let's create a simple dataclass:

```python
from dataclasses import dataclass

@dataclass
class Person:
    name: str
    age: int = 25  # Default value for age

p1 = Person("Alice")
p2 = Person("Bob", 30)

print(p1)            # Calls __repr__()
print(p1 == p2)      # Calls __eq__()
```

### **Generated Methods Behind the Scenes**
Equivalent to:
```python
class Person:
    def __init__(self, name: str, age: int = 25):  # ✅ Default values applied here
        self.name = name
        self.age = age

    def __repr__(self):  # ✅ For debugging and printing objects
        return f"Person(name={self.name!r}, age={self.age!r})"

    def __eq__(self, other):  # ✅ Checks if two objects are equal
        if not isinstance(other, Person):
            return NotImplemented
        return (self.name, self.age) == (other.name, other.age)
```

---

## **2. Using `@dataclass(order=True)`**
If we add `order=True`, **comparison methods** are generated.

```python
@dataclass(order=True)
class Employee:
    id: int
    name: str

e1 = Employee(1, "Alice")
e2 = Employee(2, "Bob")

print(e1 < e2)  # ✅ Calls __lt__()
print(e1 > e2)  # ✅ Calls __gt__()
```

Generated methods:
```python
def __lt__(self, other):
    return (self.id, self.name) < (other.id, other.name)

def __le__(self, other):
    return (self.id, self.name) <= (other.id, other.name)

def __gt__(self, other):
    return (self.id, self.name) > (other.id, other.name)

def __ge__(self, other):
    return (self.id, self.name) >= (other.id, other.name)
```

---

## **3. Using `@dataclass(frozen=True)`**
If `frozen=True`, it makes the class **immutable** (like a tuple).

```python
@dataclass(frozen=True)
class Point:
    x: int
    y: int

p = Point(1, 2)
p.x = 10  # ❌ Raises an error: dataclass is frozen!
```

Generated:
```python
def __hash__(self):
    return hash((self.x, self.y))
```
- **Hashing is enabled** because frozen dataclasses are **immutable**.

---

## **4. Custom Initialization with `__post_init__`**
You can **modify fields after object creation**.

```python
from dataclasses import field

@dataclass
class Product:
    name: str
    price: float
    discount: float = field(default=0.0)

    def __post_init__(self):
        self.price = max(self.price, 0)  # Ensures price is never negative

p = Product("Laptop", -1000)  # ❌ Wrong price
print(p.price)  # ✅ Fixed to 0
```

---

## **Summary**
| **Feature**        | **Generated Methods** |
|--------------------|----------------------|
| Default `@dataclass` | `__init__`, `__repr__`, `__eq__` |
| `order=True`       | `__lt__`, `__le__`, `__gt__`, `__ge__` |
| `frozen=True`      | `__hash__` (makes it immutable) |
| Custom Init        | `__post_init__` |

🚀 **Now you understand how `@dataclass` works behind the scenes!** 🚀