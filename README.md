# garmin-training-mcp

Lokalny serwer MCP wystawiający dane z Garmin Connect (treningi,
progresja, regeneracja) jako narzędzia dla Claude Desktop. Zamiast
150+ metod z `python-garminconnect`, ten serwer eksponuje tylko te,
które są istotne do rozmowy o formie i odpoczynku.

## Zawartość repo

| Plik | Do czego |
|---|---|
| `explore_garmin.py` | Skrypt do ręcznej zabawy z API — logowanie, podgląd surowych danych (JSON) z kilku endpointów. Uruchom go **najpierw**, żeby zapisać token logowania. |
| `garmin_mcp_server.py` | Właściwy serwer MCP, podpinany do Claude Desktop. |

## Wymagania

- Python 3.10+
- Konto Garmin Connect
- Claude Desktop

## Instalacja

```bash
pip install mcp garminconnect
```

## Krok 1 — pierwsze logowanie

Zanim podepniesz serwer MCP, zaloguj się raz ręcznie:

```bash
python3 explore_garmin.py
```

Poda Cię o email, hasło i (jeśli masz 2FA) kod MFA. Po udanym
logowaniu token zapisuje się w `~/.garminconnect` i kolejne
uruchomienia — zarówno tego skryptu, jak i serwera MCP — będą go
używać bez ponownego pytania o hasło.

> **Uwaga na rate limiting.** Garmin potrafi zablokować logowania z
> danego IP na jakiś czas (błąd `429 GarminConnectTooManyRequestsError`).
> Jeśli to się zdarzy: **nie** odpalaj skryptu w kółko — to tylko
> wydłuża blokadę. Odczekaj 30–60 minut (czasem dłużej) i spróbuj
> jeszcze raz, tym razem tylko jeden raz.

## Krok 2 — podpięcie do Claude Desktop

Otwórz plik konfiguracyjny:

- **Linux**: `~/.config/Claude/claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

i dodaj wpis (z pełną, absolutną ścieżką do pliku na Twoim dysku):

```json
{
  "mcpServers": {
    "garmin-training": {
      "command": "python3",
      "args": ["/pelna/sciezka/do/garmin_mcp_server.py"]
    }
  }
}
```

Zapisz plik i **zrestartuj Claude Desktop**. Po restarcie narzędzia
z serwera powinny pojawić się automatycznie w rozmowie.

## Dostępne narzędzia

### Aktywności

| Narzędzie | Opis |
|---|---|
| `list_recent_activities(count)` | Lista ostatnich aktywności: dystans, czas, tempo, śr. tętno, kalorie |
| `get_activity_details(activity_id)` | Pełne szczegóły jednej aktywności: splity, strefy tętna, kadencja |

### Status treningowy i progresja

| Narzędzie | Opis |
|---|---|
| `get_training_status(day)` | Acute/chronic training load, balans obciążenia, trend VO2max |
| `get_training_readiness(day)` | Gotowość na dzisiejszy wysiłek (sen + HRV + obciążenie + stres) |
| `get_fitness_metrics(day)` | VO2max (bieg/rower), fitness age |
| `get_race_predictions()` | Przewidywane czasy 5K/10K/półmaraton/maraton |
| `get_personal_records()` | Rekordy życiowe |

### Regeneracja

| Narzędzie | Opis |
|---|---|
| `get_sleep(day)` | Fazy snu, czas trwania, ocena, SpO2 w nocy |
| `get_hrv(day)` | HRV — średnia z nocy i status względem baseline |
| `get_stress(day)` | Poziom stresu w ciągu dnia |
| `get_body_battery(start_day, end_day)` | Poziom energii w zadanym zakresie dat |
| `get_daily_summary(day)` | Kroki, kalorie, resting HR, minuty aktywności |

Wszystkie parametry dat są w formacie `YYYY-MM-DD` i domyślnie
puste = dziś (poza `get_body_battery`, gdzie domyślny zakres to
ostatnie 7 dni).

## Rozwiązywanie problemów

**`GarminConnectAuthenticationError: ... MFA Required`**
Upewnij się, że logujesz się przez `explore_garmin.py` (ma
skonfigurowany `prompt_mfa`), a nie bezpośrednio przez serwer MCP.

**Serwer MCP nie startuje / Claude Desktop pokazuje błąd**
Najczęstsza przyczyna: brak zapisanego tokenu w `~/.garminconnect`.
Serwer loguje się bez hasła, zakładając że token już istnieje —
uruchom najpierw `explore_garmin.py`.

**Narzędzie zwraca pustkę albo `AttributeError`**
Niektóre metryki (VO2max, race predictions, SpO2) wymagają
kompatybilnego zegarka i/lub wystarczającej liczby zarejestrowanych
aktywności. Pusty wynik często oznacza po prostu brak danych na
Twoim koncie, nie błąd w kodzie.

**`429 GarminConnectTooManyRequestsError`**
Rate limit po stronie Garmina. Odczekaj i nie ponawiaj prób w kółko
— patrz sekcja "Krok 1" wyżej.
