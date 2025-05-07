from django import template
from finance.models import Transaction, Earnings

register = template.Library()

@register.simple_tag
def sum_amount(expenses):
    spents = [expense for expense in expenses if isinstance(expense, Transaction)]
    earnings = [expense for expense in expenses if isinstance(expense, Earnings)]

    total = sum(expense.amount.to_decimal() for expense in earnings) - sum(expense.amount.to_decimal() for expense in spents)
    return total

@register.filter
def is_transaction(expense):
    return isinstance(expense, Transaction)