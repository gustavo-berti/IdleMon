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
from .forms import TipoPokemonForm, OvoForm
from .models import TipoPokemon, Ovo


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
    context_object_name = 'ovos'
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
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class OvoUpdateView(UpdateView):
    model = Ovo
    form_class = OvoForm
    template_name = 'pokemon/admin/ovo_form.html'
    success_url = reverse_lazy('ovo_list')


@method_decorator(staff_member_required, name='dispatch')
class OvoDeleteView(DeleteView):
    model = Ovo
    template_name = 'pokemon/admin/ovo_confirm_delete.html'
    success_url = reverse_lazy('ovo_list')