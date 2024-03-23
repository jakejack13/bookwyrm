# Generated by Django 3.2.20 on 2023-11-25 00:47

from importlib import import_module
import re

from django.db import migrations
import pgtrigger.compiler
import pgtrigger.migrations

trigger_migration = import_module("bookwyrm.migrations.0077_auto_20210623_2155")

# it's _very_ convenient for development that this migration be reversible
search_vector_trigger = trigger_migration.Migration.operations[4]
author_search_vector_trigger = trigger_migration.Migration.operations[5]


assert re.search(r"\bCREATE TRIGGER search_vector_trigger\b", search_vector_trigger.sql)
assert re.search(
    r"\bCREATE TRIGGER author_search_vector_trigger\b",
    author_search_vector_trigger.sql,
)


class Migration(migrations.Migration):
    dependencies = [
        ("bookwyrm", "0190_book_search_updates"),
    ]

    operations = [
        pgtrigger.migrations.AddTrigger(
            model_name="book",
            trigger=pgtrigger.compiler.Trigger(
                name="update_search_vector_on_book_edit",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    func="new.search_vector := setweight(coalesce(nullif(to_tsvector('english', new.title), ''), to_tsvector('simple', new.title)), 'A') || setweight(to_tsvector('english', coalesce(new.subtitle, '')), 'B') || (SELECT setweight(to_tsvector('simple', coalesce(array_to_string(array_agg(bookwyrm_author.name), ' '), '')), 'C') FROM bookwyrm_author LEFT JOIN bookwyrm_book_authors ON bookwyrm_author.id = bookwyrm_book_authors.author_id WHERE bookwyrm_book_authors.book_id = new.id ) || setweight(to_tsvector('english', coalesce(new.series, '')), 'D');RETURN NEW;",
                    hash="77d6399497c0a89b0bf09d296e33c396da63705c",
                    operation='INSERT OR UPDATE OF "title", "subtitle", "series", "search_vector"',
                    pgid="pgtrigger_update_search_vector_on_book_edit_bec58",
                    table="bookwyrm_book",
                    when="BEFORE",
                ),
            ),
        ),
        pgtrigger.migrations.AddTrigger(
            model_name="author",
            trigger=pgtrigger.compiler.Trigger(
                name="reset_search_vector_on_author_edit",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    func="WITH updated_books AS (SELECT book_id FROM bookwyrm_book_authors WHERE author_id = new.id ) UPDATE bookwyrm_book SET search_vector = '' FROM updated_books WHERE id = updated_books.book_id;RETURN NEW;",
                    hash="e7bbf08711ff3724c58f4d92fb7a082ffb3d7826",
                    operation='UPDATE OF "name"',
                    pgid="pgtrigger_reset_search_vector_on_author_edit_a447c",
                    table="bookwyrm_author",
                    when="AFTER",
                ),
            ),
        ),
        migrations.RunSQL(
            sql="""DROP TRIGGER IF EXISTS search_vector_trigger ON bookwyrm_book;
                   DROP FUNCTION IF EXISTS book_trigger;
            """,
            reverse_sql=search_vector_trigger.sql,
        ),
        migrations.RunSQL(
            sql="""DROP TRIGGER IF EXISTS author_search_vector_trigger ON bookwyrm_author;
                   DROP FUNCTION IF EXISTS author_trigger;
            """,
            reverse_sql=author_search_vector_trigger.sql,
        ),
        migrations.RunSQL(
            # Recalculate book search vector for any missed author name changes
            # due to bug in JOIN in the old trigger.
            sql="UPDATE bookwyrm_book SET search_vector = NULL;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]