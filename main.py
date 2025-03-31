import json
import random
import re
import requests
from bs4 import BeautifulSoup, element
import argparse

import os

LINK_START = 'https://bulbapedia.bulbagarden.net/'

IVS = {stat: 31 for stat in ['hp', 'attack', 'defence', 'special_attack', 'special_defence', 'speed']}
EVS = {stat: 510//6 for stat in ['hp', 'attack', 'defence', 'special_attack', 'special_defence', 'speed']}

# def parse_trainer(trainer: element.Tag) -> str:
#     rows = trainer.find_all('tr', recursive=False)

#     pokemon, level, types, attacks, items = rows[1:6]

#     print(pokemon)

#     pokemon:list[str] = [p.text for p in pokemon.find_all('a')]
#     level:list[int] = [int(l.text.strip('Level ')) for l in level.find_all('td', class_='level')]
#     attacks:list[list[str]] = [[m.text for m in moveset.find_all('a')] for moveset in attacks.find_all('td', class_= 'bor')]
#     items:list[str] = [item.text.lstrip('Hold Item:') for item in items.find_all('td', class_= 'bor')]

#     j = {'team': []}

#     for p, l, a, i in zip(pokemon, level, attacks, items):
#         mon = {}

#         is_mega = i.endswith('ite X') or i.endswith('ite Y') or i.endswith('ite')

#         mon['species'] = f'cobblemon:{"mega" if is_mega else ""}{p.lower}'

#         if i.endswith('ite X'):
#             mon['species'] += 'x'
            
#         if i.endswith('ite Y'):
#             mon['species'] += 'y'

#         mon['ivs'] = IVS
#         mon['shiny'] = False
#         if i == 'No Item':
#             mon['heldItem'] = "minecraft:air"
#         elif is_mega:
#             mon['heldItem'] = 'cobblemon:life_orb'
#         else:
#             mon['heldItem'] = f'cobblemon'

def snake_case(s: str) -> str:
    return '_'.join([word.lower() for word in s.split(" ")])

def lowercase_nospace(s: str) -> str:
    s = re.sub('[^a-zA-Z0-9 \n\.]', '', s)
    return s.replace(' ', '').replace('-', '').replace('_', '').lower()

def get_pokemon_value(content:str, key:str, end = '\n') -> str:
    return re.search(f'{key}=.+?{end}', content)[0].lstrip(f'{key}=').rstrip(end)

def parse_trainer(content:list[str]):
    trainer_name = content[0].strip().strip('=')

    pokemons = ''.join(content).split('{{Pokémon')

    result = []

    for pokemon in pokemons[1:]:
        species = get_pokemon_value(pokemon, 'pokemon')
        
        gender = 'GENDERLESS'
        if 'gender' in pokemon:
            gender = get_pokemon_value(pokemon, 'gender')
            gender = random.choice(['MALE', 'FEMALE']) if gender == 'both' else gender.upper()

        level = int(get_pokemon_value(pokemon, 'level'))
        ability = get_pokemon_value(pokemon, 'ability')
        if '|' in ability:
            abilities = [a.split('=')[-1] for a in ability.split('|')]
            ability = lowercase_nospace(random.choice(abilities))
        item = get_pokemon_value(pokemon, 'held')

        moves = [get_pokemon_value(pokemon, f'move{i}', '\|').lower() for i in range(1, 5)]
        moves = [lowercase_nospace(m) for m in moves]

        is_mega = item.endswith('ite X') or item.endswith('ite Y') or item.endswith('ite')
        mon = {}
        mon['species'] = f'cobblemon:{"mega" if is_mega else ""}{lowercase_nospace(species)}'

        if item.endswith('ite X'):
            mon['species'] += 'x'
            
        if item.endswith('ite Y'):
            mon['species'] += 'y'

        mon['gender'] = gender
        mon['level'] = level
        mon['nature'] = 'cobblemon:hardy'
        mon['ability'] = lowercase_nospace(ability)
        mon['moveset'] = moves
        mon['ivs'] = IVS
        mon['evs'] = EVS
        mon['shiny'] = False

        if item == 'No Item':
            mon['heldItem'] = "minecraft:air"
        elif is_mega:
            mon['heldItem'] = 'cobblemon:life_orb'
        else:
            item = snake_case(item).replace("'", '')
            mon['heldItem'] = f'cobblemon:{item}'
        
        result.append(mon)
    
    return trainer_name, {"team": result}

def parse_links(sources: list[str], save_loc: str, verbose: bool, overwrite: bool):
    os.makedirs(save_loc, exist_ok=True)

    for source in sources:
        with open(source, 'r', encoding="utf8") as f:
            content = f.readlines()

        trainers = []
        party_info = []
        reading = False
        for line in content:
            if line.startswith('==='):
                reading = True
            if line.startswith('{{Party/Footer}}'):
                reading = False
                trainers.append(party_info)
                party_info = []

            if reading:
                party_info.append(line)
        
        for content in trainers[1:]:
            name, team = parse_trainer(content)

            with open(os.path.join(save_loc, f'{name}.json'), 'w') as f:
                json.dump(team, f, indent=4)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                        prog='CobblemonTrainerJSON',
                        description='Grabs trainer data from serebii and dumps them into json')
    
    parser.add_argument('-l', '--links', nargs= '+')
    parser.add_argument('-s', '--save_loc', nargs=1, default= 'trainers')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-o', '--overwrite', action='store_true')

    args = parser.parse_args()
    links = args.links
    save_loc = args.save_loc
    verbose = args.verbose
    overwrite = args.overwrite
    parse_links(links, save_loc, verbose, overwrite)