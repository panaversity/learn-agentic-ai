# 📘 Shallow Copy vs Deep Copy in Python (with dataclasses)

When you copy an object in Python, you might think you’re making a completely separate version — but **there are two kinds of copying**:

---

## 1️⃣ What is a Shallow Copy?
- Creates a **new outer object**.
- **Does NOT** fully copy nested mutable objects (like lists or dicts).
- **Nested objects are shared** between the original and the copy.

### Example:
```python
import copy

list1 = [[1, 2], [3, 4]]
shallow_copy = copy.copy(list1)  # Shallow copy

shallow_copy[0].append(99)

print("Original:", list1)   # Both changed!
print("Copy:    ", shallow_copy)
````

📌 **Why?** Both lists share the same inner lists.

---

## 2️⃣ What is a Deep Copy?

* Creates a **new outer object**.
* **Recursively copies** all nested mutable objects.
* No shared references — completely independent.

### Example:

```python
deep_copy = copy.deepcopy(list1)
deep_copy[0].append(100)

print("Original:", list1)   # Unchanged
print("Copy:    ", deep_copy)
```

---

## 3️⃣ Shallow vs Deep Copy — Summary Table

| Feature               | Shallow Copy | Deep Copy |
| --------------------- | ------------ | --------- |
| Copies outer object   | ✅            | ✅         |
| Copies nested objects | ❌ (shared)   | ✅         |
| Memory use            | Low          | Higher    |
| Independence          | Partial      | Full      |

---

## 4️⃣ Shallow Copy with `dataclasses.replace`

```python
from dataclasses import dataclass, field, replace
from typing import List

@dataclass
class Agent:
    name: str
    instructions: str
    tools: List[str] = field(default_factory=list)

agent1 = Agent(name="Original", instructions="Follow the plan", tools=["Hammer", "Wrench"])
agent2 = replace(agent1, name="Cloned")  # Shallow copy

print(agent1.tools is agent2.tools)  # True → same list object
```

Changing `agent2.tools` also changes `agent1.tools`:

```python
agent2.tools.append("Screwdriver")
print("Agent1 tools:", agent1.tools)  # Uh-oh, also changed!
```

---

## 5️⃣ Avoiding Shared Lists in Shallow Copy

You can pass a **copied list** to avoid shared references:

```python
agent3 = replace(agent1, name="Safe Clone", tools=agent1.tools.copy())
agent3.tools.append("Pliers")

print("Agent1 tools:", agent1.tools)  # unchanged
print("Agent3 tools:", agent3.tools)
```

📌 This creates an independent list container, but mutable items **inside** are still shared.

---

## 6️⃣ Deep Copy for Complete Independence

Use `copy.deepcopy()` to break **all links**:

```python
import copy

agent4 = copy.deepcopy(agent1)
agent4.tools.append("Drill")

print("Agent1 tools:", agent1.tools)  # unchanged
print("Agent4 tools:", agent4.tools)
```

---

## 7️⃣ Adding a `clone()` Method

We can make copying easier by adding a `clone()` method:

```python
@dataclass
class Agent:
    name: str
    instructions: str
    tools: List[str] = field(default_factory=list)

    def clone(self, **changes):
        return replace(self, **changes)

# Example usage
a = Agent("A", "Test", ["tool1"])
b = a.clone(name="B", tools=a.tools.copy())

print(a.tools is b.tools)  # False → different lists
```

---

## 8️⃣ Key Takeaways

* **Shallow copy** → Quick, memory-efficient, but shares nested data.
* **Deep copy** → Fully independent, but uses more memory.
* With `dataclasses.replace`, mutable fields are **shallow copied**.
* Avoid bugs by:

  * Copying lists/dicts manually (`.copy()`)
  * Or using `copy.deepcopy()` when full independence is needed.

