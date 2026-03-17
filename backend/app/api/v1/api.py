"""
API v1 Router Collection
This module brings together all v1 endpoints and exposes them as a single router.
"""

from fastapi import APIRouter
from app.api.routes import (
    auth,
    users,
    categories,
    products,
    orders,
    moderator
)

# Create the main API v1 router
api_router = APIRouter(prefix="/api/v1")

# Include all v1 endpoints
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(categories.router)
api_router.include_router(products.router)
api_router.include_router(orders.router)
api_router.include_router(moderator.router)

__all__ = ["api_router"]
