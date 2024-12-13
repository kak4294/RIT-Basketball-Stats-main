import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os
import textwrap

def create_bar_chart(data_dict, section, y_max, title, output_filename='bar_chart.png'):
    """
    Creates a professional-looking bar chart from a dictionary of key-value pairs with a color scheme
    based on the provided section number and sets the Y-axis limit based on y_max.
    
    Parameters:
    - data_dict (dict): Dictionary containing key-value pairs to plot.
    - section (int): An integer between 1 and 9 determining the color scheme.
    - y_max (int): Y-axis limit. Must be one of [25, 50, 100, 150].
    - title (str): The title of the bar chart.
    - output_filename (str): The filename to save the bar chart image.
    """
    
    # Input Validation
    if not isinstance(data_dict, dict):
        raise TypeError("data_dict must be a dictionary.")

    if not isinstance(section, int) or not (1 <= section <= 9):
        raise ValueError("section must be an integer between 1 and 9.")

    if not isinstance(y_max, int) or y_max not in [15, 25, 50, 100, 150]:
        raise ValueError("y_max must be an integer and one of the following values: 15, 25, 50, 100, 150.")

    if not isinstance(title, str):
        raise TypeError("title must be a string.")

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
    
    # Function to wrap labels
    def wrap_label(label):
        return '\n'.join(label.split('-'))
    
    # Assign colors based on the section
    colors = color_schemes[section]

    # Extract keys and values
    keys = list(data_dict.keys())
    values = list(data_dict.values())
    
    # Wrap labels if they exceed max_char
    wrapped_keys = [wrap_label(label) for label in keys]

    # Determine rotation angle
    rotation_angle = should_rotate_labels(wrapped_keys)

    # Create the bar chart with a professional style
    plt.style.use('seaborn-darkgrid')  # Professional-looking style

    plt.figure(figsize=(12, 8))  # Larger figure size for better visibility
    bars = plt.bar(wrapped_keys, values, color=colors, edgecolor='black')

    # Add title and labels with larger fonts
    plt.title(title, fontsize=22, fontweight='bold')
    plt.xlabel('Categories', fontsize=20, fontweight='bold', labelpad=20)
    plt.ylabel('Total Plays', fontsize=20, fontweight='bold', labelpad=20)

    # Set Y-axis limit based on y_max
    plt.ylim(0, y_max)

    # Customize tick labels with larger fonts
    plt.xticks(fontsize=17, rotation=rotation_angle)  # Rotate x labels if they are long
    plt.yticks(fontsize=17)

    # Add value labels on top of each bar with enhanced styling
    for bar in bars:
        height = bar.get_height()
        # Only annotate if the bar height is within the y_max
        if height <= y_max:
            plt.annotate(f'{height}',
                         xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 8),  
                         textcoords="offset points",
                         ha='center', va='bottom',
                         fontsize=18, fontweight='bold', color='black')
        else:
            plt.annotate('N/A',
                         xy=(bar.get_x() + bar.get_width() / 2, y_max),
                         xytext=(0, 8),
                         textcoords="offset points",
                         ha='center', va='bottom',
                         fontsize=18, fontweight='bold', color='red')

    # Add gridlines for better readability
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Improve layout
    plt.tight_layout()

    # Ensure the output directory exists
    output_dir = os.path.dirname(output_filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Save the plot to a file with high resolution
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'Bar chart saved as {output_filename}')
    
    
def should_rotate_labels(labels, max_labels=5):
    """
    Determines whether to rotate x-axis labels based on their length and count.
    
    Parameters:
    - labels (list): List of label strings.
    - max_length (int): Maximum allowed length before rotation.
    - max_labels (int): Maximum allowed number of labels before rotation.
    
    Returns:
    - rotation_angle (int): Angle to rotate labels. 0 means no rotation.
    """
    # Check if number of labels exceeds the threshold
    if len(labels) > max_labels:
        return 45  # Vertical rotation
    
    return 0  # No rotation

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
