# Project
# Medical Patient Data Analyzer

Aplikacja do analizy danych medycznych pacjentów. Działa w przeglądarce. Można w niej wczytać plik CSV z danymi, przefiltrować je, zobaczyć statystyki i wykresy, a na końcu pobrać wyniki jako CSV lub raport PDF.

## Dane

Dane pochodzą z Kaggle:  
https://www.kaggle.com/datasets/nasirayub2/human-vital-sign-dataset/data

Aplikacja korzysta z kolumn: ID pacjenta, wiek, płeć, waga, wzrost, tętno, częstość oddechów, ciśnienie skurczowe i rozkurczowe.

BMI i grupa wiekowa są wyliczane automatycznie po załadowaniu pliku.

## Co trzeba mieć zainstalowane

- Python 3.10 lub nowszy
- Biblioteki: streamlit, pandas, numpy, matplotlib, reportlab

## Jak uruchomić

Pobierz projekt:

```
https://github.com/grabowskasia/Project.git
```

Zainstaluj biblioteki:

```
pip install -r requirements.txt
```

Uruchom:

```
streamlit run Project.py
```

Powinna otworzyć się przeglądarka z aplikacją pod adresem `http://localhost:8501`.

Jeśli nie — wklej ten adres ręcznie w przeglądarkę.

**Ważne:** nie uruchamiaj przez `python Project.py` — to nie zadziała. Streamlit wymaga komendy `streamlit run`.

## Jak używać

1. Kliknij **Browse files** i wybierz plik CSV (np. `Changed_data.csv`).
2. Po lewej stronie pojawią się suwaki do filtrowania danych (wiek, tętno, ciśnienie, BMI itd.).
3. Na górze są zakładki:
   - **Dane** — tabela ze wszystkimi przefiltrowanymi danymi
   - **Statystyki** — średnia, mediana, odchylenie i inne, też w podziale na grupy
   - **Wykresy** — histogram, wykres rozrzutu, boxplot, wykres kołowy
   - **Porównanie grup** — porównanie parametrów między grupami (np. mężczyźni vs kobiety)
   - **Eksport** — pobieranie danych jako CSV albo generowanie raportu PDF

## Co robi aplikacja

- Wczytuje dane z pliku CSV
- Filtruje po płci, wieku, tętnie, oddechach, ciśnieniu i BMI
- Liczy statystyki: średnia, mediana, odchylenie standardowe, kwartyle
- Grupuje dane np. po płci albo grupie wiekowej i liczy statystyki osobno
- Rysuje wykresy: histogram, scatter, boxplot, wykres kołowy
- Porównuje grupy pacjentów na boxplotach obok siebie
- Eksportuje przefiltrowane dane do CSV
- Generuje raport PDF z tabelami i wykresami
- Działa nawet jeśli w pliku CSV brakuje niektórych kolumn

## Pliki w projekcie

```
medical-analyzer/
├── Project.py              # Główny plik aplikacji
├── human_vital_signs_dataset_2024.csv        # Dane pacjentów
├── requirements.txt        # Lista bibliotek do zainstalowania
└── README.md
```

## Czego użyto (biblioteki)

- **Streamlit** — interfejs w przeglądarce
- **Pandas** — praca z danymi (wczytywanie, filtrowanie, obliczenia)
- **Matplotlib** — rysowanie wykresów
- **ReportLab** — tworzenie plików PDF