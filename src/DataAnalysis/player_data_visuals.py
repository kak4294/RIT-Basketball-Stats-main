import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def create_bar_chart(data_dict, section, y_max, output_filename='bar_chart.png'):
    """
    Creates a bar chart from a dictionary of key-value pairs with a color scheme
    based on the provided section number and sets the Y-axis limit based on y_max.

    Parameters:
    - data_dict (dict): Dictionary containing key-value pairs to plot.
    - section (int): An integer between 1 and 9 determining the color scheme.
    - y_max (int): Y-axis limit. Must be one of [25, 50, 100, 150].
    - output_filename (str): The filename to save the bar chart image.
    """

    # Input Validation
    if not isinstance(data_dict, dict):
        raise TypeError("data_dict must be a dictionary.")

    if not isinstance(section, int) or not (1 <= section <= 9):
        raise ValueError("section must be an integer between 1 and 9.")

    if not isinstance(y_max, int) or y_max not in [25, 50, 100, 150]:
        raise ValueError("y_max must be an integer and one of the following values: 25, 50, 100, 150.")

    # Define color schemes for sections 1-9
    color_schemes = {
        1: ['#1f77b4'] * len(data_dict),  # Blue
        2: ['#ff7f0e'] * len(data_dict),  # Orange
        3: ['#2ca02c'] * len(data_dict),  # Green
        4: ['#d62728'] * len(data_dict),  # Red
        5: ['#9467bd'] * len(data_dict),  # Purple
        6: ['#8c564b'] * len(data_dict),  # Brown
        7: ['#e377c2'] * len(data_dict),  # Pink
        8: ['#7f7f7f'] * len(data_dict),  # Gray
        9: ['#bcbd22'] * len(data_dict),  # Olive
    }

    # Alternatively, use different colors for each bar within a section
    # Uncomment the following block if you prefer varied colors within a section
    """
    color_schemes = {
        1: list(mcolors.TABLEAU_COLORS.values()),
        2: list(mcolors.CSS4_COLORS.values()),
        3: list(mcolors.XKCD_COLORS.values()),
        4: list(mcolors.BASE_COLORS.values()),
        5: list(mcolors.CSS4_COLORS.values()),
        6: list(mcolors.TABLEAU_COLORS.values()),
        7: list(mcolors.XKCD_COLORS.values()),
        8: list(mcolors.BASE_COLORS.values()),
        9: list(mcolors.TABLEAU_COLORS.values()),
    }
    # Cycle through colors if there are more bars than colors available
    colors = [color_schemes[section][i % len(color_schemes[section])] for i in range(len(data_dict))]
    """

    # Assign colors based on the section
    colors = color_schemes[section]

    # Extract keys and values
    keys = list(data_dict.keys())
    values = list(data_dict.values())

    # Create the bar chart
    plt.figure(figsize=(10, 6))
    bars = plt.bar(keys, values, color=colors)

    # Add title and labels
    plt.title(f'Bar Chart - Section {section}')
    plt.xlabel('Keys')
    plt.ylabel('Total Plays')  # Updated Y-axis label

    # Set Y-axis limit based on y_max
    plt.ylim(0, y_max)

    # Optional: Add value labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        # Only annotate if the bar height is within the y_max
        if height <= y_max:
            plt.annotate(f'{height}',
                         xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 3),  # 3 points vertical offset
                         textcoords="offset points",
                         ha='center', va='bottom')
        else:
            plt.annotate('N/A',
                         xy=(bar.get_x() + bar.get_width() / 2, y_max),
                         xytext=(0, 3),
                         textcoords="offset points",
                         ha='center', va='bottom')

    # Improve layout
    plt.tight_layout()

    # Save the plot to a file
    plt.savefig(output_filename)
    plt.close()
    print(f'Bar chart saved as {output_filename}')

# Example usage
if __name__ == "__main__":
    sample_data = {
        'Category A': 23,
        'Category B': 17,
        'Category C': 35,
        'Category D': 29,
        'Category E': 12
    }

    section_number = 3  # Choose a number between 1 and 9
    y_axis_max = 50      # Choose one of the following values: 25, 50, 100, 150
    create_bar_chart(sample_data, section_number, y_axis_max, 'sample_bar_chart.png')
