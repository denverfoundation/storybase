import uuid

from uuidfield.fields import StringUUID


# Reusable functions used in app migrations

def to_uuid(obj, prop):
    tmp_prop = '_'.join(['tmp', prop])
    setattr(obj, tmp_prop, uuid.UUID(getattr(obj, prop).hex))
    return obj

def to_char32(obj, prop):
    tmp_prop = '_'.join(['tmp', prop])
    setattr(obj, tmp_prop, StringUUID(getattr(obj, prop).hex))
    return obj

def transform(using, app_name, model_name, field_name):
    def fn(apps, schema_editor):
        model = apps.get_model(app_name, model_name)
        db_alias = schema_editor.connection.alias
        for obj in model.objects.using(db_alias).all():
            using(obj, field_name).save()
    return fn


