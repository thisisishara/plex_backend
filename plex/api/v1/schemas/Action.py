# from datetime import datetime
# from typing import Any
#
# from pydantic import BaseModel
# from pydantic import Field
#
#
# class PLStatement(TypedDict):
#     file_name: str
#     content: str
#     timestamp: datetime
#
#
# class Result(BaseModel):
#     file_name: str = Field(
#         ...,
#         description="Name of the financial statement report",
#         examples=["apple_financial_statement.pdf"],
#     )
#     file_size: float = Field(
#         ...,
#         description="The permissions associated with the API token, detailing the specific access levels granted.",
#     )
#
#     class Config:
#         extra = "ignore"
#         frozen = True
