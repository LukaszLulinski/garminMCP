"""
Prosty skrypt do zabawy z python-garminconnect.
Cel: zalogować się i zobaczyć, jak wyglądają surowe dane z różnych endpointów.

Instalacja:
    pip install garminconnect

Pierwsze uruchomienie zapyta o email/hasło (i kod MFA, jeśli masz włączone).
Token zostanie zapisany w ~/.garminconnect, więc kolejne uruchomienia
nie będą wymagały ponownego logowania.
"""

import json
import os
from datetime import date, timedelta
from getpass import getpass
from pathlib import Path

import garminconnect
from garminconnect import GarminConnectTooManyRequestsError

TOKENSTORE = str(Path.home() / ".garminconnect")


def init_api():
    """
    Jedna, czysta próba logowania — bez podwójnych requestów, żeby nie
    łapać 429 od Garmina. Jeśli w TOKENSTORE są ważne tokeny, login()
    użyje ich bez pytania o hasło. Jeśli nie — poprosi o email/hasło
    i (jeśli masz 2FA) o kod MFA.
    """
    email = os.getenv("GARMIN_EMAIL") or input("Garmin email: ")
    password = os.getenv("GARMIN_PASSWORD") or getpass("Garmin hasło: ")

    api = garminconnect.Garmin(
        email=email,
        password=password,
        prompt_mfa=lambda: input("Kod MFA (z aplikacji/SMS-a): ").strip(),
    )
    try:
        api.login(TOKENSTORE)
        print(f"✅ Zalogowano. Token zapisany w {TOKENSTORE}\n")
        return api
    except GarminConnectTooManyRequestsError as e:
        print(
            f"\n❌ Garmin zablokował logowania z tego IP na jakiś czas: {e}\n"
            "Odczekaj przynajmniej 30–60 minut (czasem dłużej) i spróbuj"
            " ponownie — NIE odpalaj skryptu kilka razy pod rząd, bo to"
            " tylko wydłuża blokadę."
        )
        raise


def show(label, data):
    """Ładnie wypisuje dane (albo ich fragment, jeśli są duże)."""
    print(f"\n{'=' * 60}\n{label}\n{'=' * 60}")
    text = json.dumps(data, indent=2, ensure_ascii=False, default=str)
    if len(text) > 2000:
        print(text[:2000] + "\n... [obcięte, całość jest dużo dłuższa] ...")
    else:
        print(text)


def main():
    api = init_api()

    today = date.today().isoformat()
    week_ago = (date.today() - timedelta(days=7)).isoformat()

    # Podstawowe info o koncie
    show("Pełne imię i nazwisko", api.get_full_name())
    show("Statystyki dnia dzisiejszego", api.get_stats(today))

    # Sen
    show("Dane o śnie (dziś)", api.get_sleep_data(today))

    # Tętno
    show("Tętno (dziś)", api.get_heart_rates(today))

    # HRV
    try:
        show("HRV (dziś)", api.get_hrv_data(today))
    except Exception as e:
        print(f"\nHRV niedostępne: {e}")

    # Stres
    show("Stres (dziś)", api.get_stress_data(today))

    # Body Battery
    show("Body Battery (dziś)", api.get_body_battery(week_ago, today))

    # Lista aktywności (ostatnie 5)
    show("Ostatnie 5 aktywności", api.get_activities(0, 5))

    print(
        "\n\nTo tylko wycinek tego, co oferuje biblioteka — obiekt `api` ma"
        " ~100 metod (get_weight, get_training_readiness, get_spo2_data,"
        " get_vo2max, get_devices, ...). Odpal `demo.py` z repo"
        " cyberjunky/python-garminconnect, żeby przeklikać wszystkie."
    )


if __name__ == "__main__":
    main()
