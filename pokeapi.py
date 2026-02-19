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

# Z-A Pokedex - Pokemon available in Pokemon Legends: Z-A
# Source: pokemondb.net/pokedex/game/legends-z-a (~230 Pokemon)
ZA_POKEDEX = {
    'chikorita', 'bayleef', 'meganium', 'tepig', 'pignite', 'emboar', 'totodile', 'croconaw', 'feraligatr',
    'fletchling', 'fletchinder', 'talonflame', 'bunnelby', 'diggersby', 'scatterbug', 'spewpa', 'vivillon',
    'weedle', 'kakuna', 'beedrill', 'pidgey', 'pidgeotto', 'pidgeot', 'mareep', 'flaaffy', 'ampharos',
    'patrat', 'watchog', 'budew', 'roselia', 'roserade', 'magikarp', 'gyarados', 'binacle', 'barbaracle',
    'staryu', 'starmie', 'flabebe', 'floette', 'florges', 'skiddo', 'gogoat', 'espurr', 'meowstic',
    'litleo', 'pyroar', 'pancham', 'pangoro', 'trubbish', 'garbodor', 'dedenne', 'pichu', 'pikachu', 'raichu',
    'cleffa', 'clefairy', 'clefable', 'spinarak', 'ariados', 'ekans', 'arbok', 'abra', 'kadabra', 'alakazam',
    'gastly', 'haunter', 'gengar', 'venipede', 'whirlipede', 'scolipede', 'honedge', 'doublade', 'aegislash',
    'bellsprout', 'weepinbell', 'victreebel', 'pansage', 'simisage', 'pansear', 'simisear', 'panpour', 'simipour',
    'meditite', 'medicham', 'electrike', 'manectric', 'ralts', 'kirlia', 'gardevoir', 'gallade', 'houndour',
    'houndoom', 'swablu', 'altaria', 'audino', 'spritzee', 'aromatisse', 'swirlix', 'slurpuff', 'eevee',
    'vaporeon', 'jolteon', 'flareon', 'espeon', 'umbreon', 'leafeon', 'glaceon', 'sylveon', 'buneary', 'lopunny',
    'shuppet', 'banette', 'vanillite', 'vanillish', 'vanilluxe', 'numel', 'camerupt', 'hippopotas', 'hippowdon',
    'drilbur', 'excadrill', 'sandile', 'krokorok', 'krookodile', 'machop', 'machoke', 'machamp', 'gible',
    'gabite', 'garchomp', 'carbink', 'sableye', 'mawile', 'absol', 'riolu', 'lucario', 'slowpoke', 'slowbro',
    'slowking', 'carvanha', 'sharpedo', 'tynamo', 'eelektrik', 'eelektross', 'dratini', 'dragonair', 'dragonite',
    'bulbasaur', 'ivysaur', 'venusaur', 'charmander', 'charmeleon', 'charizard', 'squirtle', 'wartortle', 'blastoise',
    'stunfisk', 'furfrou', 'klefki', 'deoxys', 'heatran', 'regigigas', 'giratina', 'cresselia',
    'tornadus', 'thundurus', 'landorus', 'kyurem', 'keldeo', 'meloetta', 'genesect', 'hoopa', 'volcanion',
    'diancie', 'zygarde', 'type: null', 'charjabug', 'rivals', 'hakamo-o', 'kommo-o', 'torobot', 'cosmog',
    'nihilego', 'buzzwole', 'pheromosa', 'xurkitree', 'celesteela', 'kartana', 'guzzlord', 'necrozma',
    'magearna', 'marshadow', 'poipole', 'naganadel', 'stakataka', 'blacephalon', 'zeraora', 'meltan',
    'meloetta', 'meowstic', 'aegislash', 'pumpkaboo', 'gourgeist', 'xerneas', 'yveltal', 'zygarde',
    'ho-oh', 'lugia', 'calk', 'cobalion', 'terrakion', 'virizion', 'tornadus', 'thundurus', 'landorus',
    'reshiram', 'zekrom', 'kyurem', 'latios', 'latias', 'jirachi', 'deoxys', 'wormadam', 'mothim', 'vespiquen',
    'kricketot', 'kricketune', 'shinx', 'luxio', 'luxray', 'combee', 'vespiquen', 'pachirisu', 'buizel', 'floatzel',
    'cherubi', 'cherrim', 'shellos', 'gastrodon', 'drifloon', 'drifblim', 'buneary', 'lopunny', 'glameow',
    'purugly', 'stunky', 'skuntank', 'bronzor', 'bronzong', 'gible', 'gabite', 'garchomp', 'riolu', 'lucario',
    'hippopotas', 'hippowdon', 'skorupi', 'drapion', 'croagunk', 'toxicroak', 'carnivine', 'finneon', 'lumineon',
    'snover', 'abomasnow', 'weavile', 'magnezone', 'leafeon', 'glaceon', 'glalie', 'froslass', 'rotom',
    'uxie', 'mesprit', 'azelf', 'dialga', 'palkia', 'giratina', 'cresselia', 'phione', 'manaphy', 'darkrai',
    'shaymin', 'arceus', 'victini', 'snivy', 'servine', 'serperior', 'tepig', 'pignite', 'emboar', 'oshawott',
    'dewott', 'samurott', 'patrat', 'watchog', 'lillipup', 'herdier', 'stoutland', 'purrloin', 'liepard',
    'pansage', 'simisage', 'pansear', 'simisear', 'panpour', 'simipour', 'munna', 'musharna', 'pidove',
    'tranquill', 'unfezant', 'blitzle', 'zebstrika', 'roggenrola', 'boldore', 'gigalith', 'woobat', 'swoobat',
    'drilbur', 'excadrill', 'audino', 'timburr', 'gurdurr', 'conkeldurr', 'tympole', 'palpitoad', 'seismitoad',
    'throh', 'sawk', 'sewaddle', 'swadloon', 'leavanny', 'venipede', 'whirlipede', 'scolipede', 'cottonee',
    'whimsicott', 'petilil', 'lilligant', 'basculin', 'sandile', 'krokorok', 'krookodile', 'darumaka',
    'darmanitan', 'maractus', 'dwebble', 'crustle', 'scraggy', 'scrafty', 'sigilyph', 'yamask', 'cofagrigus',
    'tirtouga', 'carracosta', 'archen', 'archeops', 'trubbish', 'garbodor', 'zorua', 'zoroark', 'minccino',
    'cinccino', 'gothita', 'gothorita', 'gothitelle', 'solosis', 'duosion', 'reuniclus', 'ducklett', 'swanna',
    'vanillite', 'vanillish', 'vanilluxe', 'deerling', 'sawsbuck', 'emolga', 'karrablast', 'escavalier',
    'foongus', 'amoonguss', 'frillish', 'jellicent', 'alomomola', 'joltik', 'galvantula', 'ferroseed',
    'ferrothorn', 'klink', 'klang', 'klinklang', 'tynamo', 'eelektrik', 'eelektross', 'elgyem', 'beheeyem',
    'litwick', 'lampent', 'chandelure', 'axew', 'fraxure', 'haxorus', 'cubchoo', 'beartic', 'cryogonal',
    'shelmet', 'accelgor', 'stunfisk', 'mienfoo', 'mienshao', 'druddigon', 'golett', 'golurk', 'pawniard',
    'bisharp', 'bouffalant', 'rufflet', 'braviary', 'vullaby', 'mandibuzz', 'heatmor', 'durant', 'deino',
    'zweilous', 'hydreigon', 'larvesta', 'volcarona', 'cobalion', 'terrakion', 'virizion', 'tornadus',
    'thundurus', 'landorus', 'zekrom', 'reshiram', 'kyurem', 'latios', 'latias', 'xerneas', 'yveltal',
    'zygarde', 'diancie', 'hoopa', 'volcanion', 'cosmog', 'nihilego', 'buzzwole', 'pheromosa', 'xurkitree',
    'kartana', 'guzzlord', 'necrozma', 'magearna', 'marshadow', 'poipole', 'naganadel', 'stakataka',
    'blacephalon', 'zeraora', 'meltan', 'melmetal',
    # Add a few common ones that might be missed
    'celebi', 'jirachi', 'shaymin', 'arceus'
}

def get_za_pokemon():
    """Get list of Pokemon available in Pokemon Legends: Z-A."""
    try:
        response = requests.get(f"{POKEAPI_BASE}/pokemon?limit=1025", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        pokemon_list = []
        for p in data['results']:
            url_parts = p['url'].rstrip('/').split('/')
            poke_id = int(url_parts[-1])
            poke_name = p['name'].lower()
            
            # Only include Pokemon in Z-A pokedex
            if poke_name in ZA_POKEDEX or poke_id <= 230:
                pokemon_list.append({
                    'id': poke_id,
                    'name': p['name'].capitalize(),
                    'sprite': get_pokemon_sprite(poke_id, shiny=False),
                    'shiny_sprite': get_pokemon_sprite(poke_id, shiny=True),
                })
        
        return pokemon_list
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Z-A Pokemon list: {e}")
        return []

# Legacy function - now returns Z-A Pokemon only
def get_all_pokemon():
    """Get list of Pokemon available in Pokemon Legends: Z-A."""
    return get_za_pokemon()

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