import os
import logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "treeherder.config.settings")
import django  # noqa: E402
django.setup()

from progress.bar import Bar  # noqa: E402

from treeherder.model.models import Bugscache, OtherTextLogError  # noqa: E402


logging.basicConfig(filename='search.log')
logger = logging.getLogger(__name__)

# This runs the following query for each line in the OtherTextLogError
# SELECT *
#   FROM bugscache
#  WHERE to_tsvector(COALESCE(`bugscache`.`summary`, )) @@ (plainto_tsquery(00:22:58    ERROR - Return code: 1)) = true


Bugscache = Bugscache.objects.using('pg')
OtherTextLogError = OtherTextLogError.objects.using('pg')

bar = Bar('Searching', max=OtherTextLogError.count(), suffix='%(index)s/%(max)s (%(percent)d%%) AVG: %(avg)s ETA: %(eta_td)s')

for log in bar.iter(OtherTextLogError.iterator()):
    bugs = Bugscache.filter(summary__search=log.line)
    bug_count = bugs.count()

    if bug_count > 0:
        bug_ids = ','.join(str(b.id) for b in bugs)
        logger.info('text_log_error={} bugs={} |--> {}'.format(log.pk, bug_ids, log.line))
