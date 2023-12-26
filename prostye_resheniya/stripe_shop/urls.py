from django.urls import path

from . import views


urlpatterns = [
    path('', views.get_all_items, name='get_all_items'),
    path("item/<int:item_id>", views.get_item, name="get_item"),
    path("buy/<int:item_id>", views.buy_item, name="buy_item"),
    path("buy/<int:item_id>/success", views.buy_item_success, name="buy_item_success"),
    path('currency-carts', views.currency_carts, name="currency_carts"),
    path("cart/<str:currency>", views.cart, name='cart'),
    path("item/<int:item_id>/add-to-cart", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:item_id>", views.remove_one_such_item_from_cart, name='remove_one_such_item_from_cart'),
    path("cart/remove/<int:item_id>/all", views.remove_all_such_items_from_cart, name='remove_all_such_items_from_cart'),
    path("cart/add/<int:item_id>", views.add_another_such_item_to_cart, name='add_another_such_item_to_cart'),
    path("cart/<str:currency>/checkout", views.cart_checkout, name='cart_checkout'),
    path("cart/<str:currency>/buy", views.buy_cart, name="buy_cart"),
    path("cart/<str:currency>/buy/success", views.buy_cart_success, name="buy_cart_success")
]
