import json

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
    View,
)

from accounts.models import PerfilTreinador
from .forms import BoxForm, ChocarOvoForm, TipoPokemonForm, OvoForm
from .models import Box, TipoPokemon, Ovo, OvoInventario, PokemonInstancia
from .utils import populate_species_for_egg


# ============================================
# CRUD TipoPokemon (Admin Only)
# ============================================

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


@method_decorator(staff_member_required, name='dispatch')
class TipoPokemonListView(ListView):
    model = TipoPokemon
    template_name = 'pokemon/admin/tipopokemon_list.html'
    context_object_name = 'types'
    ordering = ['-base_generation_value', 'name']


@method_decorator(staff_member_required, name='dispatch')
class TipoPokemonCreateView(CreateView):
    model = TipoPokemon
    form_class = TipoPokemonForm
    template_name = 'pokemon/admin/tipopokemon_form.html'
    success_url = reverse_lazy('tipopokemon_list')


@method_decorator(staff_member_required, name='dispatch')
class TipoPokemonUpdateView(UpdateView):
    model = TipoPokemon
    form_class = TipoPokemonForm
    template_name = 'pokemon/admin/tipopokemon_form.html'
    success_url = reverse_lazy('tipopokemon_list')


@method_decorator(staff_member_required, name='dispatch')
class TipoPokemonDeleteView(DeleteView):
    model = TipoPokemon
    template_name = 'pokemon/admin/tipopokemon_confirm_delete.html'
    success_url = reverse_lazy('tipopokemon_list')


# ============================================
# CRUD Ovo (Admin Only)
# ============================================

@method_decorator(staff_member_required, name='dispatch')
class OvoListView(ListView):
    model = Ovo
    template_name = 'pokemon/admin/ovo_list.html'
    context_object_name = 'eggs'
    ordering = ['type__name', 'name']


@method_decorator(staff_member_required, name='dispatch')
class OvoCreateView(CreateView):
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


@method_decorator(staff_member_required, name='dispatch')
class OvoUpdateView(UpdateView):
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


@method_decorator(staff_member_required, name='dispatch')
class OvoDeleteView(DeleteView):
    model = Ovo
    template_name = 'pokemon/admin/ovo_confirm_delete.html'
    success_url = reverse_lazy('ovo_list')


# ============================================
# CRUD Box (User)
# ============================================

class BoxListView(LoginRequiredMixin, ListView):
    model = Box
    template_name = 'pokemon/box_list.html'
    context_object_name = 'boxes'

    def get_queryset(self):
        perfil, _ = PerfilTreinador.objects.get_or_create(user=self.request.user)
        return Box.objects.filter(trainer_profile=perfil).order_by('name')


class BoxCreateView(LoginRequiredMixin, CreateView):
    model = Box
    form_class = BoxForm
    template_name = 'pokemon/box_form.html'
    success_url = reverse_lazy('box_list')

    def form_valid(self, form):
        perfil, _ = PerfilTreinador.objects.get_or_create(user=self.request.user)
        form.instance.trainer_profile = perfil
        return super().form_valid(form)


class BoxUpdateView(LoginRequiredMixin, UpdateView):
    model = Box
    form_class = BoxForm
    template_name = 'pokemon/box_form.html'
    success_url = reverse_lazy('box_list')

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


# ============================================
# Loja de Ovos (User)
# ============================================

class LojaOvosView(LoginRequiredMixin, ListView):
    model = Ovo
    template_name = 'pokemon/loja_ovos.html'
    context_object_name = 'ovos_disponiveis'

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
        from django.shortcuts import render
        return render(request, 'pokemon/comprar_ovo.html', {
            'ovo': ovo,
            'saldo': perfil.coin_balance,
            'pode_comprar': perfil.coin_balance >= ovo.price,
            'quantidade_no_inventario': inventario.quantidade if inventario else 0,
        })


class MeusOvosView(LoginRequiredMixin, ListView):
    model = OvoInventario
    template_name = 'pokemon/meus_ovos.html'
    context_object_name = 'inventario'

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
        nickname = form.cleaned_data['nickname'] or inventario.ovo.name

        try:
            with transaction.atomic():
                occupied = set(box.pokemon_instances.values_list('box_position', flat=True))
                first_free = next((i for i in range(box.slots_max) if i not in occupied), None)

                pokemon = inventario.ovo.hatch(box=box, nickname=nickname)

                if first_free is not None:
                    pokemon.box_position = first_free
                    pokemon.save(update_fields=['box_position'])

                inventario.quantidade -= 1
                if inventario.quantidade == 0:
                    inventario.delete()
                else:
                    inventario.save(update_fields=['quantidade'])

            messages.success(
                request,
                f"Ovo chocado! Você recebeu um(a) {pokemon.species.name}! Verifique sua box '{box.name}'."
            )
            return redirect('meus_ovos')
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