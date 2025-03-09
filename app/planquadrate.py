import os
import json
from nicegui import ui, app
import asyncio
from dotenv import load_dotenv, set_key, find_dotenv

from app.menu import menu

dotenv_file = find_dotenv()
load_dotenv(dotenv_file)

KOMMUNE_ID_KEY = 'KOMMUNE_ID'
kommune_details: dict = {}
kommunen: dict = {}

# Lese GEOjson und entnehme enthaltene Gemeinden
async def lese_geojson() -> dict:
    global kommunen
    geoJson = json.load(open(os.path.join('data', 'gemeinden_simplify200.geojson')))
    for element in geoJson['features']:
        kommunen[element['properties']['AGS']] = element['properties']['GEN']

app.on_startup(lese_geojson)

# Extrahiere daten zur Kommunalen Grenze
async def entnehme_kommunen_details(kommune_id: str) -> None:
    geoJson = json.load(open(os.path.join('data', 'gemeinden_simplify200.geojson')))
    for element in geoJson['features']:
        if element['properties']['AGS'] == kommune_id:
            global kommune_details
            kommune_details = element
            ui.notify('Gemeindedetails geladen.', type='positive')
            return
    ui.notify('Gemeindedetails konnten nicht geladen werden.', type='warning')

async def speicher_env(key: str, value) -> None:
    os.environ[key] = value
    set_key(dotenv_file, key, value)
    return
    

@ui.refreshable
async def details_kommune() -> None:
    def get_ags(name: str) -> str:
        return list(kommunen.keys())[list(kommunen.values()).index(name)]
    
    async def speicher_id(kommune_name: str) -> None:
        kommune_id = get_ags(kommune_name)
        if os.environ[KOMMUNE_ID_KEY] != kommune_id:
            ui.notify(f'Gemeindeschlüssel {kommune_id} gespeichert', type='positive')
            input_ags.set_value(kommune_id)
            await speicher_env(KOMMUNE_ID_KEY, kommune_id)
            await entnehme_kommunen_details(kommune_id)
                        
    
    kommune_id = os.environ[KOMMUNE_ID_KEY]
    kommune_name = kommunen[kommune_id]
    with ui.row(align_items='center'):
        input_name = ui.input('Name der Gemeinde', value=kommune_name, autocomplete=list(kommunen.values()))
        ui.button(icon='save', on_click=lambda: speicher_id(input_name.value))
    input_ags = ui.input('Gemeindeschlüssel', value=kommune_id)
    input_ags.disable()

@ui.page('/planquadrate')
async def planquadrate() -> None:
    menu('Planquadrate')
    await details_kommune()
    # await entnehme_kommunen_details()