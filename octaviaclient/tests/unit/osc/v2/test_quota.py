#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import copy
import mock

from osc_lib import exceptions

from octaviaclient.osc.v2 import quota
from octaviaclient.tests.unit.osc.v2 import fakes as qt_fakes

AUTH_TOKEN = "foobar"
AUTH_URL = "http://192.0.2.2"


class TestQuota(qt_fakes.TestLoadBalancerv2):

    _qt = qt_fakes.FakeQT.create_one_quota()

    columns = ('project_id', 'load_balancer', 'listener', 'pool',
               'health_monitor', 'member')

    datalist = (
        (
            _qt.project_id,
            _qt.load_balancer,
            _qt.listener,
            _qt.pool,
            _qt.health_monitor,
            _qt.member
        ),
    )

    info = {
        'quotas':
            [{
                "project_id": _qt.project_id,
                "load_balancer": _qt.load_balancer,
                "listener": _qt.listener,
                "pool": _qt.pool,
                "health_monitor": _qt.health_monitor,
                "member": _qt.member
            }]
    }
    qt_info = copy.deepcopy(info)

    def setUp(self):
        super(TestQuota, self).setUp()
        self.qt_mock = self.app.client_manager.load_balancer.load_balancers
        self.qt_mock.reset_mock()

        self.api_mock = mock.Mock()
        self.api_mock.quota_list.return_value = self.qt_info
        lb_client = self.app.client_manager
        lb_client.load_balancer = self.api_mock


class TestQuotaList(TestQuota):

    def setUp(self):
        super(TestQuotaList, self).setUp()
        self.cmd = quota.ListQuota(self.app, None)

    def test_quota_list_no_options(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.api_mock.quota_list.assert_called_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))


class TestQuotaShow(TestQuota):

    def setUp(self):
        super(TestQuotaShow, self).setUp()
        self.api_mock = mock.Mock()
        self.api_mock.quota_list.return_value = self.qt_info
        self.api_mock.quota_show.return_value = {
            'quota': self.qt_info['quotas'][0]}
        lb_client = self.app.client_manager
        lb_client.load_balancer = self.api_mock

        self.cmd = quota.ShowQuota(self.app, None)

    @mock.patch('octaviaclient.osc.v2.utils.get_quota_attrs')
    def test_quota_show(self, mock_attrs):
        mock_attrs.return_value = self.qt_info['quotas'][0]
        arglist = [self._qt.project_id]
        verifylist = [
            ('project', self._qt.project_id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.api_mock.quota_show.assert_called_with(
            project_id=self._qt.project_id)


class TestQuotaDefaultsShow(TestQuota):

    qt_defaults = {
        "health_monitor": 1,
        "listener": 2,
        "load_balancer": 3,
        "member": 4,
        "pool": 5
    }

    def setUp(self):
        super(TestQuotaDefaultsShow, self).setUp()

        self.api_mock = mock.Mock()
        self.api_mock.quota_defaults_show.return_value = {
            'quota': self.qt_defaults}

        lb_client = self.app.client_manager
        lb_client.load_balancer = self.api_mock

        self.cmd = quota.ShowQuotaDefaults(self.app, None)

    def test_quota_defaults_show(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        rows, data = self.cmd.take_action(parsed_args)
        data = dict(zip(rows, data))

        self.api_mock.quota_defaults_show.assert_called_with()
        self.assertEqual(self.qt_defaults, data)


class TestQuotaSet(TestQuota):

    def setUp(self):
        super(TestQuotaSet, self).setUp()
        self.api_mock = mock.Mock()
        self.api_mock.quota_set.return_value = {
            'quota': self.qt_info['quotas'][0]}
        lb_client = self.app.client_manager
        lb_client.load_balancer = self.api_mock

        self.cmd = quota.SetQuota(self.app, None)

    @mock.patch('octaviaclient.osc.v2.utils.get_quota_attrs')
    def test_quota_set(self, mock_attrs):
        mock_attrs.return_value = {
            'project_id': self._qt.project_id,
            'health_monitor': '-1',
            'listener': '1',
            'load_balancer': '2',
            'member': '3',
            'pool': '4'
        }
        arglist = [self._qt.project_id, '--healthmonitor', '-1', '--listener',
                   '1', '--loadbalancer', '2', '--member', '3', '--pool', '4']
        verifylist = [
            ('project', self._qt.project_id),
            ('health_monitor', '-1'),
            ('listener', '1'),
            ('load_balancer', '2'),
            ('member', '3'),
            ('pool', '4')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.api_mock.quota_set.assert_called_with(
            self._qt.project_id, json={'quota': {'health_monitor': '-1',
                                                 'listener': '1',
                                                 'load_balancer': '2',
                                                 'member': '3',
                                                 'pool': '4'}})

    @mock.patch('octaviaclient.osc.v2.utils.get_quota_attrs')
    def test_quota_set_no_args(self, mock_attrs):
        project_id = ['fake_project_id']
        mock_attrs.return_value = {'project_id': project_id}

        arglist = [project_id]
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)
        self.assertNotCalled(self.api_mock.quota_set)


class TestQuotaReset(TestQuota):

    def setUp(self):
        super(TestQuotaReset, self).setUp()
        self.cmd = quota.ResetQuota(self.app, None)

    @mock.patch('octaviaclient.osc.v2.utils.get_quota_attrs')
    def test_quota_reset(self, mock_attrs):
        # create new quota, otherwise other quota tests will fail occasionally
        # due to a race condition
        project_id = 'fake_project_id'
        attrs = {'project_id': project_id}
        qt_reset = qt_fakes.FakeQT.create_one_quota(attrs)

        mock_attrs.return_value = qt_reset.to_dict()

        arglist = [project_id]
        verifylist = [
            ('project', project_id)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.api_mock.quota_reset.assert_called_with(
            project_id=qt_reset.project_id)
