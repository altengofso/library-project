from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    d = context["request"].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()


@register.filter
def add_class(field, class_name):
    return field.as_widget(
        attrs={"class": " ".join((field.css_classes(), class_name))}
    )

@register.filter(name="placeholder")
def placeholder(value, token):
    """ Add placeholder attribute, esp. for form inputs and textareas """
    value.field.widget.attrs["placeholder"] = token
    return value
