import json
import logging
from collections import deque
from dataclasses import dataclass, field
from typing import List, Any, Dict, Type

# Set up logging
logging.basicConfig(level=logging.WARNING)

@dataclass
class JsonMapper:
    def map_json(self, json_data: Dict[str, Any]) -> None:
        # Use a queue to avoid recursion
        queue = deque([(json_data, self)])

        while queue:
            current_json, current_instance = queue.popleft()

            for key, value in current_json.items():
                if hasattr(current_instance, key):
                    attr = getattr(current_instance, key)

                    # If attribute is a dataclass (instance)
                    if isinstance(attr, JsonMapper):
                        queue.append((value, attr))  # Append to queue for further mapping
                    elif isinstance(attr, list) and attr and hasattr(attr[0], '__dataclass__'):
                        # If the attribute is a list of dataclasses
                        nested_class = attr[0].__class__  # Get type of the first element in the list
                        mapped_objects = [nested_class() for _ in value]  # Create instances for each item
                        setattr(current_instance, key, mapped_objects)
                        for item, mapped_object in zip(value, mapped_objects):
                            queue.append((item, mapped_object))
                    else:
                        setattr(current_instance, key, value)
                else:
                    logging.warning(f"Warning: '{key}' does not exist in {current_instance.__class__.__name__}")

@dataclass
class Hobby(JsonMapper):
    name: str

@dataclass
class Address(JsonMapper):
    street: str
    city: str

@dataclass
class Person(JsonMapper):
    name: str
    age: int
    address: Address
    hobbies: List[Hobby] = field(default_factory=list)


def test_gpt():

    # Sample JSON data
    json_string = '''{
        "name": "John Doe",
        "age": 30,
        "address": {
            "street": "123 Main St",
            "city": "Anytown"
        },
        "hobbies": [
            { "name": "reading" },
            { "name": "traveling" }
        ]
    }'''

    json_data = json.loads(json_string)

    # Create a Person instance and map the JSON data
    person_instance = Person(name="", age=0, address=Address("", ""), hobbies=[])

    # Map the JSON to the Person instance
    person_instance.map_json(json_data)

    # Output instance for verification
    print(person_instance)
