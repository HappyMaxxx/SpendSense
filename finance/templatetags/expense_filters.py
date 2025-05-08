from django import template
from finance.models import Spents, Earnings

register = template.Library()

@register.simple_tag
def sum_amount(expenses):
    earnings = [expense for expense in expenses if isinstance(expense, Earnings)]
    spents = [expense for expense in expenses if  isinstance(expense, Spents)]

    total = sum(expense.amount.to_decimal() for expense in earnings) - sum(expense.amount.to_decimal() for expense in spents)
    return total

@register.filter
def is_spent(expense):
    return isinstance(expense, Spents)