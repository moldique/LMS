from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0005_course_updated_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='owner',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='lessons',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
