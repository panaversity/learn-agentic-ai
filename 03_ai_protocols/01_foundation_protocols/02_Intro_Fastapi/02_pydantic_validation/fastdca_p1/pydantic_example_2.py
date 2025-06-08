from pydantic import BaseModel, EmailStr

# Define a nested model


class Address(BaseModel):
    street: str
    city: str
    zip_code: str


class UserWithAddress(BaseModel):
    id: int
    name: str
    email: EmailStr  # Built-in validator for email format
    addresses: list[Address]  # List of nested Address models


# Valid data with nested structure
user_data = {
    "id": 2,
    "name": "Bob",
    "email": "bob@example.com",
    "addresses": [
        {"street": "123 Main St", "city": "New York", "zip_code": "10001"},
        {"street": "456 Oak Ave", "city": "Los Angeles", "zip_code": "90001"},
    ],
}
user = UserWithAddress.model_validate(user_data)
print(user.model_dump())