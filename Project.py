import io
import os
import datetime
import tempfile

import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

#Poprawic komentarze do funkcji

# Dane które nas interesują
COLUMNS_TO_KEEP = [
    "Patient ID", "Age", "Gender",
    "Weight (kg)", "Height (m)",
    "Heart Rate", "Respiratory Rate",
    "Systolic Blood Pressure", "Diastolic Blood Pressure",
]

NUMERIC_COLUMNS = [
    "Age", "Weight (kg)", "Height (m)",
    "Heart Rate", "Respiratory Rate",
    "Systolic Blood Pressure", "Diastolic Blood Pressure", "BMI"
]

SLIDER_CONFIG = {
    "Age":                      ("Wiek", 0, 120),
    "Heart Rate":               ("Tętno", 0, 300),
    "Respiratory Rate":         ("Częstość oddechów", 0, 60),
    "Systolic Blood Pressure":  ("Ciśnienie skurczowe", 0, 300),
    "Diastolic Blood Pressure": ("Ciśnienie rozkurczowe", 0, 200),
}

POLISH_NAMES = {
    "Patient ID":               "ID pacjenta",
    "Age":                      "Wiek",
    "Gender":                   "Płeć",
    "Weight (kg)":              "Waga (kg)",
    "Height (m)":               "Wzrost (m)",
    "Heart Rate":               "Tętno",
    "Respiratory Rate":         "Częstość oddechów",
    "Systolic Blood Pressure":  "Ciśnienie skurczowe",
    "Diastolic Blood Pressure": "Ciśnienie rozkurczowe",
    "BMI":                      "BMI",
}

def polish(column_name):
    return POLISH_NAMES.get(column_name, column_name)

def load_csv(uploaded_file):
    # Wczytuje dane z pliku CSV, wybiera dane z "COLUMNS_TO_KEEP"
    # Usuwa duplikaty, oblicza BMI i sortuje bo dacie

    patient_data = pd.read_csv(uploaded_file)
    available_columns = [col for col in COLUMNS_TO_KEEP if col in patient_data.columns]
    patient_data = patient_data[available_columns].copy()

    # Sprawdzanie obecności duplikatów
    if "Patient ID" in patient_data.columns:
        patient_data.drop_duplicates(subset=["Patient ID"], keep="first", inplace=True)
        patient_data.reset_index(drop=True, inplace=True)

    # Obliczanie BMI
    if "Weight (kg)" in patient_data.columns and "Height (m)" in patient_data.columns:
        patient_data["BMI"] = (
            patient_data["Weight (kg)"] / (patient_data["Height (m)"] ** 2)
        ).round(1)

    # Dzielenie na grupy wiekowe
    if "Age" in patient_data.columns:
        age_bins = [0, 18, 30, 45, 60, 120]
        age_labels = ["<18", "18-30", "31-45", "46-60", "60+"]
        patient_data["Grupa wiekowa"] = pd.cut(
            patient_data["Age"], bins=age_bins, labels=age_labels, right=True
        )

    return patient_data

def get_available_numeric_columns(patient_data):
    return [col for col in NUMERIC_COLUMNS if col in patient_data.columns]

def compute_stats(patient_data, column_name):
    # Oblicza statystyki dla danej kolumny, usuwa niepoprawne dane

    column_values = patient_data[column_name].dropna()
    stats = {
        "Średnia": column_values.mean(),
        "Mediana": column_values.median(),
        "Odch. std.": column_values.std(),
        "Min": column_values.min(),
        "Max": column_values.max(),
        "Q1 (25%)": column_values.quantile(0.25),
        "Q3 (75%)": column_values.quantile(0.75),
        "Liczba": column_values.count(),
    }

    return pd.DataFrame({
        "Miara": list(stats.keys()),
        "Wartość": [round(value, 2) for value in stats.values()],
    })

def compute_group_stats(patient_data, numeric_column, grouping_column):
    # Oblicza statystyki dla pewnych grup (dla każdej oddzielnie)
    # Skleja je w jedną tabele

    grouped_result = patient_data.groupby(grouping_column)[numeric_column].agg(
        ["mean", "median", "std", "min", "max", "count"]
    ).round(2)
    grouped_result.columns = ["Średnia", "Mediana", "Odch. std.", "Min", "Max", "Liczba"]
    return grouped_result.reset_index()

def draw_histogram(patient_data, column_name):
    # Rysuje histogram z rozkładem danych danej kolumny

    figure, axis = plt.subplots(figsize=(8, 4))
    axis.hist(patient_data[column_name].dropna(), bins=30,
              edgecolor="black", alpha=0.7, color="#4C8BF5")
    axis.set_xlabel(column_name)
    axis.set_ylabel("Liczba pacjentów")
    axis.set_title(f"Histogram – {column_name}")
    figure.tight_layout()
    return figure

