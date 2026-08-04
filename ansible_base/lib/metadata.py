from rest_framework import serializers
from rest_framework.metadata import SimpleMetadata


def inject_clean_text_patterns(field, field_info):
    """
    If the parent serializer uses CleanTextMixin, inject Tier 1 validation
    pattern metadata into the field info dict for OPTIONS responses.

    Safe to call on any field — returns field_info unmodified when
    CleanTextMixin is not in the serializer's MRO or the field is not
    a text field subject to Tier 1 validation.
    """
    from ansible_base.lib.validators import CleanTextMixin, resource_name_validator

    serializer = field.parent
    if not isinstance(serializer, CleanTextMixin):
        return field_info

    if not isinstance(field, serializers.CharField):
        return field_info

    if field.field_name in serializer.name_fields:
        field_info['pattern'] = resource_name_validator.regex.pattern
        field_info['pattern_description'] = str(resource_name_validator.message)

    return field_info


class CleanTextMetadata(SimpleMetadata):
    """
    Extends SimpleMetadata to expose CleanTextMixin validation patterns
    in OPTIONS responses. Drop-in replacement for services that don't
    define their own metadata class.
    """

    def get_field_info(self, field):
        field_info = super().get_field_info(field)
        return inject_clean_text_patterns(field, field_info)
