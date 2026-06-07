

set -eux


rm -rf $VIRTUAL_ENV/lib/python3.*/site-packages/devops_tools*
rm -rf ./*.egg-info
rm -rf ./build

pip install --no-cache-dir  .[dev] -vv

find $VIRTUAL_ENV -name '*.sh'