def draw_boxplot(patient_data, column_name):
    # Rysuje boxplot

    figure, axis = plt.subplots(figsize=(8, 4))
    if "Gender" in patient_data.columns:
        male_values = patient_data[patient_data["Gender"] == "Male"][column_name].dropna()
        female_values = patient_data[patient_data["Gender"] == "Female"][column_name].dropna()
        boxplot_result = axis.boxplot(
            [male_values, female_values],
            labels=["Male", "Female"], patch_artist=True,
        )
        boxplot_result["boxes"][0].set_facecolor("#4C8BF5")
        boxplot_result["boxes"][1].set_facecolor("#F54C7A")
    else:
        axis.boxplot(patient_data[column_name].dropna(), patch_artist=True)
    axis.set_ylabel(column_name)
    axis.set_title(f"Boxplot – {column_name}")
    figure.tight_layout()
    return figure

def draw_scatter(patient_data, x_column, y_column):
    # Rysuje wykres rozrzutu dwóch kolumn — każdy punkt to pacjent, kolorowany wg płci.

    figure, axis = plt.subplots(figsize=(8, 4))

    if "Gender" in patient_data.columns:
        gender_colors = patient_data["Gender"].map({"Male": "#4C8BF5", "Female": "#F54C7A"})
        axis.scatter(patient_data[x_column], patient_data[y_column],
                     alpha=0.4, s=12, c=gender_colors)
        male_marker = plt.Line2D([0], [0], marker='o', color='w',
                                 markerfacecolor='#4C8BF5', label='Male', markersize=8)
        female_marker = plt.Line2D([0], [0], marker='o', color='w',
                                   markerfacecolor='#F54C7A', label='Female', markersize=8)
        axis.legend(handles=[male_marker, female_marker])
    else:
        axis.scatter(patient_data[x_column], patient_data[y_column],
                     alpha=0.4, s=12, color="#4C8BF5")

    axis.set_xlabel(x_column)
    axis.set_ylabel(y_column)
    axis.set_title(f"{x_column} vs {y_column}")
    figure.tight_layout()
    return figure

def draw_gender_pie(patient_data):
    # Rysuje wykres kołowy pokazujący rozkład płci

    figure, axis = plt.subplots(figsize=(6, 4))
    gender_counts = patient_data["Gender"].value_counts()
    axis.pie(gender_counts, labels=gender_counts.index,
             autopct="%1.1f%%", colors=["#4C8BF5", "#F54C7A"], startangle=90)
    axis.set_title("Rozkład płci")
    figure.tight_layout()
    return figure

def draw_group_comparison(patient_data, grouping_column, value_column):
    # Rysuje wykres porównawczy miedzy grupami

    figure, axis = plt.subplots(figsize=(8, 4))
    unique_groups = sorted(patient_data[grouping_column].dropna().unique(), key=str)
    group_values = [
        patient_data[patient_data[grouping_column] == group][value_column].dropna().values
        for group in unique_groups
    ]
    group_labels = [str(group) for group in unique_groups]

    color_palette = ["#4C8BF5", "#F54C7A", "#FFC107", "#4CAF50", "#9C27B0"]
    boxplot_result = axis.boxplot(group_values, labels=group_labels, patch_artist=True)
    for index, box in enumerate(boxplot_result["boxes"]):
        box.set_facecolor(color_palette[index % len(color_palette)])

    axis.set_ylabel(value_column)
    axis.set_title(f"Porównanie: {value_column} wg {grouping_column}")
    figure.tight_layout()
    return figure

def save_chart_to_png(figure, filename):
    # Zapisuje figure matplotlib do png

    image_path = os.path.join(tempfile.gettempdir(), filename)
    figure.savefig(image_path, dpi=150)
    plt.close(figure)
    return image_path

