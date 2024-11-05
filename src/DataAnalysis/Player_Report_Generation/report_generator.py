import json
from jinja2 import Environment, FileSystemLoader

def load_json(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

def render_template(template_name, data, output_path):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(template_name)
    output = template.render(data)
    with open(output_path, 'w') as file:
        file.write(output)

def main():
    # Load JSON data
    with open('/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/data/2023_24/cleaned/reports/Matt-Caggiano-10-30-2024/insights_4.json') as f:
        data = json.load(f)

    # Set up Jinja2 environment
    file_loader = FileSystemLoader('.')
    env = Environment(loader=file_loader)

    # Load the LaTeX template
    template = env.get_template('latex_template.tex')

    # Render the template with data
    rendered_latex = template.render(PNR_insights=data['PNR_insights'], 
                                     Post_insights=data['Post_insights'], 
                                     Cut_insights=data['Cut_insights'],
                                     Rollman_insights=data['Rollman_insights'], 
                                     Spotup_insights=data['Spotup_insights'],
                                     Handoff_insights=data['Handoff_insights'],
                                     Transition_insights=data['Transition_insights'], 
                                     OffScreen_insights=data['Offscreen_insights'],
                                     Iso_insights=data['Iso_insights'])

    # Write the rendered LaTeX to a file
    with open('Mat.tex', 'w') as f:
        f.write(rendered_latex)

if __name__ == "__main__":
    main()
