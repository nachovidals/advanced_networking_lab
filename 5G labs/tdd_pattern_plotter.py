#
# Created by Arno Troch on 20/03/2024
#
# Visualize a single TDD frame given the TDD pattern, special slot configuration and subcarrier spacing index.
#

import re
import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.patches import ConnectionPatch

########################################################################################################################
# Constants
########################################################################################################################
# mapping of slot type to color
SLOT_COLORS = {
    'D': 'blue',
    'U': 'green',
    'S': 'yellow'
}

# allowed periodicities for the TDD pattern
PERIODICITY = {0.5, 0.625, 1, 1.25, 2, 2.5, 5, 10}


########################################################################################################################
# Plotting
########################################################################################################################
def plot_tdd_pattern(tdd_pattern: str, s_pattern: str, scs_index: int):
    # first, we need to check whether the TDD pattern and special slot configuration are valid
    # - validate format
    assert re.match(r'^D+SU+$', tdd_pattern), \
        "Invalid TDD pattern string. String should satisfy regex '^D+SU+$'"
    assert len(s_pattern) == 14 and re.match(r'^D+[-]*U+$', s_pattern), \
        "Invalid special slot string. String should be 14 characters and satisfy regex '^D+[-]*U+$'"

    # - validate the TDD pattern periodicity
    slot_time_ms = 1 / (2 ** scs_index)
    periodicity_ms = slot_time_ms * len(tdd_pattern)
    assert periodicity_ms in PERIODICITY, \
        f"Invalid TDD pattern periodicity. Periodicity of pattern is {periodicity_ms} ms, should be in {PERIODICITY}."

    # after validation, calculate the TDD parameters
    dl_slots = tdd_pattern.count('D')
    dl_symbols = s_pattern.count('D')
    ul_slots = tdd_pattern.count('U')
    ul_symbols = s_pattern.count('U')

    symbols_per_slot = 14
    slots_per_subframe = 2 ** scs_index
    slots_per_frame = slots_per_subframe * 10
    first_special_slot_limits = (dl_slots, dl_slots + 1)
    amount_of_slots_in_pattern = dl_slots + ul_slots + 1

    slot_time_ms = 1 / (2 ** scs_index)
    assert periodicity_ms == slot_time_ms * amount_of_slots_in_pattern, \
        "Periodicity does not match the TDD pattern."

    fig = plt.figure(dpi=300, figsize=(6, 2))
    plt.subplots_adjust(hspace=1)

    # Create first axes, the top-right plot with orange plot
    handles = [mpl.patches.Patch(color=c, label=s, alpha=0.5, linewidth=0) for s, c in SLOT_COLORS.items()]
    fig.legend(title="Type", handles=handles, loc='lower left', fontsize='small', bbox_to_anchor=(0.1, 0.1))

    # Create first axes, a combination of third and fourth cell
    top = fig.add_subplot(2, 7, (1, 7))  # two rows, two colums, combined fourth, fifth and sixth cell

    amount_of_repeats = int(slots_per_frame / amount_of_slots_in_pattern)
    for r in range(int(amount_of_repeats)):
        for slot in range(1, amount_of_slots_in_pattern + 1):
            if slot <= dl_slots:
                color = SLOT_COLORS['D']
            elif slot == dl_slots + 1:
                color = SLOT_COLORS['S']
            else:
                color = SLOT_COLORS['U']
            top.add_patch(mpl.patches.Rectangle((int(r * amount_of_slots_in_pattern) + slot - 1, 0),
                                                1, 1, color=color, alpha=0.5, linewidth=0))

    top.set_title("Frame Structure")
    top.set_xlim(0, slots_per_frame)
    top.set_xticks(np.arange(0, slots_per_frame, slots_per_subframe), minor=False)
    top.set_xticks(np.arange(0, slots_per_frame, 1), minor=True)
    top.set_xticklabels([])
    top.tick_params(axis='x', which='both', length=0)
    top.set_ylim(0, 1)
    top.set_yticks([])
    top.grid(which='minor', alpha=0.7, linewidth='0.5', color='black')
    top.grid(which='major', alpha=0.7, linewidth='1', color='black')
    top.set_axisbelow(False)

    # Create second axes, the top-left plot with orange plot, and share the y-axis with sub1
    bottom = fig.add_subplot(2, 7, (9, 13))  # two rows, three columns, combined second and third cell

    # create the rectangles
    for symbol in range(1, 15):
        if symbol <= dl_symbols:
            color = SLOT_COLORS['D']
        elif symbols_per_slot - ul_symbols < symbol <= symbols_per_slot:
            color = SLOT_COLORS['U']
        else:
            color = 'white'
        bottom.add_patch(mpl.patches.Rectangle((symbol - 1, 0), 1, 1,
                                               color=color, alpha=0.5, linewidth=0))

    bottom.set_title("Slot Structure")
    bottom.set_xlim(0, symbols_per_slot)
    bottom.set_xticks(np.arange(0, symbols_per_slot, 1))
    bottom.set_xticklabels([])
    bottom.tick_params(axis='x', which='both', length=0)
    bottom.set_ylim(0, 1)
    bottom.set_yticks([])
    bottom.grid(linewidth='0.5', alpha=0.7, color='black')
    top.set_axisbelow(False)

    # Create left side of Connection patch for second axes
    con1 = ConnectionPatch(xyA=(first_special_slot_limits[0], 0), coordsA=top.transData,
                           xyB=(0, 1), coordsB=bottom.transData, color='black')
    # Add left side to the figure
    fig.add_artist(con1)

    # Create right side of Connection patch for second axes
    con2 = ConnectionPatch(xyA=(first_special_slot_limits[1], 0), coordsA=top.transData,
                           xyB=(symbols_per_slot, 1), coordsB=bottom.transData, color='black')
    # Add right side to the figure
    fig.add_artist(con2)

    return fig
