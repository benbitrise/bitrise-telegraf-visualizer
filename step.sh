#!/bin/bash
set -ex

sudo pkill telegraf

pyenv install 3.12.2
pyenv local 3.12.2

pip install pandas matplotlib mpld3 plotly

python $BITRISE_STEP_SOURCE_DIR/visualize.py $telegraf_file

mkdir -p $BITRISE_HTML_REPORT_DIR/telegraf_viz/

cp resource_usage_chart.html $BITRISE_HTML_REPORT_DIR/telegraf_viz/index.html

echo "This is the value specified for the input 'example_step_input': ${example_step_input}"

envman add --key VISUALIZATION_HTML_PATH --value ${BITRISE_HTML_REPORT_DIR/telegraf_viz/index.html}
