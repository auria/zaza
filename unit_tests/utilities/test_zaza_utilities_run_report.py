# Copyright 2019 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock

import unit_tests.utils as ut_utils
import zaza.utilities.run_report as run_report


class TestUtilitiesRunReport(ut_utils.BaseTestCase):

    def setUp(self):
        super(TestUtilitiesRunReport, self).setUp()
        run_report.reset_run_data()

    def test_register_event(self):
        run_report.register_event(
            'Deploy Bundle',
            run_report.EventStates.START,
            timestamp=10)
        run_report.register_event(
            'Deploy Bundle',
            run_report.EventStates.FINISH,
            timestamp=12)
        self.assertEqual(
            run_report.get_events(),
            {
                'Deploy Bundle': {
                    'Finish': 12, 'Start': 10}})

    def test_register_metadata(self):
        run_report.register_metadata(
            cloud_name='cloud1',
            model_name='model2',
            target_bundle='precise-essex')
        self.assertEqual(
            run_report.get_metadata(),
            {
                'cloud_name': 'cloud1',
                'model_name': 'model2',
                'target_bundle': 'precise-essex'})

    def test_get_events_start_stop_time(self):
        events = {
            'event1': {'start': 12, 'finish': 18},
            'event2': {'start': 10, 'finish': 15},
            'event3': {'start': 15, 'finish': 28},
        }
        self.assertEqual(
            run_report.get_events_start_stop_time(events),
            (10, 28))

    def test_get_event_report(self):
        run_report.register_metadata(
            cloud_name='cloud1',
            model_name='model2',
            target_bundle='precise-essex')
        run_report.register_event(
            'Deploy Bundle',
            run_report.EventStates.START,
            timestamp=10)
        run_report.register_event(
            'Deploy Bundle',
            run_report.EventStates.FINISH,
            timestamp=12)
        self.assertEqual(
            run_report.get_event_report(),
            {
                'Events': {
                    'Deploy Bundle': {
                        'Elapsed Time': 2,
                        'Finish': 12,
                        'PCT Of Run Time': 100,
                        'Start': 10}},
                'Metadata': {
                    'cloud_name': 'cloud1',
                    'model_name': 'model2',
                    'target_bundle': 'precise-essex'}})

    def test_write_event_report(self):
        self.patch_object(run_report.logging, 'info')
        self.patch_object(
            run_report,
            'get_event_report',
            return_value={'myreport': 'thereport'})
        run_report.write_event_report()
        self.info.assert_called_once_with(
            'myreport: thereport\n')

    def test_write_event_report_output_file(self):
        self.patch_object(run_report.logging, 'info')
        self.patch_object(
            run_report,
            'get_event_report',
            return_value={'myreport': 'thereport'})
        open_mock = mock.mock_open()
        with mock.patch('zaza.utilities.run_report.open', open_mock,
                        create=False):
            run_report.write_event_report(output_file='/tmp/summary.yaml')
        self.info.assert_called_once_with(
            'myreport: thereport\n')
        open_mock.assert_called_once_with('/tmp/summary.yaml', 'w')
        handle = open_mock()
        handle.write.assert_called_once_with('myreport: thereport\n')

    def test_get_run_data(self):
        run_report.register_event(
            'Deploy Bundle',
            run_report.EventStates.START,
            timestamp=10)
        self.assertEqual(
            run_report.get_run_data(),
            run_report.run_data)

    def test_reset_run_data(self):
        run_report.register_event(
            'Deploy Bundle',
            run_report.EventStates.START,
            timestamp=10)
        run_report.reset_run_data()
        self.assertEqual(
            run_report.get_run_data(),
            {'Events': {}, 'Metadata': {}})
