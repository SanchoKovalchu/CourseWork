from nicegui import ui

def menu() -> None:
    ui.link('Home', '/').classes(replace='text-white')
    ui.link('Projects', '/projects').classes(replace='text-white')
