"""
07_dataclass_with_pydantic.py - Using dataclasses with Pydantic for validation

This file demonstrates how to use dataclasses with Pydantic for robust data validation and serialization.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.dataclasses import dataclass as pydantic_dataclass
from pydantic import EmailStr, HttpUrl, PositiveInt, AnyUrl, SecretStr, constr
from datetime import datetime, date
import json
from enum import Enum, auto


# EXAMPLE 1: Simple Pydantic dataclass with validation
@pydantic_dataclass
class User:
    """User data with validation via Pydantic."""
    username: str
    email: EmailStr  # Email validation
    age: PositiveInt  # Must be positive
    website: Optional[HttpUrl] = None  # URL validation if provided
    tags: List[str] = field(default_factory=list)
    
    # You can add methods as with regular dataclasses
    def is_adult(self) -> bool:
        """Check if the user is an adult."""
        return self.age >= 18


def demo_pydantic_dataclass():
    print("=== PYDANTIC DATACLASS EXAMPLE ===")
    
    # Valid data example
    try:
        user = User(
            username="johndoe",
            email="john.doe@example.com",
            age=25,
            website="https://johndoe.com",
            tags=["developer", "python"]
        )
        print(f"Valid user: {user}")
        print(f"Is adult: {user.is_adult()}")
    except Exception as e:
        print(f"Error creating user: {e}")
    
    # Invalid data examples
    print("\nValidation Examples:")
    
    try:
        # Invalid email
        user = User(username="test", email="not-an-email", age=30)
        print(f"User with invalid email: {user}")
    except Exception as e:
        print(f"Invalid email error: {e}")
    
    try:
        # Invalid age (negative)
        user = User(username="test", email="test@example.com", age=-5)
        print(f"User with invalid age: {user}")
    except Exception as e:
        print(f"Invalid age error: {e}")
    
    try:
        # Invalid URL
        user = User(
            username="test",
            email="test@example.com",
            age=30,
            website="not-a-url"
        )
        print(f"User with invalid URL: {user}")
    except Exception as e:
        print(f"Invalid URL error: {e}")


# EXAMPLE 2: Advanced Pydantic model with complex validation
class UserRole(Enum):
    """Enum for user roles."""
    ADMIN = auto()
    EDITOR = auto()
    VIEWER = auto()


class Address(BaseModel):
    """Address model with validation."""
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"
    
    @field_validator('zip_code')
    def validate_zip_code(cls, v):
        """Validate zip code format."""
        if not v.isdigit() or len(v) != 5:
            raise ValueError("ZIP code must be 5 digits")
        return v


class Profile(BaseModel):
    """User profile with validation rules."""
    full_name: str
    bio: Optional[str] = None
    birth_date: date
    profile_image: Optional[HttpUrl] = None
    
    @field_validator('birth_date')
    def validate_birth_date(cls, v):
        """Validate birth date is not in the future."""
        if v > date.today():
            raise ValueError("Birth date cannot be in the future")
        return v


class UserModel(BaseModel):
    """Advanced user model with complex validation."""
    id: str
    username: constr(min_length=3, max_length=50)  # Constrained string
    email: EmailStr
    password: SecretStr  # Sensitive data, won't be exposed in repr
    role: UserRole
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    profile: Profile
    addresses: List[Address] = Field(default_factory=list)
    settings: Dict[str, Any] = Field(default_factory=dict)
    
    @model_validator(mode='after')
    def validate_model(self):
        """Cross-field validation."""
        # Example: Admin users must have an active account
        if self.role == UserRole.ADMIN and not self.is_active:
            raise ValueError("Admin users must have an active account")
        
        return self
    
    @field_validator('username')
    def username_alphanumeric(cls, v):
        """Ensure username contains only alphanumeric chars and underscore."""
        if not all(c.isalnum() or c == '_' for c in v):
            raise ValueError("Username must contain only alphanumeric characters and underscores")
        return v
    
    def to_json(self) -> str:
        """Convert user to JSON string."""
        # Pydantic's model_dump takes care of converting to dict, including enums and complex types
        return json.dumps(self.model_dump(exclude={"password"}), default=str, indent=2)


def demo_pydantic_model():
    print("\n=== ADVANCED PYDANTIC MODEL EXAMPLE ===")
    
    # Valid user example
    try:
        user = UserModel(
            id="user123",
            username="johndoe",
            email="john@example.com",
            password="securepassword",
            role=UserRole.EDITOR,
            profile=Profile(
                full_name="John Doe",
                bio="Python developer",
                birth_date=date(1990, 1, 15),
                profile_image="https://example.com/profiles/johndoe.jpg"
            ),
            addresses=[
                Address(
                    street="123 Main St",
                    city="Springfield",
                    state="IL",
                    zip_code="62701"
                )
            ],
            settings={"theme": "dark", "notifications": True}
        )
        
        print("Created valid user:")
        print(user.to_json())
        
        # Accessing fields (password is obscured for security)
        print(f"\nUsername: {user.username}")
        print(f"Role: {user.role}")
        print(f"Password (securely stored): {user.password}")
        
    except Exception as e:
        print(f"Error creating user: {e}")
    
    # Invalid examples
    print("\nValidation Examples:")
    
    try:
        # Invalid username (special characters)
        user = UserModel(
            id="user456",
            username="john@doe",  # @ character not allowed
            email="john@example.com",
            password="password123",
            role=UserRole.ADMIN,
            profile=Profile(
                full_name="John Doe",
                birth_date=date(1990, 1, 15)
            )
        )
        print("User with invalid username created successfully (shouldn't happen)")
    except Exception as e:
        print(f"Invalid username error: {e}")
    
    try:
        # Invalid: Admin with inactive account
        user = UserModel(
            id="user789",
            username="admin_user",
            email="admin@example.com",
            password="adminpass",
            role=UserRole.ADMIN,
            is_active=False,  # Admin must be active
            profile=Profile(
                full_name="Admin User",
                birth_date=date(1985, 6, 15)
            )
        )
        print("Created inactive admin (shouldn't happen)")
    except Exception as e:
        print(f"Invalid admin status error: {e}")


# EXAMPLE 3: Mixing standard dataclasses with Pydantic validation

# Standard dataclass
@dataclass
class Product:
    """Standard dataclass for a product."""
    id: str
    name: str
    price: float
    in_stock: bool = True
    tags: List[str] = field(default_factory=list)


# Pydantic model that uses the standard dataclass
class Inventory(BaseModel):
    """Inventory with validation that uses standard dataclasses."""
    store_id: str
    products: List[Product]
    last_updated: datetime = Field(default_factory=datetime.now)
    
    # Validating a regular dataclass within Pydantic
    @field_validator('products')
    def validate_products(cls, products):
        """Custom validation for products."""
        if not products:
            raise ValueError("Inventory must have at least one product")
        
        for product in products:
            if product.price < 0:
                raise ValueError(f"Product {product.name} has invalid negative price")
        
        return products
    
    # Converting the inventory to a dictionary
    def to_dict(self) -> Dict[str, Any]:
        """Convert inventory to a dictionary."""
        return {
            "store_id": self.store_id,
            "products": [
                {
                    "id": p.id,
                    "name": p.name,
                    "price": p.price,
                    "in_stock": p.in_stock,
                    "tags": p.tags
                }
                for p in self.products
            ],
            "last_updated": self.last_updated.isoformat()
        }


def demo_mixed_validation():
    print("\n=== MIXING STANDARD DATACLASSES WITH PYDANTIC ===")
    
    # Create some products using standard dataclasses
    products = [
        Product(id="p1", name="Laptop", price=999.99, tags=["electronics", "computers"]),
        Product(id="p2", name="Headphones", price=149.99, tags=["electronics", "audio"]),
        Product(id="p3", name="Mouse", price=29.99)
    ]
    
    # Valid inventory
    try:
        inventory = Inventory(
            store_id="store001",
            products=products
        )
        
        print("Valid inventory created:")
        print(json.dumps(inventory.to_dict(), indent=2))
        
    except Exception as e:
        print(f"Error creating inventory: {e}")
    
    # Invalid inventory (empty products)
    try:
        inventory = Inventory(
            store_id="store002",
            products=[]  # Empty list, should fail validation
        )
        print("Empty inventory created (shouldn't happen)")
    except Exception as e:
        print(f"\nEmpty inventory error: {e}")
    
    # Invalid inventory (negative price)
    try:
        bad_products = [
            Product(id="p1", name="Laptop", price=999.99),
            Product(id="p2", name="Broken Item", price=-10.0)  # Negative price
        ]
        
        inventory = Inventory(
            store_id="store003",
            products=bad_products
        )
        print("Inventory with negative price created (shouldn't happen)")
    except Exception as e:
        print(f"\nNegative price error: {e}")


if __name__ == "__main__":
    demo_pydantic_dataclass()
    demo_pydantic_model()
    demo_mixed_validation() 