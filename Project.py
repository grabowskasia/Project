import io
import os
import datetime
import tempfile

import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

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


