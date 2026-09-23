"""
Serwer MCP dla Garmin Connect, skupiony na jednym celu: rozmowa o
treningach, progresji i regeneracji

Instalacja:
    pip install mcp garminconnect

Zaloguj się raz przez explore_garmin.py, żeby token zapisał się w
~/.garminconnect - ten serwer korzysta z tego samego tokenstore.

Konfiguracja Claude Desktop (claude_desktop_config.json):
    {
      "mcpServers": {
        "garmin-training": {
          "command": "python",
          "args": ["/pelna/sciezka/do/garmin_mcp_server.py"]
        }
      }
    }
"""

from datetime import date, timedelta
from pathlib import Path

import garminconnect
from mcp.server.fastmcp import FastMCP

TOKENSTORE = str(Path.home() / ".garminconnect")

mcp = FastMCP("garmin-training")

# Logowanie raz, przy starcie serwera - korzysta z zapisanego tokena,
# więc Claude Desktop odpalając ten serwer w tle nie musi pytać o hasło.
_api = garminconnect.Garmin()
_api.login(TOKENSTORE)


def _today(day: str) -> str:
    return day or date.today().isoformat()


# --- Aktywności ---------------------------------------------------

@mcp.tool()
def list_recent_activities(count: int = 10) -> list:
    """
    Zwraca listę ostatnich aktywności (bieganie, rower, siłownia itp.)
    z podstawowymi metrykami: dystans, czas, tempo, śr. tętno, kalorie.
    Dobre wejście do pytań o progresję w czasie.

    Args:
        count: ile ostatnich aktywności zwrócić (domyślnie 10).
    """
    return _api.get_activities(0, count)


@mcp.tool()
def get_activity_details(activity_id: int) -> dict:
    """
    Zwraca pełne szczegóły jednej aktywności: splity/laps, strefy
    tętna, elevation, kadencję itp. Użyj activity_id z
    list_recent_activities, gdy trzeba wejść głębiej w konkretny
    trening zamiast tylko jego podsumowania.

    Args:
        activity_id: ID aktywności (pole "activityId" z listy).
    """
    return _api.get_activity(activity_id)


# --- Status treningowy i progresja --------------------------------

@mcp.tool()
def get_training_status(day: str = "") -> dict:
    """
    Aktualny status treningowy: acute/chronic training load, balans
    obciążenia (czy trenujesz produktywnie, utrzymujesz formę, czy
    jest ryzyko przetrenowania), trend VO2max. Główne narzędzie do
    pytań typu "jak wygląda moja progresja / czy trenuję za dużo".

    Args:
        day: data YYYY-MM-DD. Puste = dziś.
    """
    return _api.get_training_status(_today(day))


@mcp.tool()
def get_training_readiness(day: str = "") -> dict:
    """
    Training Readiness - ile jesteś dziś gotowy na wysiłek, złożone
    ze snu, HRV, poprzedniego obciążenia i stresu. Główne narzędzie
    do pytań o odpoczynek/regenerację i czy dziś trenować czy odpuścić.

    Args:
        day: data YYYY-MM-DD. Puste = dziś.
    """
    return _api.get_training_readiness(_today(day))


@mcp.tool()
def get_fitness_metrics(day: str = "") -> dict:
    """
    VO2max (bieganie i rower) oraz wiek fitness (fitness age).
    Metryki długoterminowej progresji formy.

    Args:
        day: data YYYY-MM-DD. Puste = dziś.
    """
    return _api.get_max_metrics(_today(day))


@mcp.tool()
def get_race_predictions() -> dict:
    """
    Przewidywane czasy na 5K/10K/półmaraton/maraton na podstawie
    aktualnej formy. Dobre do pytań "na co mnie dziś stać".
    """
    return _api.get_race_predictions()


@mcp.tool()
def get_personal_records() -> list:
    """
    Rekordy życiowe: najszybsze czasy, najdłuższe dystanse/czasy,
    najwięcej kroków. Punkt odniesienia do progresji.
    """
    return _api.get_personal_records()


# --- Regeneracja: sen, HRV, stres, energia -------------------------

@mcp.tool()
def get_sleep(day: str = "") -> dict:
    """
    Szczegóły snu: fazy (głęboki/lekki/REM), czas trwania, ocena snu,
    SpO2 w trakcie nocy. Kluczowe dla pytań o regenerację.

    Args:
        day: data YYYY-MM-DD. Puste = dziś.
    """
    return _api.get_sleep_data(_today(day))


@mcp.tool()
def get_hrv(day: str = "") -> dict:
    """
    Heart Rate Variability - średnia z nocy, status względem
    baseline. Jeden z głównych wskaźników regeneracji/przetrenowania.

    Args:
        day: data YYYY-MM-DD. Puste = dziś.
    """
    return _api.get_hrv_data(_today(day))


@mcp.tool()
def get_stress(day: str = "") -> dict:
    """
    Poziom stresu w ciągu dnia (skala 0-100, rozbity na okresy).
    Pomaga ocenić obciążenie poza samym treningiem.

    Args:
        day: data YYYY-MM-DD. Puste = dziś.
    """
    return _api.get_stress_data(_today(day))


@mcp.tool()
def get_body_battery(start_day: str = "", end_day: str = "") -> list:
    """
    Poziom "baterii energii" w zadanym zakresie dat - jak szybko się
    ładuje/rozładowuje w ciągu dnia. Dobre do korelacji z jakością
    snu i intensywnością treningów.

    Args:
        start_day: data początkowa YYYY-MM-DD. Puste = 7 dni temu.
        end_day: data końcowa YYYY-MM-DD. Puste = dziś.
    """
    end_day = _today(end_day)
    start_day = start_day or (date.today() - timedelta(days=7)).isoformat()
    return _api.get_body_battery(start_day, end_day)


@mcp.tool()
def get_daily_summary(day: str = "") -> dict:
    """
    Ogólne podsumowanie dnia: kroki, kalorie, resting heart rate,
    minuty aktywności. Dobry punkt wyjścia zanim wejdzie się w
    szczegółowe narzędzia powyżej.

    Args:
        day: data YYYY-MM-DD. Puste = dziś.
    """
    return _api.get_stats(_today(day))


if __name__ == "__main__":
    mcp.run(transport="stdio")
