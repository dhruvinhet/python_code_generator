# main.py
import streamlit as st
import npc_logic
import npc_data
import pandas as pd


def main():
    """Entry point of the Streamlit application."""
    st.title("NPC Simulator")

    # Sidebar for user input
    st.sidebar.header("Simulation Parameters")
    num_npcs = st.sidebar.slider("Number of NPCs", 1, 10, 3)
    num_days = st.sidebar.slider("Number of Simulation Days", 1, 30, 7)

    # Button to start the simulation
    if st.button("Start Simulation"):    
        # Initialize NPCs
        npcs = [npc_logic.create_npc() for _ in range(num_npcs)]

        # Simulate each day for each NPC
        simulation_data = []
        for day in range(num_days):
            for npc in npcs:
                daily_data = npc_logic.simulate_npc_day(npc, day)
                simulation_data.append(daily_data)

        # Convert simulation data to Pandas DataFrame for display
        df = pd.DataFrame(simulation_data)

        # Display the simulation results
        st.header("Simulation Results")
        st.dataframe(df)

        # Download the data in CSV format
        try:
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download simulation data as CSV",
                data=csv,
                file_name='npc_simulation.csv',
                mime='text/csv',
            )
        except Exception as e:
            st.error(f"An error occurred during CSV conversion or download: {e}")


if __name__ == "__main__":
    main()