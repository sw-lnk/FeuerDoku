from nicegui import app, ui

from app.menu import menu
from app.planquadrate import planquadrate     

@ui.page('/')
def index() -> None:
    ''' Startseite '''
    menu()
    ui.label('Startseite').classes('text-2xl')
    
ui.run()