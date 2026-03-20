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
