import logging
import sys
import os

DEVOPS_LOG_LEVEL = None

if 'DEVOPS_LOG_LEVEL' in os.environ:
    DEVOPS_LOG_LEVEL = os.environ['DEVOPS_LOG_LEVEL']
else:
    DEVOPS_LOG_LEVEL = logging.INFO

logging.basicConfig(level=DEVOPS_LOG_LEVEL,
                    stream=sys.stderr,
                    format='%(asctime)s %(name)s %(levelname)-5s %(message)s')

HpiLogger: logging.Logger = logging.getLogger('hpi')
