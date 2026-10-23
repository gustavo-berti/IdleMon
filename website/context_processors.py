def administrador(request):
    """Expõe is_administrador para o menu: mesmo critério do GroupRequiredMixin das views admin."""
    user = getattr(request, 'user', None)
    is_administrador = bool(
        user and user.is_authenticated
        and (user.is_superuser or user.groups.filter(name='administradores').exists())
    )
    return {'is_administrador': is_administrador}
