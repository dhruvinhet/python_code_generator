# visualizer.py
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import io

def draw_map(map_data):
    """Draws the map using Matplotlib.

    Args:
        map_data (numpy.ndarray): A 2D numpy array representing the map.

    Returns:
        matplotlib.figure.Figure: The Matplotlib figure.
        matplotlib.axes._axes.Axes: The Matplotlib axes.
    """
    fig, ax = plt.subplots()
    ax.imshow(map_data, cmap='gray')
    ax.set_xticks([])
    ax.set_yticks([])
    return fig, ax


def draw_npc(ax, npc):
    """Draws an NPC on the map.

    Args:
        ax (matplotlib.axes._axes.Axes): The Matplotlib axes.
        npc (NPC): The NPC object to draw.
    """
    ax.plot(npc.x, npc.y, 'ro', markersize=8)  # Red circle for NPC


def update_plot(fig, ax, map_data, npcs):
    """Updates the Matplotlib plot with the current simulation state.

    Args:
        fig (matplotlib.figure.Figure): The Matplotlib figure.
        ax (matplotlib.axes._axes.Axes): The Matplotlib axes.
        map_data (numpy.ndarray): The map environment.
        npcs (list): A list of NPC objects.
    """
    ax.imshow(map_data, cmap='gray')
    for npc in npcs:
        draw_npc(ax, npc)


def convert_to_image(fig):
    """Converts the Matplotlib plot to a PIL Image for Streamlit display.

    Args:
        fig (matplotlib.figure.Figure): The Matplotlib figure.

    Returns:
        PIL.Image.Image: The PIL Image object.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    img = Image.open(buf)
    return img