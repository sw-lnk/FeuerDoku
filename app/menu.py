from nicegui import ui
import toml

with open('pyproject.toml', 'r') as f:
    config = toml.load(f)

def menu(titel: str = 'FeuerOrga') -> None:
    ''' Navigationsmenü '''
    # ui.colors(primary='#d63031')
    with ui.header():
        ui.label(titel).classes('text-2xl').classes('mr-auto')
        with ui.button(icon='menu'):
            with ui.menu() as menu:
                ui.menu_item('Startseite', on_click=lambda:ui.navigate.to('/'))
                ui.menu_item('Planquadrate', on_click=lambda:ui.navigate.to('/planquadrate'))
                ui.separator()
                ui.menu_item('Close', menu.close)
    
    with ui.footer():
        ui.label(f'Version {config['project']['version']}')
