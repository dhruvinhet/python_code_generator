# main.py
import streamlit as st
import npc_core
import npc_visualizer
import pandas as pd


def main():
    """Entry point for the Streamlit application."""
    st.title("NPC Simulator")

    # Sidebar for user inputs
    st.sidebar.header("Simulation Parameters")
    num_npcs = st.sidebar.number_input("Number of NPCs", min_value=1, max_value=100, value=10)
    simulation_steps = st.sidebar.number_input("Simulation Steps", min_value=10, max_value=500, value=100)
    environment_width = st.sidebar.number_input("Environment Width", min_value=10, max_value=100, value=50)
    environment_height = st.sidebar.number_input("Environment Height", min_value=10, max_value=100, value=50)

    # Button to start the simulation
    if st.sidebar.button("Run Simulation"):
        try:
            # Create NPCs with default traits
            npcs = [npc_core.NPC(f"NPC_{i}", {"aggression": 0.5, "intelligence": 0.5}, environment_width, environment_height) for i in range(num_npcs)]

            # Create the environment
            environment = npc_core.Environment(environment_width, environment_height)

            # Run the simulation
            simulation_results = npc_core.simulate(npcs, environment, simulation_steps)

            # Visualize the results
            st.header("Simulation Results")
            npc_visualizer.display_simulation_data(simulation_results)

            # Plot NPC locations
            st.header("NPC Locations")
            npc_visualizer.plot_npc_locations(environment, npcs)
        except Exception as e:
            st.error(f"An error occurred during the simulation: {e}")


# Run the Streamlit app
if __name__ == "__main__":
    main()