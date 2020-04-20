import time

from apiclient.discovery import build
from dynaconf import settings
from oauth2client.service_account import ServiceAccountCredentials
from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY, GaugeMetricFamily


class GoogleAnalyticsCollector():
    def __init__(self, sites):
        self.sites = sites

    def collect(self):
        for site in self.sites:
            analytics = self.initialize_analyticsreporting(site)
            for query in settings.QUERY:
                date_range = query['date']
                metrics = query['metrics']
                dimensions = query['dimensions']

                report_response = self.get_report(site['viewid'], analytics, metrics, dimensions, date_range)
                gauges = self.get_gauges(site['viewid'], site['viewname'], query['name'], report_response)
                for metric in gauges:
                    yield gauges[metric]


    def initialize_analyticsreporting(self, site):
        credfile = site['credsfile']
        scopes = site['scopes']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            credfile, scopes)

        analytics = build('analyticsreporting', 'v4', credentials=credentials)

        return analytics

    def get_report(self, viewid, analytics, metrics, dimensions, date_range):

        return analytics.reports().batchGet(
            body={
              'reportRequests': [
                {
                  'viewId': str(viewid),
                  'dateRanges': [{'startDate': elem['start'], 'endDate': elem['end']} for elem in date_range],
                  'metrics': [{'expression': elem} for elem in metrics],
                  'dimensions': [{'name': elem} for elem in dimensions]
                }]
            }
        ).execute()

    def get_gauges(self, viewid, viewname, queryname, response):
        _gauges = {}
        for report in response.get('reports', []):
            columnHeader = report.get('columnHeader', {})
            dimensionHeaders = columnHeader.get('dimensions', [])
            metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

            labels = ['viewid', 'viewname', 'queryname'] + [elem[3:] for elem in dimensionHeaders]
            for metricHeader in metricHeaders:
                _gauges[metricHeader.get('name')] = GaugeMetricFamily("ga_" + metricHeader.get('name')[3:], 'Description of gauge', value=None, labels=labels)

            for row in report.get('data', {}).get('rows', []):
                dimensions = row.get('dimensions', [])
                dateRangeValues = row.get('metrics', [])

                labelvalues = [str(viewid), viewname, queryname] + dimensions
                for i, values in enumerate(dateRangeValues):
                    for metricHeader, value in zip(metricHeaders, values.get('values')):
                        _gauges[metricHeader.get('name')].add_metric(labelvalues, value=value)
        return _gauges


def setup():
    REGISTRY.register(GoogleAnalyticsCollector(settings.SITES))
    start_http_server(8000)


if __name__ == '__main__':
    setup()
    while True:
        time.sleep(1)