def generate_pdf(patient_data):
    # Generuje raport pdf z danymi i wykresami

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    )
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors as rl_colors

    buffer = io.BytesIO()
    pdf_styles = getSampleStyleSheet()
    pdf_elements = []

    pdf_elements.append(Paragraph("Raport analizy danych medycznych", pdf_styles["Title"]))
    pdf_elements.append(Paragraph(
        f"Data: {datetime.datetime.now():%Y-%m-%d %H:%M}  |  "
        f"Rekordów: {len(patient_data)}",
        pdf_styles["Normal"],
    ))
    pdf_elements.append(Spacer(1, 0.5 * cm))

    for column_name in get_available_numeric_columns(patient_data):
        stats_result = compute_stats(patient_data, column_name)
        pdf_elements.append(Paragraph(f"<b>{column_name}</b>", pdf_styles["Heading3"]))
        table_rows = [["Miara", "Wartość"]] + stats_result.values.tolist()
        stats_table = Table(table_rows, colWidths=[5 * cm, 4 * cm])
        stats_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), rl_colors.HexColor("#4C8BF5")),
            ("TEXTCOLOR", (0, 0), (-1, 0), rl_colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, rl_colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
        ]))
        pdf_elements.append(stats_table)
        pdf_elements.append(Spacer(1, 0.3 * cm))

    if "Age" in patient_data.columns:
        image_path = save_chart_to_png(draw_histogram(patient_data, "Age"), "chart_age.png")
        pdf_elements.append(Paragraph("<b>Rozkład wieku</b>", pdf_styles["Heading3"]))
        pdf_elements.append(Image(image_path, width=14 * cm, height=7 * cm))
        pdf_elements.append(Spacer(1, 0.3 * cm))

    if "Heart Rate" in patient_data.columns and "Systolic Blood Pressure" in patient_data.columns:
        image_path = save_chart_to_png(
            draw_scatter(patient_data, "Heart Rate", "Systolic Blood Pressure"),
            "chart_hr_bp.png",
        )
        pdf_elements.append(Paragraph("<b>Tętno vs Ciśnienie skurczowe</b>", pdf_styles["Heading3"]))
        pdf_elements.append(Image(image_path, width=14 * cm, height=7 * cm))
        pdf_elements.append(Spacer(1, 0.3 * cm))

    if "BMI" in patient_data.columns:
        image_path = save_chart_to_png(draw_boxplot(patient_data, "BMI"), "chart_bmi.png")
        pdf_elements.append(Paragraph("<b>BMI wg płci</b>", pdf_styles["Heading3"]))
        pdf_elements.append(Image(image_path, width=14 * cm, height=7 * cm))

    pdf_document = SimpleDocTemplate(buffer, pagesize=A4)
    pdf_document.build(pdf_elements)
    return buffer.getvalue()


def apply_filters(patient_data, filters):
    # Filtruje dane według zakresow min max

    for column_name, (min_value, max_value) in filters.items():
        if column_name in patient_data.columns:
            patient_data = patient_data[
                ((patient_data[column_name] >= min_value) &
                 (patient_data[column_name] <= max_value)) |
                patient_data[column_name].isna()
                ]
    return patient_data

def build_sidebar_filters(patient_data):
    # Buduje panel boczny z filtrami (płeć + suwaki zakresowe) i zwraca przefiltrowane dane.
    st.sidebar.header("Filtry")

    if "Gender" in patient_data.columns:
        gender_options = ["Wszystkie"] + sorted(patient_data["Gender"].dropna().unique().tolist())
        selected_gender = st.sidebar.selectbox("Płeć", gender_options)
        if selected_gender != "Wszystkie":
            patient_data = patient_data[patient_data["Gender"] == selected_gender]

    filter_ranges = {}

    for column_name, (label, min_val, max_val) in SLIDER_CONFIG.items():
        if column_name in patient_data.columns:
            filter_ranges[column_name] = st.sidebar.slider(
                label, min_val, max_val,
                (int(patient_data[column_name].min()), int(patient_data[column_name].max()))
            )

    if "BMI" in patient_data.columns:
        filter_ranges["BMI"] = st.sidebar.slider(
            "BMI", 0.0, 100.0,
            (float(patient_data["BMI"].min()), float(patient_data["BMI"].max())),
            step=0.5,
        )

    filtered_data = apply_filters(patient_data, filter_ranges)
    st.sidebar.metric("Liczba rekordów", f"{len(filtered_data)} / {len(patient_data)}")
    return filtered_data


def show_tab_data(filtered_data):
    # Wyświetla tabelę z danymi pacjentów.
    st.subheader(f"Tabela danych ({len(filtered_data)} rekordów)")
    st.dataframe(filtered_data, use_container_width=True, height=500)


def show_tab_stats(filtered_data):
    # Wyświetla statystyki opisowe i grupowane dla wybranej kolumny.
    available_columns = get_available_numeric_columns(filtered_data)

    st.subheader("Statystyki opisowe")
    stats_column = st.selectbox("Kolumna", available_columns,
                                format_func=polish, key="stats_col")
    st.dataframe(compute_stats(filtered_data, stats_column), use_container_width=True)

    st.subheader("Statystyki grupowane")

    grouping_options = []
    if "Gender" in filtered_data.columns:
        grouping_options.append("Gender")
    if "Grupa wiekowa" in filtered_data.columns:
        grouping_options.append("Grupa wiekowa")

    if grouping_options:
        col_group, col_value = st.columns(2)
        with col_group:
            grouping_column = st.selectbox("Grupuj wg", grouping_options,
                                           format_func=polish)
        with col_value:
            group_value_column = st.selectbox("Kolumna", available_columns,
                                              format_func=polish, key="group_col")

        st.dataframe(
            compute_group_stats(filtered_data, group_value_column, grouping_column),
            use_container_width=True,
        )
    else:
        st.warning("Brak kolumn do grupowania (Gender lub Grupa wiekowa).")

