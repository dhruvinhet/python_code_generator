# nfa_to_dfa_converter.py
import regex as re


def parse_nfa_description(nfa_description):
    """Parses the NFA description string and extracts the states, alphabet, start state, accepting states, and transitions."""
    try:
        states_match = re.search(r"States are (.*?)[.]", nfa_description, re.IGNORECASE)
        alphabet_match = re.search(r"Alphabet is (.*?)[.]", nfa_description, re.IGNORECASE)
        start_state_match = re.search(r"Start state is (.*?)[.]", nfa_description, re.IGNORECASE)
        accepting_states_match = re.search(r"Accepting states are (.*?)[.]", nfa_description, re.IGNORECASE)
        transitions_match = re.search(r"Transitions: (.*?)$", nfa_description, re.IGNORECASE | re.MULTILINE)

        states = [s.strip() for s in states_match.group(1).split(",")] if states_match else []
        alphabet = [a.strip() for a in alphabet_match.group(1).split(",")] if alphabet_match else []
        start_state = start_state_match.group(1).strip() if start_state_match else None
        accepting_states = [a.strip() for a in accepting_states_match.group(1).split(",")] if accepting_states_match else []
        transitions_str = transitions_match.group(1).strip() if transitions_match else None

        transitions = {}  # transitions[state, symbol] = [next_states]
        if transitions_str:
            transition_lines = transitions_str.split(",")
            for line in transition_lines:
                match = re.search(r"(.*?)\s+on\s+(.*?)\s+goes to\s+(.*?)$", line.strip(), re.IGNORECASE)
                if match:
                    from_state = match.group(1).strip()
                    symbol = match.group(2).strip()
                    to_states = [s.strip() for s in match.group(3).split("and")]

                    if (from_state, symbol) not in transitions:
                        transitions[(from_state, symbol)] = []
                    transitions[(from_state, symbol)].extend(to_states)

        return states, alphabet, start_state, accepting_states, transitions

    except Exception as e:
        print(f"Error parsing NFA description: {e}")
        return [], [], None, [], {}


def build_nfa(states, alphabet, start_state, accepting_states, transitions):
    """Builds the NFA data structure from the parsed components."""
    nfa = {
        "states": states,
        "alphabet": alphabet,
        "start_state": start_state,
        "accepting_states": accepting_states,
        "transitions": transitions,
    }
    return nfa


def convert_nfa_to_dfa(nfa_description):
    """Converts an NFA to a DFA."""
    states, alphabet, start_state, accepting_states, transitions = parse_nfa_description(nfa_description)

    if not all([states, alphabet, start_state, accepting_states, transitions is not None]):
        print("Error: Could not parse NFA description.")
        return None

    if not states or not alphabet or not start_state or not accepting_states:
        print("Error: Incomplete NFA description.")
        return None

    nfa = build_nfa(states, alphabet, start_state, accepting_states, transitions)

    dfa_states = {frozenset({nfa['start_state']})}  # DFA states are sets of NFA states
    dfa_start_state = frozenset({nfa['start_state']})
    dfa_accepting_states = set()
    dfa_transitions = {}

    queue = [dfa_start_state]

    while queue:
        current_dfa_state = queue.pop(0)
        for symbol in nfa['alphabet']:
            next_nfa_states = set()
            for nfa_state in current_dfa_state:
                if (nfa_state, symbol) in nfa['transitions']:
                    next_nfa_states.update(nfa['transitions'][(nfa_state, symbol)])

            next_dfa_state = frozenset(next_nfa_states)

            if next_dfa_state:
                dfa_transitions[(current_dfa_state, symbol)] = next_dfa_state

                if next_dfa_state not in dfa_states:
                    dfa_states.add(next_dfa_state)
                    queue.append(next_dfa_state)

    # Determine DFA accepting states
    for dfa_state in dfa_states:
        for nfa_state in dfa_state:
            if nfa_state in nfa['accepting_states']:
                dfa_accepting_states.add(dfa_state)
                break

    dfa = {
        "states": [str(state) for state in dfa_states],
        "alphabet": nfa['alphabet'],
        "start_state": str(dfa_start_state),
        "accepting_states": [str(state) for state in dfa_accepting_states],
        "transitions": {(
            str(from_state), symbol
        ): str(to_state) for (from_state, symbol), to_state in dfa_transitions.items()},
    }

    dfa = remove_unreachable_states(dfa)

    return dfa


def remove_unreachable_states(dfa):
    """Removes unreachable states from the DFA."""
    reachable_states = {dfa['start_state']}
    new_states = {dfa['start_state']}

    while new_states:
        current_state = new_states.pop()
        for symbol in dfa['alphabet']:
            if (current_state, symbol) in dfa['transitions']:
                next_state = dfa['transitions'][(current_state, symbol)]
                if next_state not in reachable_states:
                    reachable_states.add(next_state)
                    new_states.add(next_state)

    # Filter out unreachable states
    dfa['states'] = [state for state in dfa['states'] if state in reachable_states]
    dfa['accepting_states'] = [state for state in dfa['accepting_states'] if state in reachable_states]
    dfa['transitions'] = {(
        state, symbol
    ): next_state for (state, symbol), next_state in dfa['transitions'].items() if state in reachable_states}

    return dfa