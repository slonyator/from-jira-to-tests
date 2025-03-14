import os
import instructor
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field, AfterValidator
from typing import Annotated

load_dotenv()

client = instructor.from_openai(OpenAI(api_key=os.environ["OPENAI_API_KEY"]))


class Validation(BaseModel):
    is_valid: bool = Field(
        ..., description="Whether the value is valid based on the rules"
    )
    error_message: str | None = Field(
        None, description="The error message if the value is not valid"
    )


ambiguity_statement = "Ensure the user story is clear, precise, and unambiguous, with no room for multiple interpretations."
completeness_statement = (
    "Ensure the user story is complete with a user role, goal, and benefit."
)
contradiction_statement = (
    "Ensure the user story has no contradictions in its requirements."
)


def ambiguity_validator(v):
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a validator. Determine if the value is valid for the statement. If it is not, explain why.",
            },
            {
                "role": "user",
                "content": f"Does `{v}` follow the rules: {ambiguity_statement}",
            },
        ],
        response_model=Validation,
    )
    if not resp.is_valid:
        raise ValueError(
            f"Ambiguity issue: {resp.error_message or 'No specific error message provided.'}"
        )
    return v


def completeness_validator(v):
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a validator. Determine if the value is valid for the statement. If it is not, explain why.",
            },
            {
                "role": "user",
                "content": f"Does `{v}` follow the rules: {completeness_statement}",
            },
        ],
        response_model=Validation,
    )
    if not resp.is_valid:
        raise ValueError(
            f"Completeness issue: {resp.error_message or 'No specific error message provided.'}"
        )
    return v


def contradiction_validator(v):
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a validator. Determine if the value is valid for the statement. If it is not, explain why.",
            },
            {
                "role": "user",
                "content": f"Does `{v}` follow the rules: {contradiction_statement}",
            },
        ],
        response_model=Validation,
    )
    if not resp.is_valid:
        raise ValueError(
            f"Contradiction issue: {resp.error_message or 'No specific error message provided.'}"
        )
    return v


class UserStory(BaseModel):
    story: Annotated[
        str,
        AfterValidator(ambiguity_validator),
        AfterValidator(completeness_validator),
        AfterValidator(contradiction_validator),
    ]


if __name__ == "__main__":
    input_story = "As a bank customer, I want to withdraw cash from an ATM using my debit card so that I can access my money without visiting a branch."
    try:
        validated_story = UserStory(story=input_story)
        print("User story is valid.")
    except ValueError as e:
        print("User story is invalid:", e)
