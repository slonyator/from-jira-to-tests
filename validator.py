import instructor
from instructor import llm_validator
from openai import OpenAI
from pydantic import BaseModel, ValidationError
from typing import Annotated
from pydantic.functional_validators import AfterValidator

client = instructor.from_openai(OpenAI())

class UserStory(BaseModel):
    story: Annotated[
        str,
        AfterValidator(
            llm_validator(
                client=client,
                "Ensure the user story is complete with user role, goal, and benefit; has no contradictions; is clear, precise, and unambiguous."
            )
        ),
    ]

if __name__ == "__main__":
    test_stories = [
        "As a bank customer, I want to withdraw cash from an ATM using my debit card so that I can access my money without visiting a branch.",
    ]

    for i, story in enumerate(test_stories):
        print(f"Testing story {i+1}:")
        try:
            validated_story = UserStory(story=story)
            print("  - Valid")
        except ValidationError as e:
            print("  - Invalid")
            for error in e.errors():
                print(f"    - {error['msg']}")
        print()