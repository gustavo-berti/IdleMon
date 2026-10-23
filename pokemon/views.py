import json

from braces.views import GroupRequiredMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.db.models import Count, ProtectedError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)
from django_filters.views import FilterView

from accounts.models import PerfilTreinador
from .filters import OvoFilter, OvoInventarioFilter, TipoPokemonFilter
from .forms import BoxForm, ChocarOvoForm, PokemonInstanciaForm, TipoPokemonForm, OvoForm
from .models import (
    BOX_PRICE,
    MAX_ACTIVE_TEAM,
    Box,
    TipoPokemon,
    Ovo,
    OvoInventario,
    PokemonInstancia,
)
from .utils import populate_species_for_egg


# ============================================
# CRUD TipoPokemon (Admin Only)
# ============================================

class TipoPokemonListView(GroupRequiredMixin, FilterView):
    group_required = ['administradores']
    model = TipoPokemon
    filterset_class = TipoPokemonFilter
    template_name = 'pokemon/admin/tipopokemon_list.html'
    context_object_name = 'types'
    ordering = ['-base_generation_value', 'name']
    paginate_by = 10


class TipoPokemonCreateView(GroupRequiredMixin, SuccessMessageMixin, CreateView):
    group_required = ['administradores']
    model = TipoPokemon
    form_class = TipoPokemonForm
    template_name = 'pokemon/admin/tipopokemon_form.html'
    success_url = reverse_lazy('tipopokemon_list')
    success_message = "Tipo '%(name)s' criado com sucesso!"


class TipoPokemonUpdateView(GroupRequiredMixin, SuccessMessageMixin, UpdateView):
    group_required = ['administradores']
    model = TipoPokemon
    form_class = TipoPokemonForm
    template_name = 'pokemon/admin/tipopokemon_form.html'
    success_url = reverse_lazy('tipopokemon_list')
    success_message = "Tipo '%(name)s' atualizado com sucesso!"


class TipoPokemonDeleteView(GroupRequiredMixin, DeleteView):
    group_required = ['administradores']
    model = TipoPokemon
    template_name = 'pokemon/admin/tipopokemon_confirm_delete.html'
    success_url = reverse_lazy('tipopokemon_list')

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                f"O tipo '{self.object.name}' não pode ser excluído: existem ovos usando este tipo."
            )
            return redirect('tipopokemon_list')
        messages.success(self.request, f"Tipo '{self.object.name}' excluído.")
        return response


# ============================================
# CRUD Ovo (Admin Only)
# ============================================

class OvoListView(GroupRequiredMixin, FilterView):
    group_required = ['administradores']
    model = Ovo
    filterset_class = OvoFilter
    template_name = 'pokemon/admin/ovo_list.html'
    context_object_name = 'eggs'
    paginate_by = 10

    def get_queryset(self):
        return (
            Ovo.objects
            .select_related('type', 'trainer_profile__user')
            .prefetch_related('species')
            .order_by('type__name', 'name')
        )


class OvoCreateView(GroupRequiredMixin, CreateView):
    group_required = ['administradores']
    model = Ovo
    form_class = OvoForm
    template_name = 'pokemon/admin/ovo_form.html'
    success_url = reverse_lazy('ovo_list')

    def form_valid(self, form):
        perfil, _ = PerfilTreinador.objects.get_or_create(user=self.request.user)
        form.instance.trainer_profile = perfil
        response = super().form_valid(form)
        try:
            especies = populate_species_for_egg(self.object, self.object.type)
            if especies:
                messages.success(self.request, f"Ovo criado! {len(especies)} espécies adicionadas automaticamente.")
            else:
                messages.warning(self.request, "Ovo criado, mas nenhuma espécie foi encontrada na PokéAPI.")
        except Exception as e:
            messages.error(self.request, f"Ovo criado, mas erro ao buscar espécies: {e}")
        return response


