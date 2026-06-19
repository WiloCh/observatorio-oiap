from collections.abc import Callable

from src.ui.pages.alerts import render_alerts_page
from src.ui.pages.dashboard import render_dashboard_page
from src.ui.pages.database_view import render_database_view_page
from src.ui.pages.home import render_home_page
from src.ui.pages.manual_entry import render_manual_entry_page
from src.ui.pages.reports import render_reports_page
from src.ui.pages.upload import render_upload_page
from src.ui.pages.users import render_users_page


PAGE_RENDERERS: dict[str, Callable[[], None]] = {
    "Inicio": render_home_page,
    "Cargar datos": render_upload_page,
    "Registro manual": render_manual_entry_page,
    "Dashboard": render_dashboard_page,
    "Base de datos": render_database_view_page,
    "Usuarios": render_users_page,
    "Alertas": render_alerts_page,
    "Reportes": render_reports_page,
}

NAVIGATION_GROUPS: dict[str, list[str]] = {
    "Navegación": [
        "Inicio",
        "Cargar datos",
        "Registro manual",
        "Dashboard",
        "Base de datos",
        "Usuarios",
    ],
    "Herramientas": [
        "Alertas",
        "Reportes",
    ],
}
