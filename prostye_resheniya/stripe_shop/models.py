from django.db import models


class Item(models.Model):
    name = models.CharField(
        max_length=200,
        null=False
    )
    description = models.TextField(
        null=True
    )
    price = models.BigIntegerField(null=False)
    currency = models.CharField(max_length=3)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gt=0),
                name='check_price_positive'
            )
        ]


class Tax(models.Model):
    percentage = models.DecimalField(max_digits=7, decimal_places=4, null=False)
    display_name = models.TextField(null=False)
    inclusive = models.BooleanField(null=False)
    country = models.CharField(blank=True, null=True, max_length=2)
    state = models.CharField(blank=True, null=True, max_length=2)
    jurisdiction = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    stripe_id = models.TextField(blank=True, null=True, unique=True)
    currency = models.CharField(null=False, max_length=3, db_index=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(percentage__gt=0, percentage__lt=100),
                name='tax_check_percentage_between_0_and_100'
            )
        ]


class Discount(models.Model):
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=False)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(percentage__gt=0, percentage__lt=100),
                name='discount_check_percentage_between_0_and_10000'
            )
        ]


class OrderItem(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE, primary_key=True)
    quantity = models.IntegerField(null=False)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gt=0),
                name="order_item_check_at_least_one_ordered"
            )
        ]


class Order(models.Model):
    order_items = models.ManyToManyField(OrderItem)
    taxes = models.ManyToManyField(Tax)
    discounts = models.ManyToManyField(Discount)
