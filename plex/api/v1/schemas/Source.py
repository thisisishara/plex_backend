from pydantic import BaseModel
from pydantic import Field


class Source(BaseModel):
    file_name: str = Field(
        ...,
        description="Name of the financial statement report",
        examples=["apple_financial_statement.pdf"],
    )
    file_size: float = Field(
        ...,
        description="Size of the uploaded file",
    )
    content: str = Field(
        ...,
        description="Name of the financial statement report",
        examples=["apple_financial_statement.pdf"],
    )

    class Config:
        extra = "ignore"
        frozen = True
