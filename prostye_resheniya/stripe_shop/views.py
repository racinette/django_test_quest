import os

import urllib.parse
from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.urls import reverse
from .cart import Cart
from .etc.stripe_api import get_stripe_client_api_key, get_stripe_server_api_key
import stripe

from .models import Item, Order, OrderItem, Tax, Discount


def get_all_items(request: HttpRequest) -> HttpResponse:
    items = Item.objects.all()
    return render(
        request,
        'stripe_shop/itemlist.html',
        {"items": items}
    )


def get_item(request: HttpRequest, item_id: int) -> HttpResponse:
    item = get_object_or_404(Item, pk=item_id)
    formatted_price = '{:.2f}'.format(item.price / 100)
    return render(
        request,
        "stripe_shop/item.html",
        {
            "item": item,
            "formatted_price": formatted_price,
            "include_stripe": True,
            "STRIPE_CLIENT_API_KEY": get_stripe_client_api_key(item.currency),
        }
    )


def buy_item_success(request: HttpRequest, item_id: int) -> HttpResponse:
    return render(request, "stripe_shop/buy_item_success.html")


def buy_item(_request: HttpRequest, item_id: int) -> HttpResponse:
    item = get_object_or_404(Item, pk=item_id)

    success_url = urllib.parse.urljoin(os.environ['SELF_ADDRESS'], reverse('buy_item_success', args=(item_id, )))
    checkout = stripe.checkout.Session.create(
        api_key=get_stripe_server_api_key(item.currency),
        mode='payment',
        line_items=[
            {
                "price_data": {
                    "currency": item.currency.lower(),
                    "unit_amount": item.price,
                    "product_data": {
                        "description": item.description,
                        "name": item.name
                    },
                },
                "quantity": 1
            }
        ],
        success_url=success_url,
    )

    return JsonResponse({
        "checkout_session_id": checkout.id
    })


def add_to_cart(request: HttpRequest, item_id: int) -> HttpResponse:
    if not Item.objects.filter(pk=item_id).exists():
        return HttpResponseNotFound()

    Cart(request).add_to_cart(item_id)
    return redirect('get_item', item_id=item_id)


def currency_carts(request: HttpRequest) -> HttpResponse:
    carts = Cart(request).get_currency_carts()
    if len(carts) == 1:
        return redirect('cart', currency=carts[0].currency)

    return render(
        request,
        "stripe_shop/currency_carts.html",
        {"currency_carts": carts}
    )


def cart(request: HttpRequest, currency: str) -> HttpResponse:
    return render(
        request,
        'stripe_shop/cart.html',
        {
            "cart_items": Cart(request).get_items(currency),
            "currency": currency,
            "include_stripe": True,
            "STRIPE_CLIENT_API_KEY": get_stripe_client_api_key(currency),
        },
    )


def add_another_such_item_to_cart(request: HttpRequest, item_id: int):
    currency = Cart(request).add_to_cart(item_id)
    return redirect('cart', currency=currency)


def remove_one_such_item_from_cart(request: HttpRequest, item_id: int):
    currency = Cart(request).remove_from_cart(item_id)
    return redirect('cart', currency=currency)


def remove_all_such_items_from_cart(request: HttpRequest, item_id: int):
    currency = Cart(request).remove_all_from_cart(item_id)
    return redirect('cart', currency=currency)


def buy_cart(request: HttpRequest, currency: str) -> HttpResponse:
    cart_items = Cart(request).get_items(currency)
    if not cart_items:
        return JsonResponse({})

    tax = Tax.objects.filter(currency=currency).first()
    if tax and not tax.stripe_id:
        kwargs = dict(
            display_name=tax.display_name,
            inclusive=tax.inclusive,
            percentage=tax.percentage,
            country=(tax.country or None),
            state=(tax.state or None),
            jurisdiction=(tax.jurisdiction or None),
            description=(tax.description or None)
        )
        stripe_tax = stripe.TaxRate.create(
            api_key=get_stripe_server_api_key(currency),
            **kwargs
        )
        # сохраняем в базу ID налога, чтобы переиспользовать
        tax.stripe_id = stripe_tax.id
        tax.save()
        tax_rates = [stripe_tax.id]
    elif not tax:
        tax_rates = None
    else:
        tax_rates = [tax.stripe_id]

    discount = Discount.objects.first()
    if discount:
        coupon = stripe.Coupon.create(
            api_key=get_stripe_server_api_key(currency),
            percent_off=discount.percentage,
            duration='once'
        )
        discounts = [{"coupon": coupon.id}]
    else:
        discounts = None

    # создаем заказ
    with transaction.atomic():
        order = Order()
        order.save()

        for item in cart_items:
            order_item = OrderItem(item=item.item, quantity=item.count)
            order_item.save()
            order.order_items.add(order_item)

        # возьмем первый попавшийся налог и скидку для теста
        if tax:
            order.taxes.add(tax)

        if discount:
            order.discounts.add(discount)

        order.save()

    success_url = urllib.parse.urljoin(os.environ['SELF_ADDRESS'], reverse('buy_cart_success', args=(currency, )))
    checkout = stripe.checkout.Session.create(
        api_key=get_stripe_server_api_key(currency),
        mode='payment',
        line_items=[
            {
                "price_data": {
                    "currency": item.item.currency.lower(),
                    "unit_amount": item.item.price,
                    "product_data": {
                        "description": item.item.description,
                        "name": item.item.name
                    },
                },
                "quantity": item.count,
                "tax_rates": tax_rates
            }
            for item in cart_items
        ],
        discounts=discounts,
        success_url=success_url,
    )

    return JsonResponse({"checkout_session_id": checkout.id})


def cart_checkout(request: HttpRequest, currency: str) -> HttpResponse:
    currency = currency.lower()

    items = Cart(request).get_items(currency)

    if not items:
        return HttpResponseBadRequest()

    checkout_sum = sum([
        item.full_price
        for item in items
    ])

    payment_intent = stripe.PaymentIntent.create(
        api_key=get_stripe_server_api_key(currency),
        currency=currency,
        amount=checkout_sum,
        setup_future_usage="on_session"
    )

    return render(
        request,
        'stripe_shop/cart_checkout.html',
        {
            "include_stripe": True,
            "STRIPE_CLIENT_API_KEY": get_stripe_client_api_key(currency),
            "STRIPE_PAYMENT_CLIENT_SECRET": payment_intent.client_secret,
            "currency": currency
        }
    )


def buy_cart_success(request: HttpRequest, currency: str) -> HttpResponse:
    return render(request, "stripe_shop/buy_cart_success.html")
