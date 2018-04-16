import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "treeherder.config.settings")

import django  # noqa: E402
django.setup()

from django.core.management import call_command  # noqa: E402


tables = [
    'build_platform',
    'failure_classification',
    'job_group',
    'job_type',
    'machine_platform',
    'machine',
    'product',
    'repository_group',
    'repository',
    'push',
    'reference_data_signatures',

    'failure_line',
    'job',
    'text_log_step',
    'text_log_error',
]
for table in tables:
    call_command('loaddata', 'dumps/{}.json'.format(table))
