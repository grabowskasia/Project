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
    "Systolic Blood Pressure", "Diastolic Blood Pressure",
]


def load_csv(uploaded_file):
    # Wczytuje dane z pliku CSV, wybiera dane z "COLUMNS_TO_KEEP"
    # Usuwa duplikaty, oblicza BMI i sortuje bo dacie

    patient_data = pd.read_csv(uploaded_file)
    available_columns = [col for col in COLUMNS_TO_KEEP if col in patient_data.columns]
    patient_data = patient_data[available_columns].copy()
    patient_data.dropna(subset=available_columns, inplace=True)

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

    for column_name in NUMERIC_COLUMNS:
        if column_name not in patient_data.columns:
            continue
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
                (patient_data[column_name] >= min_value) &
                (patient_data[column_name] <= max_value)
            ]
    return patient_data
