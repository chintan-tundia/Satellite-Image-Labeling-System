# Generated by Django 3.2.5 on 2021-10-09 23:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Gmapv3', '0004_auto_20211010_0436'),
    ]

    operations = [
    	migrations.RunSQL("""
            INSERT INTO "Gmapv3_gmapmarker" (
                id,
                marked_date,
                locality,
                district,
                "geometryJSON",
                source_image_id,
                ground_truthing_done
            )
            SELECT
                id,
                marked_date,
                locality,
                district,
                "geometryJSON",
                source_image_id,
                ground_truthing_done
            FROM
                "Gmapv2_gmapmarker";
        """, reverse_sql="""
            INSERT INTO "Gmapv3_gmapmarker" (
                id,
                marked_date,
                locality,
                district,
                "geometryJSON",
                source_image_id,
                ground_truthing_done
            )
            SELECT
                id,
                marked_date,
                locality,
                district,
                "geometryJSON",
                source_image_id,
                ground_truthing_done
            FROM
                "Gmapv2_gmapmarker";
        """)
    ]