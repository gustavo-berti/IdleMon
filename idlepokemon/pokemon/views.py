from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from accounts.models import PerfilTreinador
from .forms import BoxForm, TipoPokemonForm, OvoForm
from .models import Box, TipoPokemon, Ovo
from .utils import populate_species_for_egg


# ============================================
# CRUD TipoPokemon (Admin Only)
# ============================================

class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin para restringir acesso apenas a staff/admin"""
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
        # Define o perfil_treinador como o admin atual (para fins de registro)
        perfil, created = PerfilTreinador.objects.get_or_create(user=self.request.user)
        form.instance.trainer_profile = perfil
        
        # Salvar o ovo primeiro
        response = super().form_valid(form)
        
        # Agora popular as espécies automaticamente via PokéAPI
        try:
            especies_adicionadas = populate_species_for_egg(self.object, self.object.type)
            
            if especies_adicionadas:
                messages.success(
                    self.request,
                    f"Ovo criado com sucesso! {len(especies_adicionadas)} espécies foram adicionadas automaticamente."
                )
            else:
                messages.warning(
                    self.request,
                    "Ovo criado, mas nenhuma espécie foi encontrada para o tipo selecionado. Verifique a conexão com a PokéAPI."
                )
        except Exception as e:
            messages.error(
                self.request,
                f"Ovo criado, mas houve um erro ao buscar as espécies: {str(e)}"
            )
        
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
                especies_adicionadas = populate_species_for_egg(self.object, self.object.type)
                
                if especies_adicionadas:
                    messages.success(
                        self.request,
                        f"Ovo atualizado! {len(especies_adicionadas)} espécies foram recarregadas."
                    )
                else:
                    messages.warning(
                        self.request,
                        "Ovo atualizado, mas nenhuma espécie foi encontrada para o novo tipo."
                    )
            except Exception as e:
                messages.error(
                    self.request,
                    f"Ovo atualizado, mas houve um erro ao buscar as espécies: {str(e)}"
                )
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
        perfil, created = PerfilTreinador.objects.get_or_create(user=self.request.user)
        return Box.objects.filter(trainer_profile=perfil).order_by('name')


class BoxCreateView(LoginRequiredMixin, CreateView):
    model = Box
    form_class = BoxForm
    template_name = 'pokemon/box_form.html'
    success_url = reverse_lazy('box_list')
    
    def form_valid(self, form):
        perfil, created = PerfilTreinador.objects.get_or_create(user=self.request.user)
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