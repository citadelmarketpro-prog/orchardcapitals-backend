from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_fix_decimal_overflow'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='source',
            field=models.CharField(
                blank=True,
                choices=[('balance', 'Main Balance'), ('profit', 'Profit')],
                default='balance',
                max_length=10,
            ),
        ),
    ]
