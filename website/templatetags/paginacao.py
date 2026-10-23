from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def parametros_url(context, **kwargs):
    """Querystring da busca atual trocando só os parâmetros informados.

    Uso: <a href="?{% parametros_url page=2 %}">. Mantém os filtros (nome, tipo...) ao
    trocar de página; um valor vazio remove o parâmetro.
    """
    params = context['request'].GET.copy()
    for chave, valor in kwargs.items():
        if valor in (None, ''):
            params.pop(chave, None)
        else:
            params[chave] = valor
    return params.urlencode()
