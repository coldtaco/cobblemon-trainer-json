import requests
from bs4 import BeautifulSoup, element
import argparse

import os

LINK_START = 'https://www.serebii.net'

IVS = {stat: 31 for stat in ['hp', 'attack', 'defence', 'special_attack', 'special_defence', 'speed']}
EVS = {stat: 31 for stat in ['hp', 'attack', 'defence', 'special_attack', 'special_defence', 'speed']}

def parse_trainer(trainer: element.Tag) -> str:
    rows = trainer.find_all('tr', recursive=False)

    pokemon, level, types, attacks, items = rows[1:6]

    print(pokemon)

    pokemon:list[str] = [p.text for p in pokemon.find_all('a')]
    level:list[int] = [int(l.text.strip('Level ')) for l in level.find_all('td', class_='level')]
    attacks:list[list[str]] = [[m.text for m in moveset.find_all('a')] for moveset in attacks.find_all('td', class_= 'bor')]
    items:list[str] = [item.text.lstrip('Hold Item:') for item in items.find_all('td', class_= 'bor')]

    j = {'team': []}

    for p, l, a, i in zip(pokemon, level, attacks, items):
        mon = {}

        is_mega = i.endswith('ite X') or i.endswith('ite Y') or i.endswith('ite')

        mon['species'] = f'cobblemon:{"mega" if is_mega else ""}{p.lower}'

        if i.endswith('ite X'):
            mon['species'] += 'x'
            
        if i.endswith('ite Y'):
            mon['species'] += 'y'

        mon['ivs'] = IVS
        mon['shiny'] = False
        if i == 'No Item':
            mon['heldItem'] = "minecraft:air"
        elif is_mega:
            mon['heldItem'] = 'cobblemon:life_orb'
        else:
            mon['heldItem'] = f'cobblemon'



def parse_links(links: list[str], save_loc: str, verbose: bool, overwrite: bool):
    os.makedirs(save_loc, exist_ok=True)

    print(links)

    for l in links:
        if not l.startswith(LINK_START):
            print(f'Link must start with {LINK_START}" {l}')
            continue
        
        filename = l.lstrip(LINK_START).rstrip('.shtml')
        filename = filename.replace('/', '.')

        content = requests.get(l).content
        soup = BeautifulSoup(content, 'html.parser')

        trainers = soup.find_all('table', class_ = 'trainer')

        for trainer in trainers:
            parse_trainer(trainer)

        exit()

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