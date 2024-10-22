#!/bin/bash
set -ex

sudo pkill telegraf

pyenv install 3.12.2
pyenv local 3.12.2

pip install pandas matplotlib mpld3 plotly

echo $telegraf_dir
python $BITRISE_STEP_SOURCE_DIR/visualize.py $telegraf_dir

mkdir -p $BITRISE_HTML_REPORT_DIR/telegraf_viz/

cp resource_usage_chart.html $BITRISE_HTML_REPORT_DIR/telegraf_viz/index.html

envman add --key VISUALIZATION_HTML_PATH --value ${BITRISE_HTML_REPORT_DIR/telegraf_viz/index.html}