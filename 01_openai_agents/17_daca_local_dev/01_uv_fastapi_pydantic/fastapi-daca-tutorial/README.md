# Pydantic Data Validation Examples

This project demonstrates the use of Pydantic for data validation with nested models and custom validators.

## Features

- Nested model validation (User with multiple Addresses)
- Email validation using EmailStr
- Custom validators (e.g., name length validation)
- Error handling with ValidationError

## Setup

1. Install the required packages:
```bash
pip install pydantic email-validator
```

## Usage

The project includes examples of:
- Creating nested Pydantic models
- Validating data with custom rules
- Handling validation errors
- Using model_dump() instead of the deprecated dict() method

### Example Code

```python
from pydantic import BaseModel, EmailStr, validator, ValidationError
from typing import List

class Address(BaseModel):
    street: str
    city: str
    zip_code: str

class UserWithAddress(BaseModel):
    id: int
    name: str
    email: EmailStr
    addresses: List[Address]
    
    @validator("name")
    def name_must_be_at_least_two_chars(cls, v):
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters long")
        return v
```

## Important Notes

- Use `model_dump()` instead of the deprecated `dict()` method
- Import `ValidationError` from pydantic for error handling
- The `email-validator` package is required for email validation
