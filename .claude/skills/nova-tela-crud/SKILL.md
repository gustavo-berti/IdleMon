---
name: nova-tela-crud
description: Receita para criar telas de listagem, cadastro, edição, detalhe e exclusão no IdleMon com Class-Based Views, dono do registro, mensagens, django-filter e paginação. Use ao criar ou alterar qualquer CRUD.
---

# Nova tela CRUD

Modelo a copiar: CRUD de `Box` e de `PokemonInstancia` em `pokemon/views.py`.

## 1. Acesso

- **Admin:** `class XListView(GroupRequiredMixin, FilterView)` com `group_required = ['administradores']`.
- **Treinador (registro tem dono):** `LoginRequiredMixin` e **todas** as views filtram pelo dono:
  ```python
  def get_queryset(self):
      return Box.objects.filter(trainer_profile__user=self.request.user)
  ```
  Isso vale para List, Detail, Update e Delete: registro de outro usuário vira 404.
  No Create, preencha o dono em `form_valid` (`form.instance.trainer_profile = perfil`), nunca pelo formulário.
- Campos de chave estrangeira no form devem listar só registros do próprio usuário (veja `PokemonInstanciaForm`).

## 2. Mensagens

- Create/Update: `SuccessMessageMixin` com `success_message = "Box '%(name)s' criada!"`.
- Delete: sobrescreva `form_valid` e chame `messages.success(self.request, f"... '{self.object.name}' excluído.")`
  antes do `super()`. Trate `ProtectedError` com `messages.error` e redirect.
- As mensagens aparecem sozinhas: `website/template.html` já as exibe.

## 3. Listagem com filtro e paginação

1. Em `<app>/filters.py`:
   ```python
   class BoxFilter(django_filters.FilterSet):
       name = django_filters.CharFilter(lookup_expr='icontains', label='Nome')
       class Meta:
           model = Box
           fields = ('name',)
   ```
2. Na view: herde de `django_filters.views.FilterView`, defina `filterset_class` e `paginate_by`.
3. No template, antes da lista e no fim do container:
   ```django
   {% include 'website/partials/filtro.html' %}
   ...
   {% include 'website/partials/paginacao.html' %}
   ```
   A paginação usa a templatetag própria `{% parametros_url page=N %}` (`website/templatetags/paginacao.py`),
   que preserva os filtros. Não escreva `?page=N` direto.
4. Estado vazio: com `request.GET` preenchido diga "nenhum resultado para os filtros" e ofereça "Limpar".

## 4. Consultas

- `select_related` para FK e `prefetch_related` para M2M/reverso que o template acessa.
- Contagem por linha: `annotate(total=Count(...))` em vez de `.count` no template.
- Confira na aba SQL da Django Debug Toolbar (`/__debug__/`) que o número de consultas não cresce com a lista.

## 5. Templates e URLs

- Templates estendem `website/template.html`; formulários com `{{ form|crispy }}`; botão principal `btn btn-poke`.
- Exclusão: página `*_confirm_delete.html` ou formulário com `data-confirmar="..."` (Bootbox).
- URLs em `<app>/urls.py` no padrão `boxes/`, `boxes/nova/`, `boxes/<int:pk>/`, `boxes/<int:pk>/editar/`,
  `boxes/<int:pk>/excluir/`; nomes `box_list`, `box_create`, `box_detail`, `box_update`, `box_delete`.
- Adicione o link no menu (`website/templates/website/partials/navbar.html`).

## 6. Testes

No `tests.py` do app, cubra no mínimo: dono acessa (200), outro usuário recebe 404 em detail/update/delete,
mensagem aparece após criar/alterar/excluir, filtro reduz a lista e a paginação mantém o filtro.
