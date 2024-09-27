#!/bin/bash
set -ex

pip install pandas matplotlib mpld3 plotly

python visualize.py $telegraf_file

cp resource_usage_chart.html $BITRISE_DEPLOY_DIR/telegraf_viz/index.html

echo "This is the value specified for the input 'example_step_input': ${example_step_input}"

envman add --key VISUALIZATION_HTML_PATH --value ${BITRISE_DEPLOY_DIR/telegraf_viz/index.html}
