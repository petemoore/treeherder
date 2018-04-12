import PropTypes from 'prop-types';
import treeherder from "../js/treeherder";

function PerformanceTab(props) {
  const { repoName, revision, perfJobDetail } = props;
  console.log("perfJobDetail", perfJobDetail);
  const sortedDetails = perfJobDetail ? perfJobDetail.slice() : [];
  sortedDetails.sort((a, b) => a.title.localeCompare(b.title));
  // order by 'title'

  return (
    <div className="performance-panel">
      {!!sortedDetails.length && <ul>
        <li>Perfherder:
          {sortedDetails.map((detail, idx) => (
            <ul
              key={idx} // eslint-disable-line react/no-array-index-key
            >
              <li>{detail.title}:
                <a href={detail.url}>{detail.value}</a>
              </li>
            </ul>
          ))}
        </li>
      </ul>}
      <ul>
        <li>
          <a
            href={`perf.html#/comparechooser?newProject=${repoName}&newRevision=${revision}`}
            target="_blank"
            rel="noopener"
          >Compare result against another revision</a>
        </li>
      </ul>
    </div>
  );
}

PerformanceTab.propTypes = {
  repoName: PropTypes.string.isRequired,
  revision: PropTypes.string,
  perfJobDetail: PropTypes.array,
};

PerformanceTab.defaultProps = {
  revision: '',
  perfJobDetail: null,
};

treeherder.directive('performanceTab', ['reactDirective', reactDirective =>
  reactDirective(PerformanceTab, undefined, {}, {})]);
