import logging

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch_dsl import (Boolean,
                               DocType,
                               Integer,
                               Search,
                               Text,
                               analyzer,
                               tokenizer)
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.query import Match as ESMatch
from six import string_types

from treeherder.model.models import FailureLine, Job

logger = logging.getLogger(__name__)

connection = connections.create_connection()

failure_lines = FailureLine.objects.exclude(message=None).exclude(message='')

# Tokenizer that splits on tokens matching a hex number
# a decimal number, or anything non-alphanumeric.
message_tokenizer = tokenizer(
    'message_tokenizer',
    'pattern',
    pattern=r"0x[0-9a-fA-F]+|[\W0-9]+?",
)

message_analyzer = analyzer(
    'message_analyzer',
    type="custom",
    tokenizer=message_tokenizer,
    filters=[],
)


class FailureLineIndex(DocType):
    """
    DocType representing a test with an unexpected result and an error message
    """
    job_guid = Text(required=True, index='not_analyzed')
    test = Text(required=True, index='not_analyzed')
    subtest = Text(index='not_analyzed')
    status = Text(required=True, index='not_analyzed')
    expected = Text(required=True, index='not_analyzed')
    best_classification = Integer(index='not_analyzed')
    best_is_verified = Boolean(index='not_analyzed')
    message = Text()

    class Meta:
        index = 'failure-line'

    @classmethod
    def from_model(cls, line):
        """Create a FailureLineIndex object from a FailureLine model instance."""
        if line.action != "test_result":
            return

        if not isinstance(line.test, string_types):
            # Reftests used to use tuple indicies, which we can't support
            # this is fixed upstream, but we also need to handle it here to allow
            # for older branches.
            return

        doc = cls(
            meta={'id': line.id},
            job_guid=line.job_guid,
            test=line.test,
            subtest=line.subtest,
            status=line.status,
            expected=line.expected,
            message=line.message,
            # best_classification=line.best_classification_id,
            best_is_verified=line.best_is_verified,
        )
        doc.save()
        return doc.to_dict(include_meta=True)


def run():
    # Delete and reinitialise the index
    connection.indices.delete(FailureLineIndex._doc_type.index, ignore=404)
    FailureLineIndex.init()

    actions = (FailureLineIndex.from_model(fl) for fl in failure_lines)
    actions = (x for x in actions if x)
    client = Elasticsearch()
    count, _ = bulk(client=client, actions=actions)
    print('Inserted {} documents from {} FailureLines'.format(count, len(failure_lines)))

    for failure_line in failure_lines:
        match = ESMatch(message={"query": failure_line.message[:1024],
                                 "type": "phrase"})

        # what type of query do these generate?
        # are they boolean'd together?
        s = (Search().using(client)
                     .filter("term", test=failure_line.test)
                     .filter("term", status=failure_line.status)
                     .filter("term", expected=failure_line.expected)
                     .filter("exists", field="best_classification")
                     .query(match))

        if failure_line.subtest:
            s = s.filter("term", subtest=failure_line.subtest)

        print(s.to_dict())

        try:
            resp = s.execute()
        except Exception as e:
            if not Job.objects.filter(guid=failure_line.job_guid).exists():
                print('No job found for Failure Line: {}'.format(failure_line.id))
            continue

        if len(resp) > 0:
            print('{} | {}'.format(len(resp), failure_line.message))
            print('')

    # s = Search().filter('term', author=author)
    # response = s.execute()
    # return response

    # Iterate over the lines trying to find themselves/close to themselves


if __name__ == '__main__':
    run()
