import requests
from typing import List, Dict, Tuple
from .models import Especie, TipoPokemon


def fetch_pokemon_by_type(tipo_nome: str) -> List[Dict]:
    """
    Busca todos os Pokémon de um determinado tipo na PokéAPI
    
    Args:
        tipo_nome: Nome do tipo em inglês (ex: 'fire', 'water', 'grass')
    
    Returns:
        Lista de dicionários com informações dos Pokémon
    """
    try:
        # Buscar todos os Pokémon do tipo
        url = f"https://pokeapi.co/api/v2/type/{tipo_nome.lower()}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        pokemon_list = data.get('pokemon', [])
        
        return pokemon_list
    except requests.RequestException as e:
        print(f"Erro ao buscar Pokémon do tipo {tipo_nome}: {e}")
        return []


def get_pokemon_details(pokemon_name: str) -> Dict:
    """
    Busca detalhes de um Pokémon específico
    
    Args:
        pokemon_name: Nome do Pokémon
    
    Returns:
        Dicionário com detalhes do Pokémon
    """
    try:
        url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        return response.json()
    except requests.RequestException as e:
        print(f"Erro ao buscar detalhes do Pokémon {pokemon_name}: {e}")
        return {}


def get_species_details(species_url: str) -> Dict:
    """
    Busca detalhes da espécie do Pokémon (para verificar evolução)
    
    Args:
        species_url: URL da espécie na PokéAPI
    
    Returns:
        Dicionário com detalhes da espécie
    """
    try:
        response = requests.get(species_url, timeout=10)
        response.raise_for_status()
        
        return response.json()
    except requests.RequestException as e:
        print(f"Erro ao buscar detalhes da espécie: {e}")
        return {}


def get_evolution_chain(evolution_chain_url: str) -> Dict:
    """
    Busca a cadeia evolutiva completa
    
    Args:
        evolution_chain_url: URL da cadeia evolutiva
    
    Returns:
        Dicionário com a cadeia evolutiva
    """
    try:
        response = requests.get(evolution_chain_url, timeout=10)
        response.raise_for_status()
        
        return response.json()
    except requests.RequestException as e:
        print(f"Erro ao buscar cadeia evolutiva: {e}")
        return {}


def parse_evolution_chain(chain: Dict) -> List[Dict]:
    """
    Parseia a cadeia evolutiva recursivamente
    
    Args:
        chain: Dicionário com a cadeia evolutiva
    
    Returns:
        Lista de todos os Pokémon na cadeia com seus estágios
    """
    pokemon_list = []
    
    def traverse(node, stage=1):
        if 'species' in node:
            pokemon_list.append({
                'name': node['species']['name'],
                'stage': stage
            })
        
        if 'evolves_to' in node:
            for evolution in node['evolves_to']:
                traverse(evolution, stage + 1)
    
    if 'chain' in chain:
        traverse(chain['chain'])
    
    return pokemon_list


def get_final_evolution_stats(pokemon_name: str) -> Tuple[int, int]:
    """
    Busca os stats da evolução final de um Pokémon
    
    Args:
        pokemon_name: Nome do Pokémon
    
    Returns:
        Tupla (base_stat_total, evolution_stage)
    """
    # Buscar detalhes da espécie
    pokemon_details = get_pokemon_details(pokemon_name)
    if not pokemon_details:
        return 0, 1
    
    species_url = pokemon_details.get('species', {}).get('url')
    if not species_url:
        return 0, 1
    
    species_details = get_species_details(species_url)
    if not species_details:
        return 0, 1
    
    evolution_chain_url = species_details.get('evolution_chain', {}).get('url')
    if not evolution_chain_url:
        return 0, 1
    
    # Buscar cadeia evolutiva
    evolution_chain = get_evolution_chain(evolution_chain_url)
    evolution_list = parse_evolution_chain(evolution_chain)
    
    if not evolution_list:
        return 0, 1
    
    # Encontrar evolução final
    final_evolution = max(evolution_list, key=lambda x: x['stage'])
    final_evolution_name = final_evolution['name']
    final_stage = final_evolution['stage']
    
    # Buscar stats da evolução final
    final_pokemon_details = get_pokemon_details(final_evolution_name)
    if not final_pokemon_details:
        return 0, final_stage
    
    # Calcular total de base stats
    stats = final_pokemon_details.get('stats', [])
    base_stat_total = sum(stat['base_stat'] for stat in stats)
    
    return base_stat_total, final_stage