def show_tab_charts(filtered_data):
    # Wyświetla wybrany typ wykresu (histogram, scatter, boxplot, pie, tętno vs ciśnienie).
    available_columns = get_available_numeric_columns(filtered_data)

    chart_options = ["Histogram", "Wykres rozrzutu", "Boxplot"]
    if "Gender" in filtered_data.columns:
        chart_options.append("Rozkład płci")
    if "Heart Rate" in filtered_data.columns and "Systolic Blood Pressure" in filtered_data.columns:
        chart_options.append("Tętno vs Ciśnienie")

    chart_type = st.selectbox("Typ wykresu", chart_options)

    col_x_select, col_y_select = st.columns(2)
    with col_x_select:
        x_column = st.selectbox("Kolumna X", available_columns,
                                format_func=polish, key="x_col")
    with col_y_select:
        y_column = st.selectbox("Kolumna Y", available_columns,
                                format_func=polish,
                                index=min(1, len(available_columns) - 1), key="y_col")

    if chart_type == "Histogram":
        st.pyplot(draw_histogram(filtered_data, x_column))
    elif chart_type == "Wykres rozrzutu":
        st.pyplot(draw_scatter(filtered_data, x_column, y_column))
    elif chart_type == "Boxplot":
        st.pyplot(draw_boxplot(filtered_data, x_column))
    elif chart_type == "Rozkład płci":
        st.pyplot(draw_gender_pie(filtered_data))


def show_tab_compare(filtered_data):
    # Wyświetla porównanie grup (boxploty obok siebie wg płci lub grupy wiekowej).
    available_columns = get_available_numeric_columns(filtered_data)

    grouping_options = []
    if "Gender" in filtered_data.columns:
        grouping_options.append("Gender")
    if "Grupa wiekowa" in filtered_data.columns:
        grouping_options.append("Grupa wiekowa")

    if grouping_options:
        col_cmp_group, col_cmp_value = st.columns(2)
        with col_cmp_group:
            compare_grouping = st.selectbox("Porównaj wg", grouping_options,
                                            format_func=polish, key="cmp_grp")
        with col_cmp_value:
            compare_value = st.selectbox("Parametr", available_columns,
                                         format_func=polish, key="cmp_val")

        st.pyplot(draw_group_comparison(filtered_data, compare_grouping, compare_value))
    else:
        st.warning("Brak kolumn do grupowania (Gender lub Grupa wiekowa).")


def show_tab_export(filtered_data):
    # Wyświetla przyciski do pobrania danych (CSV) i raportu (PDF).
    st.subheader("Eksport danych")

    csv_bytes = filtered_data.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Pobierz filtrowane dane (CSV)",
        data=csv_bytes,
        file_name="filtered_data.csv",
        mime="text/csv",
    )

    st.subheader("Eksport raportu PDF")
    if st.button("Generuj raport PDF"):
        with st.spinner("Generowanie raportu..."):
            pdf_bytes = generate_pdf(filtered_data)
        st.download_button(
            label="Pobierz raport PDF",
            data=pdf_bytes,
            file_name="raport.pdf",
            mime="application/pdf",
        )


def main():
    # Punkt wejścia — konfiguracja strony, upload CSV i przekazanie danych do zakładek.
    st.set_page_config(page_title="Medical Data Analyzer", layout="wide")
    st.title("Medical Patient Data Analyzer")

    uploaded_file = st.file_uploader("Wczytaj plik CSV z danymi pacjentów", type=["csv"])

    if uploaded_file is None:
        st.info("Załaduj plik CSV, aby rozpocząć analizę.")
        return

    patient_data = load_csv(uploaded_file)

    if patient_data.empty:
        st.error("Plik CSV jest pusty lub nie zawiera rozpoznanych kolumn.")
        return

    st.success(f"Wczytano {len(patient_data)} rekordów.")

    filtered_data = build_sidebar_filters(patient_data)

    tab_data, tab_stats, tab_charts, tab_compare, tab_export = st.tabs(
        ["Dane", "Statystyki", "Wykresy", "Porównanie grup", "Eksport"]
    )

    with tab_data:
        show_tab_data(filtered_data)
    with tab_stats:
        show_tab_stats(filtered_data)
    with tab_charts:
        show_tab_charts(filtered_data)
    with tab_compare:
        show_tab_compare(filtered_data)
    with tab_export:
        show_tab_export(filtered_data)

if __name__ == "__main__":
    main()
