from django.views.generic import TemplateView

TYPE_COLORS = {
    'Fogo': '#FF6B35',
    'Água': '#4A90D9',
    'Grama': '#4CAF50',
    'Elétrico': '#FFC107',
    'Psíquico': '#E91E63',
    'Dragão': '#6A1B9A',
    'Sombrio': '#37474F',
    'Lutador': '#795548',
    'Voador': '#90CAF9',
    'Venenoso': '#9C27B0',
    'Terrestre': '#8D6E63',
    'Pedra': '#9E9E9E',
    'Inseto': '#8BC34A',
    'Fantasma': '#4A148C',
    'Aço': '#607D8B',
    'Fada': '#F48FB1',
    'Gelo': '#80DEEA',
    'Normal': '#BDBDBD',
}


class HomeView(TemplateView):
    def get_template_names(self):
        if self.request.user.is_authenticated:
            return ['website/userLoggedIn.html']
        return ['website/home.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated:
            return context

        from accounts.models import PerfilTreinador
        from pokemon.models import Box

        perfil, _ = PerfilTreinador.objects.get_or_create(user=self.request.user)
        boxes = (
            Box.objects
            .filter(trainer_profile=perfil)
            .prefetch_related('pokemon_instances__species__types')
            .order_by('name')
        )

        box_data = []
        for box in boxes:
            slot_map = {}
            for p in box.pokemon_instances.all():
                if p.box_position is not None:
                    slot_map[p.box_position] = p

            slots = []
            for i in range(box.slots_max):
                pokemon = slot_map.get(i)
                if pokemon:
                    first_type = pokemon.species.types.first()
                    color = TYPE_COLORS.get(first_type.name if first_type else '', '#BDBDBD')
                    slots.append({'pokemon': pokemon, 'color': color, 'position': i})
                else:
                    slots.append({'pokemon': None, 'color': None, 'position': i})

            box_data.append({'box': box, 'slots': slots})

        context['box_data'] = box_data
        context['saldo'] = perfil.coin_balance
        return context


class AboutView(TemplateView):
    def get_template_names(self):
        return ['website/about.html']
