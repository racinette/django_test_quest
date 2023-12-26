import os

from django.http import HttpRequest

from ..cart import Cart


def stripe_context_processor(request: HttpRequest) -> dict:
    return {
        "cart_length": len(Cart(request)),
    }
