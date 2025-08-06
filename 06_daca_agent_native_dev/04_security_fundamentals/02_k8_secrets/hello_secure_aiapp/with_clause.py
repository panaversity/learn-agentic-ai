from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    email: str
    
    def __enter__(self):
        print("Entering context")
        return self
    
    def do_something(self):
        print("Doing something")
        # raise Exception("Something went wrong")
    def __exit__(self, exc_type, exc_value, traceback):
        print("Exiting context")
        print(f"Exception type: {exc_type}")
        print(f"Exception value: {exc_value}")
        print(f"Traceback: {traceback}")

# Create an instance
junaid = User(id=1, name="Junaid", email="junaid@example.com")

# Use in a with statement
with junaid as user:
    user.do_something()