class OvoUpdateView(GroupRequiredMixin, UpdateView):
    group_required = ['administradores']
    model = Ovo
    form_class = OvoForm
    template_name = 'pokemon/admin/ovo_form.html'
    success_url = reverse_lazy('ovo_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        if 'type' in form.changed_data:
            try:
                self.object.species.clear()
                especies = populate_species_for_egg(self.object, self.object.type)
                if especies:
                    messages.success(self.request, f"Ovo atualizado! {len(especies)} espécies recarregadas.")
                else:
                    messages.warning(self.request, "Ovo atualizado, mas nenhuma espécie encontrada para o novo tipo.")
            except Exception as e:
                messages.error(self.request, f"Ovo atualizado, mas erro ao buscar espécies: {e}")
        else:
            messages.success(self.request, "Ovo atualizado com sucesso!")
        return response


class OvoDeleteView(GroupRequiredMixin, DeleteView):
    group_required = ['administradores']
    model = Ovo
    template_name = 'pokemon/admin/ovo_confirm_delete.html'
    success_url = reverse_lazy('ovo_list')

    def form_valid(self, form):
        messages.success(self.request, f"Ovo '{self.object.name}' excluído.")
        return super().form_valid(form)


# ============================================
# CRUD Box (User)
# ============================================

class BoxListView(LoginRequiredMixin, ListView):
    model = Box
    template_name = 'pokemon/box_list.html'
    context_object_name = 'boxes'

    def get_queryset(self):
        perfil, _ = PerfilTreinador.objects.get_or_create(user=self.request.user)
        return (
            Box.objects
            .filter(trainer_profile=perfil)
            .annotate(pokemon_count=Count('pokemon_instances'))
            .order_by('name')
        )


class BoxDetailView(LoginRequiredMixin, DetailView):
    model = Box
    template_name = 'pokemon/box_detail.html'
    context_object_name = 'box'

    def get_queryset(self):
        return Box.objects.filter(trainer_profile__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pokemons'] = (
            self.object.pokemon_instances
            .select_related('species')
            .prefetch_related('species__types')
            .order_by('box_position', 'id')
        )
        return context


class BoxCreateView(LoginRequiredMixin, CreateView):
    model = Box
    form_class = BoxForm
    template_name = 'pokemon/box_form.html'
    success_url = reverse_lazy('box_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        perfil, _ = PerfilTreinador.objects.get_or_create(user=self.request.user)
        context['preco'] = BOX_PRICE if perfil.boxes.exists() else 0
        context['saldo'] = perfil.coin_balance
        return context

    def form_valid(self, form):
        perfil, _ = PerfilTreinador.objects.get_or_create(user=self.request.user)
        # A primeira box é gratuita; as demais custam BOX_PRICE
        preco = BOX_PRICE if perfil.boxes.exists() else 0
        if perfil.coin_balance < preco:
            messages.error(self.request, f"Saldo insuficiente! Uma nova box custa {BOX_PRICE} moedas.")
            return self.form_invalid(form)

        form.instance.trainer_profile = perfil
        with transaction.atomic():
            if preco:
                perfil.manage_account(-preco)
            response = super().form_valid(form)

        if preco:
            messages.success(self.request, f"Box '{self.object.name}' comprada por {preco} moedas!")
        else:
            messages.success(self.request, f"Box '{self.object.name}' criada! A primeira box é por nossa conta.")
        return response


class BoxUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Box
    form_class = BoxForm
    template_name = 'pokemon/box_form.html'
    success_url = reverse_lazy('box_list')
    success_message = "Box renomeada para '%(name)s'."

    def get_queryset(self):
        perfil = get_object_or_404(PerfilTreinador, user=self.request.user)
        return Box.objects.filter(trainer_profile=perfil)


class BoxDeleteView(LoginRequiredMixin, DeleteView):
    model = Box
    template_name = 'pokemon/box_confirm_delete.html'
    success_url = reverse_lazy('box_list')

    def get_queryset(self):
        perfil = get_object_or_404(PerfilTreinador, user=self.request.user)
        return Box.objects.filter(trainer_profile=perfil)

    def form_valid(self, form):
        perfil = self.object.trainer_profile
        if self.object.pokemon_instances.filter(is_active_team=True).exists():
            perfil.collect_income()
        messages.success(self.request, f"Box '{self.object.name}' excluída.")
        return super().form_valid(form)


# ============================================
# Pokémon do Jogador (User)
# ============================================

class PokemonOwnerMixin(LoginRequiredMixin):
    """Restringe as views de PokemonInstancia aos Pokémons do próprio treinador."""
    model = PokemonInstancia
    context_object_name = 'pokemon'

    def get_queryset(self):
        return (
            PokemonInstancia.objects
            .filter(box__trainer_profile__user=self.request.user)
            .select_related('species', 'box')
            .prefetch_related('species__types')
        )


class PokemonDetailView(PokemonOwnerMixin, DetailView):
    template_name = 'pokemon/pokemon_detail.html'


class PokemonUpdateView(PokemonOwnerMixin, UpdateView):
    form_class = PokemonInstanciaForm
    template_name = 'pokemon/pokemon_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['perfil'] = get_object_or_404(PerfilTreinador, user=self.request.user)
        return kwargs

    def get_success_url(self):
        return reverse_lazy('pokemon_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        with transaction.atomic():
            if 'is_active_team' in form.changed_data:
                form.perfil.collect_income()
            if 'box' in form.changed_data:
                form.instance.box_position = form.cleaned_data['box'].first_free_position()
            response = super().form_valid(form)
        messages.success(self.request, f"{self.object.nickname} atualizado com sucesso!")
        return response


class PokemonDeleteView(PokemonOwnerMixin, DeleteView):
    template_name = 'pokemon/pokemon_confirm_delete.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        if self.object.is_active_team:
            self.object.box.trainer_profile.collect_income()
        messages.success(self.request, f"{self.object.nickname} foi libertado. Adeus, {self.object.species.name}!")
        return super().form_valid(form)


class PokemonEquipeView(LoginRequiredMixin, View):
    """Coloca ou retira o Pokémon da Equipe Ativa (botão da tela inicial)."""

    def post(self, request, pk):
        pokemon = get_object_or_404(PokemonInstancia, pk=pk, box__trainer_profile__user=request.user)
        perfil = pokemon.box.trainer_profile

        if not pokemon.is_active_team:
            em_equipe = PokemonInstancia.objects.filter(box__trainer_profile=perfil, is_active_team=True).count()
            if em_equipe >= MAX_ACTIVE_TEAM:
                messages.error(request, f"Sua Equipe Ativa já tem {MAX_ACTIVE_TEAM} Pokémons. Retire um antes.")
                return redirect('home')

        with transaction.atomic():
            perfil.collect_income()
            pokemon.is_active_team = not pokemon.is_active_team
            pokemon.save(update_fields=['is_active_team'])

        if pokemon.is_active_team:
            messages.success(
                request,
                f"{pokemon.nickname} entrou na Equipe Ativa e rende {pokemon.generate_profit()} moedas / hora!"
            )
        else:
            messages.info(request, f"{pokemon.nickname} saiu da Equipe Ativa.")
        return redirect(request.POST.get('next') or 'home')


class ColetarRendimentoView(LoginRequiredMixin, View):
    def post(self, request):
        perfil = get_object_or_404(PerfilTreinador, user=request.user)
        valor = perfil.collect_income()
        if valor:
            messages.success(request, f"Você coletou {valor} moedas da sua Equipe Ativa! 🪙")
        else:
            messages.info(request, "Ainda não há moedas para coletar. Coloque Pokémons na Equipe Ativa.")
        return redirect('home')


# ============================================
# Loja de Ovos (User)
# ============================================

class LojaOvosView(LoginRequiredMixin, FilterView):
    model = Ovo
    filterset_class = OvoFilter
    template_name = 'pokemon/loja_ovos.html'
    context_object_name = 'ovos_disponiveis'
    paginate_by = 9

    def get_queryset(self):
        return (
            Ovo.objects
            .filter(trainer_profile__user__is_staff=True)
            .select_related('type', 'trainer_profile')
            .prefetch_related('species')
            .order_by('type__name', 'price')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        perfil, _ = PerfilTreinador.objects.get_or_create(user=self.request.user)
        context['saldo'] = perfil.coin_balance
        # Mapa ovo_id -> quantidade no inventário do jogador
        inventario = {
            inv.ovo_id: inv.quantidade
            for inv in OvoInventario.objects.filter(trainer_profile=perfil)
        }
        for ovo in context['ovos_disponiveis']:
            ovo.quantidade_no_inventario = inventario.get(ovo.id, 0)
        return context


class ComprarOvoView(LoginRequiredMixin, View):
    def get(self, request, pk):
        ovo = get_object_or_404(Ovo, pk=pk, trainer_profile__user__is_staff=True)
        perfil, _ = PerfilTreinador.objects.get_or_create(user=request.user)
        inventario = OvoInventario.objects.filter(trainer_profile=perfil, ovo=ovo).first()
        return self._render(request, ovo, perfil, inventario)

    def post(self, request, pk):
        ovo = get_object_or_404(Ovo, pk=pk, trainer_profile__user__is_staff=True)
        perfil = get_object_or_404(PerfilTreinador, user=request.user)

        if perfil.coin_balance < ovo.price:
            messages.error(request, "Saldo insuficiente para comprar este ovo!")
            return redirect('comprar_ovo', pk=pk)

        try:
            with transaction.atomic():
                perfil.manage_account(-ovo.price)
                inventario, created = OvoInventario.objects.get_or_create(
                    trainer_profile=perfil,
                    ovo=ovo,
                    defaults={'quantidade': 1},
                )
                if not created:
                    inventario.quantidade += 1
                    inventario.save(update_fields=['quantidade'])

            messages.success(
                request,
                f"'{ovo.name}' adicionado ao inventário! Saldo restante: {perfil.coin_balance} 🪙"
            )
            return redirect('meus_ovos')
        except Exception as e:
            messages.error(request, f"Erro ao comprar ovo: {e}")
            return redirect('comprar_ovo', pk=pk)

    def _render(self, request, ovo, perfil, inventario):
        return render(request, 'pokemon/comprar_ovo.html', {
            'ovo': ovo,
            'especies': ovo.species.prefetch_related('types').order_by('-bst_final', 'name'),
            'saldo': perfil.coin_balance,
            'pode_comprar': perfil.coin_balance >= ovo.price,
            'quantidade_no_inventario': inventario.quantidade if inventario else 0,
        })


class MeusOvosView(LoginRequiredMixin, FilterView):
    model = OvoInventario
    filterset_class = OvoInventarioFilter
    template_name = 'pokemon/meus_ovos.html'
    context_object_name = 'inventario'
    paginate_by = 9

    def get_queryset(self):
        perfil = get_object_or_404(PerfilTreinador, user=self.request.user)
        return (
            OvoInventario.objects
            .filter(trainer_profile=perfil)
            .select_related('ovo__type')
            .prefetch_related('ovo__species')
            .order_by('-id')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        perfil = get_object_or_404(PerfilTreinador, user=self.request.user)
        context['saldo'] = perfil.coin_balance
        return context


# ============================================
# Chocar Ovo (User)
# ============================================

class ChocarOvoView(LoginRequiredMixin, View):
    def get(self, request, pk):
        inventario = get_object_or_404(OvoInventario, pk=pk, trainer_profile__user=request.user)
        perfil = get_object_or_404(PerfilTreinador, user=request.user)
        form = ChocarOvoForm(perfil=perfil)
        return render(request, 'pokemon/chocar_ovo.html', {
            'inventario': inventario,
            'form': form,
        })

    def post(self, request, pk):
        inventario = get_object_or_404(OvoInventario, pk=pk, trainer_profile__user=request.user)
        perfil = get_object_or_404(PerfilTreinador, user=request.user)
        form = ChocarOvoForm(request.POST, perfil=perfil)

        if not form.is_valid():
            return render(request, 'pokemon/chocar_ovo.html', {
                'inventario': inventario,
                'form': form,
            })

        box = form.cleaned_data['box']
        nickname = form.cleaned_data['nickname']

        try:
            with transaction.atomic():
                pokemon = inventario.ovo.hatch(box=box, nickname=nickname)

                inventario.quantidade -= 1
                if inventario.quantidade == 0:
                    inventario.delete()
                else:
                    inventario.save(update_fields=['quantidade'])

            messages.success(
                request,
                f"Ovo chocado! Você recebeu um(a) {pokemon.species.name} ({pokemon.species.rarity_name})! "
                f"Verifique sua box '{box.name}'."
            )
            return redirect('pokemon_detail', pk=pokemon.pk)
        except Exception as e:
            messages.error(request, f"Erro ao chocar ovo: {e}")
            return render(request, 'pokemon/chocar_ovo.html', {
                'inventario': inventario,
                'form': form,
            })


# ============================================
# Descartar Ovo do Inventário (User)
# ============================================

class DescartarOvoView(LoginRequiredMixin, View):
    def post(self, request, pk):
        inventario = get_object_or_404(OvoInventario, pk=pk, trainer_profile__user=request.user)

        inventario.quantidade -= 1
        if inventario.quantidade == 0:
            inventario.delete()
            messages.success(request, f"Ovo '{inventario.ovo.name}' descartado.")
        else:
            inventario.save(update_fields=['quantidade'])
            messages.success(
                request,
                f"1x '{inventario.ovo.name}' descartado. Restam {inventario.quantidade} no inventário."
            )

        return redirect('meus_ovos')


# ============================================
# Atualizar Posição na Box (AJAX)
# ============================================

class UpdatePokemonPositionView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            pokemon_id = int(data['pokemon_id'])
            new_position = int(data['position'])
        except (KeyError, ValueError, json.JSONDecodeError):
            return JsonResponse({'error': 'Dados inválidos'}, status=400)

        perfil = get_object_or_404(PerfilTreinador, user=request.user)
        pokemon = get_object_or_404(PokemonInstancia, pk=pokemon_id, box__trainer_profile=perfil)

        if not (0 <= new_position < pokemon.box.slots_max):
            return JsonResponse({'error': 'Posição fora do intervalo'}, status=400)

        with transaction.atomic():
            occupant = (
                PokemonInstancia.objects
                .select_for_update()
                .filter(box=pokemon.box, box_position=new_position)
                .exclude(pk=pokemon.pk)
                .first()
            )
            old_position = pokemon.box_position
            if occupant:
                occupant.box_position = old_position
                occupant.save(update_fields=['box_position'])
            pokemon.box_position = new_position
            pokemon.save(update_fields=['box_position'])

        return JsonResponse({'success': True})
