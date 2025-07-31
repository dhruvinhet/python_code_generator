# main.py
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
import npc
import map_generator
import visualizer
import time

# Configuration
MAP_SIZE = 20
NPC_COUNT = 5
SIMULATION_SPEED = 0.1  # Delay in seconds between simulation steps

@st.cache_resource
def initialize_simulation(map_size, npc_count):
    """Initializes the map and NPCs for the simulation."""
    map_data = map_generator.generate_random_map(map_size)
    npcs = []
    for _ in range(npc_count):
        # Find a valid random start location for the NPC
        while True:
            x = np.random.randint(0, map_size)
            y = np.random.randint(0, map_size)
            if map_data[y, x] == 0:  # Check if location is not an obstacle
                break
        new_npc = npc.NPC(x, y, map_size)
        npcs.append(new_npc)
    return map_data, npcs

def main():
    """Main function to handle the Streamlit application flow."""
    st.title("NPC Simulation")

    # Sidebar for user input
    st.sidebar.header("Simulation Parameters")
    map_size = st.sidebar.slider("Map Size", min_value=10, max_value=50, value=MAP_SIZE)
    npc_count = st.sidebar.slider("Number of NPCs", min_value=1, max_value=10, value=NPC_COUNT)
    simulation_speed = st.sidebar.slider("Simulation Speed (seconds per step)", min_value=0.01, max_value=1.0, value=SIMULATION_SPEED, step=0.01)
    load_default = st.sidebar.checkbox("Load Default Image", value=False)

    # Initialize map and NPCs
    map_data, npcs = initialize_simulation(map_size, npc_count)

    # Placeholder for the visualization
    visualization_placeholder = st.empty()
    
    # Use Session State to manage simulation state
    if 'simulation_running' not in st.session_state:
        st.session_state['simulation_running'] = False

    col1, col2 = st.columns(2)
    with col1:
        run_button = st.button("Run Simulation", disabled=st.session_state['simulation_running'])
    with col2:
        stop_button = st.button("Stop Simulation", disabled=not st.session_state['simulation_running'])

    if run_button:
        st.session_state['simulation_running'] = True

    if stop_button:
        st.session_state['simulation_running'] = False

    # Simulation loop
    while st.session_state['simulation_running']:
        # Update NPC positions
        for n in npcs:
            n.move(map_data)  # Pass the map for obstacle avoidance

        # Visualize the simulation
        fig, ax = visualizer.draw_map(map_data)
        for n in npcs:
            visualizer.draw_npc(ax, n)

        # Update the Streamlit placeholder with the new image
        image = visualizer.convert_to_image(fig)
        visualization_placeholder.image(image, use_column_width=True)

        plt.close(fig) # Close the figure to prevent memory leaks
        # Pause for the specified simulation speed
        time.sleep(simulation_speed)

if __name__ == "__main__":
    main()