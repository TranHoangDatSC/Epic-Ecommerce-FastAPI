"""
API Response Models - Standardized response format for all API endpoints
"""

from pydantic import BaseModel
from typing import Any, Optional, List, Generic, TypeVar

T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    """Standard API response format"""
    success: bool
    message: str
    data: Optional[T] = None
    errors: Optional[List[str]] = None
    
    class Config:
        arbitrary_types_allowed = True


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response format"""
    items: List[T]
    total: int
    skip: int
    limit: int
    
    class Config:
        arbitrary_types_allowed = True


class ErrorDetail(BaseModel):
    """Error detail format"""
    code: str
    message: str
    field: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response format"""
    success: bool = False
    message: str
    errors: List[ErrorDetail] = []


# Example usage in routes:
#
# @router.get("/items", response_model=APIResponse[List[ItemResponse]])
# async def get_items():
#     items = crud.get_all_items()
#     return APIResponse(
#         success=True,
#         message="Items retrieved successfully",
#         data=items
#     )
#
# @router.get("/items/paginated")
# async def get_items_paginated(skip: int = 0, limit: int = 100):
#     items = crud.get_all_items(skip=skip, limit=limit)
#     total = crud.count_items()
#     return PaginatedResponse(
#         items=items,
#         total=total,
#         skip=skip,
#         limit=limit
#     )
