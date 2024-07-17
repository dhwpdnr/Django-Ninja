# Generated by Django 5.0.1 on 2024-07-17 05:40

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("product", "0003_product_search_vector_product_tags_and_more"),
    ]

    operations = [
        migrations.RunSQL(sql="CREATE EXTENSION pg_bigm;", reverse_sql=""),
        migrations.AddIndex(
            model_name="product",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["name"],
                name="product_name_gin_index",
                opclasses=["gin_bigm_ops"],
            ),
        ),
    ]
