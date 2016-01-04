# Copyright 2014 Red Hat, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import imp
import os
from oslotest import base

module_path = (os.path.dirname(os.path.realpath(__file__)) +
               '/../extra-data.d/10-merge-svc-map-files')
service_map = imp.load_source('service_map', module_path)


class TestDataMerge(base.BaseTestCase):

    nova_api_services = {
        u'nova-api': {
            u'debian': u'nova-api',
            u'default': u'openstack-nova-api'
        },
        u'nova-cert': {
            u'debian': u'nova-cert',
            u'default': u'openstack-nova-cert'
        },
        u'nova-compute': {
            u'debian': u'nova-compute',
            u'default': u'openstack-nova-compute'
        },
        u'nova-conductor': {
            u'debian': u'nova-conductor',
            u'default': u'openstack-nova-conductor'
        },
        u'nova-consoleauth': {
            u'debian': u'nova-console',
            u'default': u'openstack-nova-console'
        }
    }

    glance_api_services = {
        u'glance-api': {
            u'debian': u'glance-api',
            u'default': u'openstack-glance-api'
        },
        u'glance-reg': {
            u'debian': u'glance-reg',
            u'default': u'openstack-glance-registry'
        }
    }

    cinder_api_services = {
        u'cinder-api': {
            u'debian': u'cinder-api',
            u'default': u'openstack-cinder-api'
        },
        u'cinder-scheduler': {
            u'debian': u'cinder-scheduler',
            u'default': u'openstack-cinder-scheduler'
        }
    }

    def test_merge_data_fedora(self):

        fedora_nova_api_services = {
            u'nova-api': u'openstack-nova-api',
            u'nova-cert': u'openstack-nova-cert',
            u'nova-compute': u'openstack-nova-compute',
            u'nova-conductor': u'openstack-nova-conductor',
            u'nova-consoleauth': u'openstack-nova-console'
        }

        fedora_nova_glance_services = {
            u'nova-api': u'openstack-nova-api',
            u'nova-cert': u'openstack-nova-cert',
            u'nova-compute': u'openstack-nova-compute',
            u'nova-conductor': u'openstack-nova-conductor',
            u'nova-consoleauth': u'openstack-nova-console',
            u'glance-api': u'openstack-glance-api',
            u'glance-reg': u'openstack-glance-registry'
        }

        fedora_nova_glance_cinder_services = {
            u'nova-api': u'openstack-nova-api',
            u'nova-cert': u'openstack-nova-cert',
            u'nova-compute': u'openstack-nova-compute',
            u'nova-conductor': u'openstack-nova-conductor',
            u'nova-consoleauth': u'openstack-nova-console',
            u'glance-api': u'openstack-glance-api',
            u'glance-reg': u'openstack-glance-registry',
            u'cinder-api': u'openstack-cinder-api',
            u'cinder-scheduler': u'openstack-cinder-scheduler',
        }

        result = dict()
        result = service_map.merge_data(self.nova_api_services,
                                        result,
                                        "fedora")

        self.assertDictEqual(result,
                             fedora_nova_api_services,
                             "Merge failed")

        result = service_map.merge_data(self.glance_api_services,
                                        result,
                                        "fedora")

        self.assertDictEqual(result,
                             fedora_nova_glance_services,
                             "Merge failed")

        result = service_map.merge_data(self.cinder_api_services,
                                        result,
                                        "fedora")
        self.assertDictEqual(result,
                             fedora_nova_glance_cinder_services,
                             "Merge failed")

    def test_merge_data_ubuntu(self):

        ubuntu_nova_api_services = {
            u'nova-api': u'nova-api',
            u'nova-cert': u'nova-cert',
            u'nova-compute': u'nova-compute',
            u'nova-conductor': u'nova-conductor',
            u'nova-consoleauth': u'nova-console'
        }

        ubuntu_nova_glance_services = {
            u'nova-api': u'nova-api',
            u'nova-cert': u'nova-cert',
            u'nova-compute': u'nova-compute',
            u'nova-conductor': u'nova-conductor',
            u'nova-consoleauth': u'nova-console',
            u'glance-api': u'glance-api',
            u'glance-reg': u'glance-reg'
        }

        ubuntu_nova_glance_cinder_services = {
            u'nova-api': u'nova-api',
            u'nova-cert': u'nova-cert',
            u'nova-compute': u'nova-compute',
            u'nova-conductor': u'nova-conductor',
            u'nova-consoleauth': u'nova-console',
            u'glance-api': u'glance-api',
            u'glance-reg': u'glance-reg',
            u'cinder-api': u'cinder-api',
            u'cinder-scheduler': u'cinder-scheduler'
        }

        result = dict()
        result = service_map.merge_data(self.nova_api_services,
                                        result,
                                        "ubuntu")

        self.assertDictEqual(result,
                             ubuntu_nova_api_services,
                             "Merge failed")

        result = service_map.merge_data(self.glance_api_services,
                                        result,
                                        "ubuntu")

        self.assertDictEqual(result,
                             ubuntu_nova_glance_services,
                             "Merge failed")

        result = service_map.merge_data(self.cinder_api_services,
                                        result,
                                        "ubuntu")

        self.assertDictEqual(result,
                             ubuntu_nova_glance_cinder_services,
                             "Merge failed")
