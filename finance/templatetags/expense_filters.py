from django import template
from finance.models import Spents, Earnings

register = template.Library()

@register.simple_tag
def sum_amount(expenses):
    earnings = [expense for expense in expenses if isinstance(expense, Earnings)]
    spents = [expense for expense in expenses if  isinstance(expense, Spents)]

    total = sum(expense.amount for expense in earnings) - sum(expense.amount for expense in spents)
    return total

@register.simple_tag
def sum_expenses(transactions):
    spents = [expense for expense in transactions if  isinstance(expense, Spents)]
    return sum(expense.amount for expense in spents)

@register.simple_tag
def sum_earnings(transactions):
    earnings = [expense for expense in transactions if  isinstance(expense, Earnings)]
    return sum(expense.amount for expense in earnings)

@register.filter
def is_spent(expense):
    return isinstance(expense, Spents)