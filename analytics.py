import time

from apiclient.discovery import build
from dynaconf import settings
from oauth2client.service_account import ServiceAccountCredentials
from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY, GaugeMetricFamily


class GoogleAnalyticsCollector():
    def __init__(self, viewid, viewname, credfile, scope):
        self.viewid = viewid
        self.viewname = viewname
        self.credfile = credfile
        self.scope = scope

    def collect(self):
        analytics = self.initialize_analyticsreporting()

        for query in settings.QUERY:
            date_range = query['date']
            metrics = query['metrics']
            dimensions = query['dimensions']

            report_response = self.get_report(analytics, metrics, dimensions, date_range)
            gauges = self.get_gauges(self.viewid, self.viewname, report_response)
            for metric in gauges:
                yield gauges[metric]

    def initialize_analyticsreporting(self):
        """Initializes an Analytics Reporting API V4 service object.

        Returns:
          An authorized Analytics Reporting API V4 service object.
        """
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.credfile, self.scope)

        # Build the service object.
        analytics = build('analyticsreporting', 'v4', credentials=credentials)

        return analytics

    def get_report(self, analytics, metrics, dimensions, date_range):

        return analytics.reports().batchGet(
            body={
              'reportRequests': [
                {
                  'viewId': str(self.viewid),
                  'dateRanges': [{'startDate': elem['start'], 'endDate': elem['end']} for elem in date_range],
                  'metrics': [{'expression': elem} for elem in metrics],
                  'dimensions': [{'name': elem} for elem in dimensions]
                }]
            }
        ).execute()

    def get_gauges(self, viewid, viewname, response):
        _gauges = {}
        for report in response.get('reports', []):
            columnHeader = report.get('columnHeader', {})
            dimensionHeaders = columnHeader.get('dimensions', [])
            metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

            labels = ['viewid', 'viewname'] + [elem[3:] for elem in dimensionHeaders]
            for metricHeader in metricHeaders:
                _gauges[metricHeader.get('name')] = GaugeMetricFamily(metricHeader.get('name')[3:], 'Description of gauge', value=None, labels=labels)

            for row in report.get('data', {}).get('rows', []):
                dimensions = row.get('dimensions', [])
                dateRangeValues = row.get('metrics', [])

                labelvalues = [str(viewid), viewname] + dimensions
                for i, values in enumerate(dateRangeValues):
                    for metricHeader, value in zip(metricHeaders, values.get('values')):
                        _gauges[metricHeader.get('name')].add_metric(labelvalues, value=value)
        return _gauges


def setup():
    for site in settings.SITES:
        REGISTRY.register(GoogleAnalyticsCollector(site['viewid'], site['name'], site['credsfile'], settings.SCOPES))
        start_http_server(8000)


if __name__ == '__main__':
    setup()
    while True:
        time.sleep(1)
