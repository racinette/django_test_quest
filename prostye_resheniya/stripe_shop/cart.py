import dataclasses
from collections import defaultdict

from django.http import HttpRequest
from django.contrib.sessions.backends.db import SessionBase

from .models import Item


@dataclasses.dataclass
class CartItem:
    item: Item
    count: int
    full_price: int
    full_price_pretty: str
    price_pretty: str


@dataclasses.dataclass
class CurrencyCart:
    currency: str
    length: int


class Cart:
    def __init__(self, request: HttpRequest) -> None:
        self.session: SessionBase = request.session

    def _get_cart(self) -> dict[str, list[int]]:
        cart = self.session.get('cart', dict())

        if not isinstance(cart, dict):
            cart = dict()
            self.session['cart'] = cart

        return cart

    def _get(self, currency: str) -> list[int]:
        currency = currency.lower()
        cart = self._get_cart()
        return cart.get(currency, [])

    def _set(self, currency: str, item_ids: list[int]) -> None:
        currency = currency.lower()
        cart = self.session.get('cart', dict())
        if item_ids:
            cart[currency] = item_ids
        else:
            cart.pop(currency, None)
        self.session['cart'] = cart

    def add_to_cart(self, item_id: int) -> str | None:
        try:
            item: Item = Item.objects.get(pk=item_id)
        except Item.DoesNotExist:
            return None
        else:
            currency = item.currency.lower()
            item_ids = self._get(currency)
            item_ids.append(item_id)
            self._set(currency, item_ids)
            return currency

    def remove_from_cart(self, item_id: int) -> str | None:
        try:
            item: Item = Item.objects.get(pk=item_id)
        except Item.DoesNotExist:
            return None
        else:
            currency = item.currency.lower()
            item_ids = self._get(currency)
            item_ids.remove(item_id)
            self._set(currency, item_ids)
            return currency

    def remove_all_from_cart(self, item_id: int) -> str | None:
        try:
            item: Item = Item.objects.get(pk=item_id)
        except Item.DoesNotExist:
            return None
        else:
            currency = item.currency.lower()
            item_ids = self._get(currency)
            item_ids = list(filter(lambda x: x != item_id, item_ids))
            self._set(currency, item_ids)
            return currency

    def get_currency_carts(self) -> list[CurrencyCart]:
        return [
            CurrencyCart(currency=currency, length=len(value))
            for currency, value in self._get_cart().items()
        ]

    def get_items(self, currency: str) -> list[CartItem]:
        currency = currency.lower()

        item_ids = self._get(currency)
        if not item_ids:
            return []

        unique_item_ids = set(item_ids)
        cart_items = Item.objects.filter(pk__in=unique_item_ids).order_by('-pk')

        d = defaultdict(lambda: 0)
        for item_id in item_ids:
            d[item_id] += 1

        full_cart_items = []

        for item in cart_items:
            if item.currency.lower() != currency:
                self.remove_all_from_cart(item.pk)
                continue

            cart_item = CartItem(
                item=item,
                count=(count := d[item.pk]),
                full_price=(full_price := count * item.price),
                full_price_pretty='{:.2f}'.format(full_price / 100),
                price_pretty='{:.2f}'.format(item.price / 100)
            )
            full_cart_items.append(cart_item)

        return full_cart_items

    def length(self, currency: str) -> int:
        return len(self._get_cart().get(currency, []))

    def __len__(self) -> int:
        return sum(
            [
                len(values)
                for values in self._get_cart().values()
            ]
        )

