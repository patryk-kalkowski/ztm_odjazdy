
# <img src="brand/icon.png" width="35" height="35" style="vertical-align: middle;"> ZTM Gdańsk - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub Release](https://img.shields.io/github/release/patryk-kalkowski/ztm_odjazdy.svg)](https://github.com/patryk-kalkowski/ztm_odjazdy/releases)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/patryk-kalkowski/ztm_odjazdy/graphs/commit-activity)


![CARD_EXAMPLE](https://raw.githubusercontent.com/patryk-kalkowski/ztm_odjazdy/main/brand/card_example.png)

## Funkcje

- **Śledzenie odjazdów w czasie rzeczywistym** - dane z oficjalnego  [API ZTM Gdańsk](https://ckan.multimediagdansk.pl/dataset/tristar).


## Instalacja

### HACS (Rekomendowane)

1. Otwórz HACS w Home Assistant
2. Kliknij na "Menu"
3. Kliknij menu w prawym górnym rogu i wybierz "Custom repositories"
4. Dodaj URL: `https://github.com/patryk-kalkowski/ztm_odjazdy`
5. Kategoria: `Integration`
6. Kliknij "Add"
7. Znajdź "ZTM Odjazdy" na liście i kliknij "Download"
8. Zrestartuj Home Assistant

### Instalacja manualna

1. Skopiuj folder `custom_components/ztmodjazdy` do katalogu `custom_components` w Twojej instalacji Home Assistant
2. Zrestartuj Home Assistant

## Konfiguracja

1. Przejdź do **Ustawienia** → **Urządzenia i usługi**
2. Kliknij przycisk **+ DODAJ INTEGRACJĘ**
3. Wyszukaj **ZTM Odjazdy**
4. Postępuj zgodnie z instrukcjami w kreatorze konfiguracji:
   - **Wybierz przystanek**: Lista przystanków pobierana z API ZTM
   - **Filtruj linie** (opcjonalne): Lista linii oddzielona średnikami (np. `2;11;115`)
   - **Interwał odświeżania**: Częstotliwość aktualizacji w minutach (domyślnie, minimalnie: 1)
   - **Odjazdy w ciągu**: Maksymalny czas do odjazdu w minutach (domyślnie: 50)

## Przykład użycia w Lovelace


### Custom Flex Table Card (Rekomendowane)

```yaml
type: custom:flex-table-card
entities:
  - sensor.piotrkowska_03
  - sensor.piotrkowska_01
sort_by: czas
strict: true
css:
  tbody td:
    padding: 2px 8px
    font-size: 14px
    border-bottom: 1px solid rgba(127,127,127,0.18)
  tbody tr:nth-child(even):
    background: rgba(127,127,127,0.06)
columns:
  - name: Linia
    data: odjazdy
    align: center
    modify: |
      (() => {
        const line = String(x.linia);
        const map = { '2': '#729ddb', '11': '#48648c', '115': '#2F7D6D', '174': '#1b4d42' };
        let color = map[line] || `hsl(${Math.abs(line.split('').reduce((a,b)=>(((a<<5)-a)+b.charCodeAt(0)),0)) % 360} 28% 38%)`;
        return `<span style="display:inline-block; min-width:2.8em; text-align:center; padding: 2px 8px; border-radius:99px; background:${color}; color:white; font-weight:700;">${line}</span>`;
      })()
  - name: Kierunek
    data: odjazdy
    modify: x.kierunek
  - name: Godz.
    data: odjazdy
    align: center
    modify: >-
      new
      Date(x.czas).toLocaleTimeString('pl-PL',{hour:'2-digit',minute:'2-digit'})
  - name: Za
    data: odjazdy
    align: right
    modify: |
      (() => {
        const min = Math.max(0, Math.round((new Date(x.czas) - new Date()) / 60000));
        return min <= 0 ? 'teraz' : `${min} min`;
      })()
  - name: czas
    data: odjazdy
    modify: x.czas
    hidden: true
```

## 📈 Atrybuty sensora

Każdy sensor ZTM Odjazdy udostępnia następujące atrybuty:

| Atrybut | Opis |
|---------|------|
| `stop_id` | Identyfikator przystanku |
| `nazwa_przystanku` | Przyjazna nazwa przystanku |
| `limit_minut` | Maksymalny czas do odjazdu (w minutach) |
| `odjazdy` | Lista odjazdów z szczegółami |
| `ostatnia_aktualizacja` | Czas ostatniej aktualizacji |

### Struktura obiektu `odjazdy`:

```json
{
  "linia": "11",
  "kierunek": "Siedlce",
  "czas": "2026-05-04T14:30:00Z",
  "minuty": 5
}
```


## Podziękowania

- Dane dostarczane przez [API ZTM Gdańsk](https://ckan.multimediagdansk.pl/dataset/tristar)


## Wsparcie projektu

Jeśli podoba Ci się ta integracja, zostaw gwiazdkę na GitHub!
