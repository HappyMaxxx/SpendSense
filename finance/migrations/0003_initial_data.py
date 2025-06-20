# Generated by Django 5.2.3 on 2025-06-17 10:48

from django.db import migrations

def create_initial_categories(apps, schema_editor):
    EarnCategory = apps.get_model('finance', 'EarnCategory')
    SpentCategory = apps.get_model('finance', 'SpentCategory')

    if not EarnCategory.objects.filter(value='salary').exists():
        EarnCategory.objects.create(
            name="Salary",
            value="salary",
            icon="💰"
        )
        EarnCategory.objects.create(
            name="Deposit interest",
            value="deposit_interest",
            icon="🏛️"
        )
        EarnCategory.objects.create(
            name="Returning",
            value="returning",
            icon="🤝"
        )
        EarnCategory.objects.create(
            name="Gifts",
            value="gifts",
            icon="🎁"
        )

    if not SpentCategory.objects.filter(value='supermarket').exists():
        SpentCategory.objects.create(
            name="Supermarket",
            value="supermarket",
            icon="🛒"
        )
        SpentCategory.objects.create(
            name="Restaurants",
            value="restaurants",
            icon="🍽️"
        )
        SpentCategory.objects.create(
            name="Transport",
            value="transport",
            icon="🚗"
        )
        SpentCategory.objects.create(
            name="Home",
            value="home",
            icon="🏠"
        )
        SpentCategory.objects.create(
            name="Pets",
            value="pets",
            icon="🐶"
        )
        SpentCategory.objects.create(
            name="Clothing and footwear",
            value="clothing",
            icon="👕"
        )
        SpentCategory.objects.create(
            name="Vacation",
            value="vacation",
            icon="🌴"
        )
        SpentCategory.objects.create(
            name="Technology",
            value="technology",
            icon="💻"
        )
        SpentCategory.objects.create(
            name="Taxes",
            value="taxes",
            icon="🏛️"
        )
        SpentCategory.objects.create(
            name="Health",
            value="health",
            icon="🏥"
        )
        SpentCategory.objects.create(
            name="Gifts",
            value="gifts",
            icon="🎁"
        )
        SpentCategory.objects.create(
            name="Education",
            value="education",
            icon="📚"
        )
        SpentCategory.objects.create(
            name="Other",
            value="other",
            icon="🤷"
        )

class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0002_earncategory_spentcategory_alter_earnings_id_and_more'),
    ]

    operations = [
        migrations.RunPython(create_initial_categories),
    ]
