# npc_visualizer.py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st


def plot_npc_locations(environment, npcs):
    """Plots the locations of NPCs in the environment.

    Args:
        environment (Environment): The environment object.
        npcs (list): A list of NPC objects.
    """
    x_coords = [npc.x for npc in npcs]
    y_coords = [npc.y for npc in npcs]

    fig, ax = plt.subplots()
    ax.set_xlim(0, environment.width)
    ax.set_ylim(0, environment.height)
    ax.scatter(x_coords, y_coords)
    ax.set_xlabel("X Position")
    ax.set_ylabel("Y Position")
    ax.set_title("NPC Locations")
    ax.set_aspect('equal', adjustable='box') # Ensure axis are equal for proper visualization

    st.pyplot(fig)


def display_simulation_data(simulation_results):
    """Displays simulation data in a Pandas DataFrame.

    Args:
        simulation_results (list): A list of dictionaries containing simulation data.
    """
    df = pd.DataFrame(simulation_results)
    st.dataframe(df)