def filter_initial_stage_pokemon(pokemon_list: List[Dict]) -> List[Dict]:
    """
    Filtra apenas Pokémon de estágio inicial ou únicos
    
    Args:
        pokemon_list: Lista de Pokémon retornados pela PokéAPI
    
    Returns:
        Lista filtrada de Pokémon
    """
    filtered_pokemon = []
    
    for entry in pokemon_list:
        pokemon_name = entry['pokemon']['name']
        
        # Buscar detalhes da espécie
        pokemon_details = get_pokemon_details(pokemon_name)
        if not pokemon_details:
            continue
        
        species_url = pokemon_details.get('species', {}).get('url')
        if not species_url:
            continue
        
        species_details = get_species_details(species_url)
        if not species_details:
            continue
        
        evolution_chain_url = species_details.get('evolution_chain', {}).get('url')
        if not evolution_chain_url:
            continue
        
        # Buscar cadeia evolutiva
        evolution_chain = get_evolution_chain(evolution_chain_url)
        evolution_list = parse_evolution_chain(evolution_chain)
        
        if not evolution_list:
            continue
        
        # Verificar se é o primeiro da cadeia evolutiva
        first_pokemon = min(evolution_list, key=lambda x: x['stage'])
        
        if first_pokemon['name'] == pokemon_name:
            # Buscar stats da evolução final para determinar raridade
            base_stat_total, final_stage = get_final_evolution_stats(pokemon_name)
            
            filtered_pokemon.append({
                'name': pokemon_name,
                'evolution_stage': 1,  # Sempre 1 pois é estágio inicial
                'final_evolution_stats': base_stat_total,
                'max_evolution_stage': final_stage
            })
    
    return filtered_pokemon


def populate_species_for_egg(ovo, tipo_pokemon: TipoPokemon):
    """
    Popula automaticamente as espécies de um ovo baseado no tipo
    
    Args:
        ovo: Instância do modelo Ovo
        tipo_pokemon: Instância do modelo TipoPokemon
    """
    # Mapear nome do tipo para nome em inglês da PokéAPI
    # Você pode expandir esse mapeamento conforme necessário
    type_mapping = {
        'Fogo': 'fire',
        'Água': 'water',
        'Grama': 'grass',
        'Elétrico': 'electric',
        'Psíquico': 'psychic',
        'Dragão': 'dragon',
        'Sombrio': 'dark',
        'Lutador': 'fighting',
        'Voador': 'flying',
        'Venenoso': 'poison',
        'Terrestre': 'ground',
        'Pedra': 'rock',
        'Inseto': 'bug',
        'Fantasma': 'ghost',
        'Aço': 'steel',
        'Fada': 'fairy',
        'Gelo': 'ice',
        'Normal': 'normal',
    }
    
    tipo_ingles = type_mapping.get(tipo_pokemon.name, tipo_pokemon.name.lower())
    
    # Buscar Pokémon do tipo
    pokemon_list = fetch_pokemon_by_type(tipo_ingles)
    
    # Filtrar apenas estágio inicial
    filtered_pokemon = filter_initial_stage_pokemon(pokemon_list)
    
    # Criar ou buscar espécies no banco de dados
    especies_adicionadas = []
    
    for pokemon_data in filtered_pokemon[:10]:  # Limitar a 10 espécies por ovo
        # Criar ou buscar a espécie
        especie, created = Especie.objects.get_or_create(
            name=pokemon_data['name'].capitalize(),
            defaults={
                'evolution_stage': pokemon_data['evolution_stage']
            }
        )
        
        # Adicionar o tipo à espécie se ainda não tiver
        if not especie.types.filter(id=tipo_pokemon.id).exists():
            especie.types.add(tipo_pokemon)
        
        especies_adicionadas.append(especie)
    
    # Adicionar todas as espécies ao ovo
    ovo.species.set(especies_adicionadas)
    
    return especies_adicionadas