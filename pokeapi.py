"""PokeAPI integration for Pokemon data."""

import requests
import time
from functools import lru_cache

POKEAPI_BASE = "https://pokeapi.co/api/v2"

# Cache for Pokemon data
_pokemon_cache = {}
_types_cache = None

def get_pokemon_sprite(pokemon_id, shiny=False):
    """Get sprite URL for a Pokemon."""
    # Use PokeAPI's official sprites - they have both regular and shiny
    if shiny:
        return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/{pokemon_id}.png"
    return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pokemon_id}.png"

def get_pokemon_data(pokemon_id_or_name):
    """Get full Pokemon data from PokeAPI."""
    if isinstance(pokemon_id_or_name, int) or pokemon_id_or_name.isdigit():
        cache_key = int(pokemon_id_or_name)
    else:
        cache_key = pokemon_id_or_name.lower()
    
    if cache_key in _pokemon_cache:
        return _pokemon_cache[cache_key]
    
    try:
        response = requests.get(f"{POKEAPI_BASE}/pokemon/{pokemon_id_or_name}", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Simplify and cache
        simplified = {
            'id': data['id'],
            'name': data['name'].capitalize(),
            'types': [t['type']['name'].capitalize() for t in data['types']],
            'sprite': data['sprites']['front_default'],
            'shiny_sprite': data['sprites']['front_shiny'],
            'height': data['height'] / 10,  # Convert to meters
            'weight': data['weight'] / 10,  # Convert to kg
            'abilities': [a['ability']['name'].replace('-', ' ').title() for a in data['abilities']],
        }
        
        _pokemon_cache[cache_key] = simplified
        _pokemon_cache[data['id']] = simplified
        
        return simplified
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Pokemon {pokemon_id_or_name}: {e}")
        return None

@lru_cache(maxsize=1)
def get_all_pokemon():
    """Get list of all Pokemon (up to Gen 9 for Scarlet/Violet + Z-A)."""
    try:
        # Get Pokemon up to Gen 9 (index 1025 for Paldean + new Kalos)
        response = requests.get(f"{POKEAPI_BASE}/pokemon?limit=1025", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        pokemon_list = []
        for p in data['results']:
            # Extract ID from URL
            url_parts = p['url'].rstrip('/').split('/')
            poke_id = int(url_parts[-1])
            
            pokemon_list.append({
                'id': poke_id,
                'name': p['name'].capitalize(),
                'sprite': get_pokemon_sprite(poke_id, shiny=False),
                'shiny_sprite': get_pokemon_sprite(poke_id, shiny=True),
            })
        
        return pokemon_list
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Pokemon list: {e}")
        return []

def get_pokemon_by_type(pokemon_type):
    """Get all Pokemon of a specific type."""
    try:
        response = requests.get(f"{POKEAPI_BASE}/type/{pokemon_type.lower()}", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        pokemon_list = []
        for p in data['pokemon']:
            url_parts = p['pokemon']['url'].rstrip('/').split('/')
            poke_id = int(url_parts[-1])
            
            pokemon_list.append({
                'id': poke_id,
                'name': p['pokemon']['name'].capitalize(),
                'sprite': get_pokemon_sprite(poke_id),
                'shiny_sprite': get_pokemon_sprite(poke_id, shiny=True),
            })
        
        return pokemon_list
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Pokemon by type: {e}")
        return []

def get_types():
    """Get all Pokemon types."""
    global _types_cache
    
    if _types_cache is not None:
        return _types_cache
    
    try:
        response = requests.get(f"{POKEAPI_BASE}/type", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        _types_cache = [t['name'].capitalize() for t in data['results']]
        return _types_cache
    except requests.exceptions.RequestException as e:
        print(f"Error fetching types: {e}")
        return []

# Hunt method recommendations based on game and Pokemon
HUNT_METHODS = {
    'respawn': 'Respawn - Defeat Pokemon and respawn it to encounter again',
    'fast_travel': 'Fast Travel - Use fast travel to reset spawns',
    'door_method': 'Door Method - Open/close doors to respawn Pokemon',
    'special_scan': 'Special Scan - Use the Scanner in Pokemon GO (for transfer)',
    'soft_reboot': 'Soft-reboot - Close and reopen the game',
}

def get_recommended_method(pokemon_name, game='PLA'):
    """Get recommended shiny hunting method based on game."""
    # In Pokemon Legends: Z-A (Kalos), methods are different
    # These are general recommendations
    recommendations = {
        'PLA': ['respawn', 'fast_travel', 'special_scan'],
        'SV': ['sandwich', 'mass_outbreak', 'tera_raid', 'fishing', 'soft_reboot'],
        'Z-A': ['respawn', 'fast_travel', 'door_method', 'special_scan', 'soft_reboot'],
    }
    
    return recommendations.get(game, HUNT_METHODS)

if __name__ == '__main__':
    # Test
    print("Testing PokeAPI...")
    all_pokemon = get_all_pokemon()
    print(f"Fetched {len(all_pokemon)} Pokemon")
    
    if all_pokemon:
        print(f"First Pokemon: {all_pokemon[0]}")