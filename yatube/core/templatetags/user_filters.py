from django import template
register = template.Library()


@register.filter
def addclass(field, css):
    """Добавляем атрибут class для верстки."""

    return field.as_widget(attrs={'class': css})
