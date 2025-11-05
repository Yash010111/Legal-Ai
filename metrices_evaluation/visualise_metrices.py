"""
visualise_metrices.py
Plots various metrics (accuracy, precision, recall, F1-score) for Legal Mind AI project.
"""

import matplotlib.pyplot as plt
import numpy as np
import json
import os

def plot_metrics(metrics: dict, title: str = "Model Metrics Evaluation"):
    """
    Plots bar, line, scatter, and radar charts for given metrics.
    Args:
        metrics: Dictionary of metric name to value
        title: Title of the plot
    """
    names = list(metrics.keys())
    values = list(metrics.values())

    fig, axs = plt.subplots(2, 2, figsize=(12, 10))

    # Bar chart
    bars = axs[0, 0].bar(names, values, color=['#4e79a7', '#f28e2b', '#e15759', '#76b7b2'])
    axs[0, 0].set_ylim(0, 1.05)
    axs[0, 0].set_ylabel("Score")
    axs[0, 0].set_title("Bar Chart")
    axs[0, 0].grid(axis='y', linestyle='--', alpha=0.5)
    for bar, value in zip(bars, values):
        axs[0, 0].text(bar.get_x() + bar.get_width()/2, value + 0.02, f"{value:.2f}", ha='center', va='bottom')

    # Line chart
    axs[0, 1].plot(names, values, marker='o', color='#4e79a7', linewidth=2)
    axs[0, 1].set_ylim(0, 1.05)
    axs[0, 1].set_ylabel("Score")
    axs[0, 1].set_title("Line Chart")
    axs[0, 1].grid(axis='y', linestyle='--', alpha=0.5)

    # Scatter plot
    axs[1, 0].scatter(names, values, s=120, color='#e15759')
    axs[1, 0].set_ylim(0, 1.05)
    axs[1, 0].set_ylabel("Score")
    axs[1, 0].set_title("Scatter Plot")
    axs[1, 0].grid(axis='y', linestyle='--', alpha=0.5)

    # Radar chart
    angles = np.linspace(0, 2 * np.pi, len(names), endpoint=False).tolist()
    values_radar = values + [values[0]]  # close the loop
    angles_radar = angles + [angles[0]]
    axs[1, 1] = plt.subplot(2, 2, 4, polar=True)
    axs[1, 1].plot(angles_radar, values_radar, 'o-', color='#76b7b2', linewidth=2)
    axs[1, 1].fill(angles_radar, values_radar, color='#76b7b2', alpha=0.25)
    axs[1, 1].set_title("Radar Chart", y=1.1)
    axs[1, 1].set_xticks(angles)
    axs[1, 1].set_xticklabels(names)
    axs[1, 1].set_yticklabels([f"{y:.1f}" for y in np.linspace(0, 1, 6)])

    plt.suptitle(title, fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

if __name__ == "__main__":
    # Load actual metrics from tests/metrics_results.json if available
    metrics_path = os.path.join(os.path.dirname(__file__), "..", "tests", "metrics_results.json")
    if os.path.exists(metrics_path):
        with open(metrics_path, "r") as f:
            metrics = json.load(f)
        # Assign unique metrics to each graph
        bar_metrics = {k: metrics[k] for k in ["Accuracy", "Precision"] if k in metrics}
        line_metrics = {k: metrics[k] for k in ["Recall", "F1-score"] if k in metrics}
        scatter_metrics = {k: metrics[k] for k in ["ROC-AUC", "Specificity"] if k in metrics}
        radar_metrics = metrics  # All available metrics

        fig, axs = plt.subplots(2, 2, figsize=(12, 10))

        # Bar chart
        names = list(bar_metrics.keys())
        values = list(bar_metrics.values())
        bars = axs[0, 0].bar(names, values, color=['#4e79a7', '#f28e2b'])
        axs[0, 0].set_ylim(0, 1.05)
        axs[0, 0].set_ylabel("Score")
        axs[0, 0].set_title("Bar Chart: Accuracy & Precision")
        axs[0, 0].grid(axis='y', linestyle='--', alpha=0.5)
        for bar, value in zip(bars, values):
            axs[0, 0].text(bar.get_x() + bar.get_width()/2, value + 0.02, f"{value:.2f}", ha='center', va='bottom')

        # Line chart
        names = list(line_metrics.keys())
        values = list(line_metrics.values())
        axs[0, 1].plot(names, values, marker='o', color='#4e79a7', linewidth=2)
        axs[0, 1].set_ylim(0, 1.05)
        axs[0, 1].set_ylabel("Score")
        axs[0, 1].set_title("Line Chart: Recall & F1-score")
        axs[0, 1].grid(axis='y', linestyle='--', alpha=0.5)

        # Scatter plot
        names = list(scatter_metrics.keys())
        values = list(scatter_metrics.values())
        axs[1, 0].scatter(names, values, s=120, color='#e15759')
        axs[1, 0].set_ylim(0, 1.05)
        axs[1, 0].set_ylabel("Score")
        axs[1, 0].set_title("Scatter Plot: ROC-AUC & Specificity")
        axs[1, 0].grid(axis='y', linestyle='--', alpha=0.5)

        # Radar chart
        names = list(radar_metrics.keys())
        values = list(radar_metrics.values())
        angles = np.linspace(0, 2 * np.pi, len(names), endpoint=False).tolist()
        values_radar = values + [values[0]]
        angles_radar = angles + [angles[0]]
        axs[1, 1] = plt.subplot(2, 2, 4, polar=True)
        axs[1, 1].plot(angles_radar, values_radar, 'o-', color='#76b7b2', linewidth=2)
        axs[1, 1].fill(angles_radar, values_radar, color='#76b7b2', alpha=0.25)
        axs[1, 1].set_title("Radar Chart: All Metrics", y=1.1)
        axs[1, 1].set_xticks(angles)
        axs[1, 1].set_xticklabels(names)
        axs[1, 1].set_yticklabels([f"{y:.1f}" for y in np.linspace(0, 1, 6)])

        plt.suptitle("Legal Mind AI - Metrics Evaluation", fontsize=16)
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()
    else:
        print("metrics_results.json not found in tests/. Please run your evaluation and save metrics as JSON.")
