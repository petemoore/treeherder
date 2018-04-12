import { getProjectUrl } from "../helpers/urlHelper";

export default class PerfSeriesModel {
  getSeriesData(repoName, params) {
    return fetch(
      getProjectUrl('/performance/data/', repoName),
      { params }).then(function (response) {
          if (response.data) {
              return response.data;
          }
          return Promise.reject(new Error("No series data found"));
      });
  }
}
