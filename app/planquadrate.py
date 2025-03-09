import os
import json
from nicegui import ui, app
import folium
from dotenv import load_dotenv, set_key, find_dotenv

from app.menu import menu

dotenv_file = find_dotenv()
load_dotenv(dotenv_file)

KOMMUNE_ID_KEY = 'KOMMUNE_ID'

kommune_details: dict = {}
kommunen: dict = {}

async def lese_geojson() -> dict:
    # Lese GEOjson und entnehme enthaltene Gemeinden
    global kommunen
    geoJson = json.load(open(os.path.join('data', 'gemeinden_simplify200.geojson')))
    for element in geoJson['features']:
        kommunen[element['properties']['AGS']] = element['properties']['GEN']
app.on_startup(lese_geojson)

def entnehme_kommunen_details(kommune_id: str = None, info: bool = True) -> None:
    # Extrahiere daten zur Kommunalen Grenze
    if not kommune_id: kommune_id = os.environ[KOMMUNE_ID_KEY]
    geoJson = json.load(open(os.path.join('data', 'gemeinden_simplify200.geojson')))
    for element in geoJson['features']:
        if element['properties']['AGS'] == kommune_id:
            global kommune_details
            kommune_details = element
            if info: ui.notify('Gemeindedetails geladen.', type='positive')
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
        kommune_name = kommune_name.strip().capitalize()
        kommune_id = get_ags(kommune_name)
        if os.environ[KOMMUNE_ID_KEY] != kommune_id:
            ui.notify(f'Gemeindeschlüssel {kommune_id} gespeichert', type='positive')
            input_ags.set_value(kommune_id)
            input_name.set_value(kommune_name)
            await speicher_env(KOMMUNE_ID_KEY, kommune_id)
            entnehme_kommunen_details(kommune_id)
            landkarte.refresh()
                        
    kommune_id = os.environ[KOMMUNE_ID_KEY]
    kommune_name = kommunen[kommune_id]
    with ui.row(align_items='center'):
        optionen = list(kommunen.values())
        input_name = ui.input(
            label='Name der Gemeinde',
            value=kommune_name,
            autocomplete=optionen,
            validation=lambda value: 'Nicht vorhanden' if not str(value).strip().capitalize() in optionen else None
            )
        ui.button(icon='save', on_click=lambda: speicher_id(input_name.value))
    input_ags = ui.input('Gemeindeschlüssel', value=kommune_id)
    input_ags.disable()

@ui.refreshable
async def landkarte() -> None:
    if kommune_details.get('properties'):
        center = (
            float(kommune_details['properties']['destatis']['center_lat'].replace(',', '.')),
            float(kommune_details['properties']['destatis']['center_lon'].replace(',', '.'))
            )
        m = ui.leaflet(center=center, zoom=12, options={'minZoom':6, 'maxZoom':15}).classes('h-96')
        name = str(kommune_details["geometry"]["type"]).lower()
        coords = [(p[1], p[0]) for p in kommune_details["geometry"]["coordinates"][0]]
        m.generic_layer(name=name, args=[coords, {'color':'black', 'fillColor':'#00000000', 'weight':1}])
        #TODO: fit bounds: https://github.com/zauberzeug/nicegui/issues/2500

@ui.page('/planquadrate')
async def planquadrate() -> None:
    menu('Planquadrate')
    await details_kommune()
    entnehme_kommunen_details(info=False)
    await landkarte()
    