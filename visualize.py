import pandas as pd
import plotly.graph_objects as go
import sys
from datetime import datetime

def parse_telegraf_output(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    cpu_data = {'timestamp': [], 'cpu': [], 'usage_user': []}
    mem_data = {'timestamp': [], 'used_percent': []}

    for line in lines:
        parts = line.split()
        if line.startswith('cpu'):
            cpu_metrics = parts[1].split(',')
            timestamp = int(parts[-1]) / 1e9  # Convert nanoseconds to seconds
            human_readable_time = datetime.utcfromtimestamp(timestamp)

            cpu = cpu_metrics[0].split('=')[1]
            metrics = {metric.split('=')[0]: float(metric.split('=')[1]) for metric in cpu_metrics[0:]}

            cpu_data['timestamp'].append(human_readable_time)
            cpu_entry=parts[0].split(',')[1].split('=')[1]
            cpu_data['cpu'].append(cpu_entry)
            cpu_usage_entry=metrics.get('usage_user', 0)
            cpu_data['usage_user'].append(cpu_usage_entry)
            if cpu_entry == 'cpu-total' and cpu_usage_entry == 0:
                    print(cpu_metrics)
                    print(metrics)
                    print(cpu_entry + " - " + str(cpu_usage_entry) + " - " + str(timestamp))
        elif line.startswith('mem'):
            mem_metrics = parts[1].split(',')
            timestamp = int(parts[-1]) / 1e9  # Convert nanoseconds to seconds
            human_readable_time = datetime.utcfromtimestamp(timestamp)

            metrics = {metric.split('=')[0]: float(metric.split('=')[1].strip('i')) for metric in mem_metrics}

            mem_data['timestamp'].append(human_readable_time)
            mem_data['used_percent'].append(metrics.get('used_percent', 0))

    cpu_df = pd.DataFrame(cpu_data)
    mem_df = pd.DataFrame(mem_data)

    start_time = cpu_df['timestamp'].min()
    cpu_df['duration'] = cpu_df['timestamp'] - start_time
    cpu_df['duration'] = cpu_df['duration'].dt.total_seconds()  # Convert duration to seconds
    

    start_time = mem_df['timestamp'].min()
    mem_df['duration'] = mem_df['timestamp'] - start_time
    mem_df['duration'] = mem_df['duration'].dt.total_seconds()  # Convert duration to seconds

    return cpu_df, mem_df

def create_cpu_chart(df):
    fig = go.Figure()

    muted_colors = [
        'rgba(31, 119, 180, 0.5)', 'rgba(255, 127, 14, 0.5)', 'rgba(44, 160, 44, 0.5)', 
        'rgba(214, 39, 40, 0.5)', 'rgba(148, 103, 189, 0.5)', 'rgba(140, 86, 75, 0.5)', 
        'rgba(227, 119, 194, 0.5)', 'rgba(127, 127, 127, 0.5)', 'rgba(188, 189, 34, 0.5)', 
        'rgba(23, 190, 207, 0.5)'
    ]
    total_color = 'rgba(255, 0, 0, 1)'  # Bright red for cpu-total

    color_index = 0
    for cpu in df['cpu'].unique():

        

        cpu_data = df[df['cpu'] == cpu]
        line_width = 4 if cpu == 'cpu-total' else 2
        line_color = total_color if cpu == 'cpu-total' else muted_colors[color_index % len(muted_colors)]
        fig.add_trace(go.Scatter(
            x=cpu_data['duration'], 
            y=cpu_data['usage_user'],
            mode='lines', 
            name=f'{cpu} - User',
            line=dict(width=line_width, color=line_color)
        ))
        if cpu != 'cpu-total':
            color_index += 1

    fig.update_layout(title='CPU User Usage Over Time',
                      xaxis_title='Duration Passed (s)',
                      yaxis_title='CPU User Usage (%)')

    return fig

def create_mem_chart(df):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['duration'], 
        y=df['used_percent'],
        mode='lines', 
        name='Memory Used (%)',
        line=dict(width=2)
    ))

    fig.update_layout(title='Memory Usage Over Time',
                      xaxis_title='Duration Passed (s)',
                      yaxis_title='Memory Usage (%)')

    return fig

def main(file_path):
    cpu_df, mem_df = parse_telegraf_output(file_path)

    cpu_fig = create_cpu_chart(cpu_df)
    mem_fig = create_mem_chart(mem_df)

    # Combine both charts into a single HTML file
    combined_html = f"""
    <html>
    <head>
        <title>Resource Usage Charts</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    </head>
    <body>
        <h1>CPU Usage</h1>
        {cpu_fig.to_html(full_html=False, include_plotlyjs='cdn')}
        <h1>Memory Usage</h1>
        {mem_fig.to_html(full_html=False, include_plotlyjs='cdn')}
    </body>
    </html>
    """

    output_file = 'resource_usage_chart.html'
    with open(output_file, 'w') as file:
        file.write(combined_html)

    print(f'Charts have been created and saved to {output_file}')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python telegraf_to_chart.py <path_to_telegraf_output_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    main(file_path)