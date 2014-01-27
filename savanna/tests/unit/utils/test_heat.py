# Copyright (c) 2013 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import unittest2

from savanna.tests.unit.plugins.general import test_utils as tu
from savanna.utils import files as f
from savanna.utils.openstack import heat as h


class TestHeat(unittest2.TestCase):
    def test_gets(self):
        inst_name = "cluster-worker-001"
        self.assertEqual(h._get_inst_name("cluster", "worker", 0), inst_name)
        self.assertEqual(h._get_port_name(inst_name),
                         "cluster-worker-001-port")
        self.assertEqual(h._get_floating_name(inst_name),
                         "cluster-worker-001-floating")
        self.assertEqual(h._get_volume_name(inst_name, 1),
                         "cluster-worker-001-volume-1")
        self.assertEqual(h._get_volume_attach_name(inst_name, 1),
                         "cluster-worker-001-volume-attachment-1")

    def test_prepare_user_data(self):
        userdata = "line1\nline2"
        self.assertEqual(h._prepare_userdata(userdata), '"line1",\n"line2"')

    def test_get_anti_affinity_scheduler_hints(self):
        inst_names = ['i1', 'i2']
        expected = '"scheduler_hints" : {"different_host": ' \
                   '[{"Ref": "i1"}, {"Ref": "i2"}]},'
        actual = h._get_anti_affinity_scheduler_hints(inst_names)
        self.assertEqual(expected, actual)

        inst_names = ['i1', 'i1']
        expected = '"scheduler_hints" : {"different_host": [{"Ref": "i1"}]},'
        actual = h._get_anti_affinity_scheduler_hints(inst_names)
        self.assertEqual(expected, actual)

        inst_names = []
        expected = ''
        actual = h._get_anti_affinity_scheduler_hints(inst_names)
        self.assertEqual(expected, actual)


class TestClusterTemplate(unittest2.TestCase):
    """This test checks valid structure of Resources
       section in Heat templates generated by Savanna:
       1. It checks templates generation with different OpenStack
       network installations: Neutron, NovaNetwork with floating Ip auto
       assignment set to True or False.
       2. Cinder volume attachments.
       3. Basic instances creations with multi line user data provided.
       4. Anti-affinity feature with proper nova scheduler hints included
       into Heat templates.
    """

    def test_load_template_use_neutron(self):
        """This test checks Heat cluster template with Neutron enabled.
           Two NodeGroups used: 'master' with Ephemeral drive attached and
           'worker' with 2 attached volumes 10GB size each
        """

        ng1 = tu._make_ng_dict('master', 42, ['namenode'], 1,
                               floating_ip_pool='floating', image_id=None,
                               volumes_per_node=0, volumes_size=0, id=1)
        ng2 = tu._make_ng_dict('worker', 42, ['datanode'], 1,
                               floating_ip_pool='floating', image_id=None,
                               volumes_per_node=2, volumes_size=10, id=2)
        cluster = tu._create_cluster("cluster", "tenant1", "general",
                                     "1.2.1", [ng1, ng2],
                                     user_keypair_id='user_key',
                                     neutron_management_network='private_net',
                                     default_image_id='1', anti_affinity=[],
                                     image_id=None)
        heat_template = h.ClusterTemplate(cluster)
        heat_template.add_node_group_extra(ng1['id'], 1, 'line1\nline2')
        heat_template.add_node_group_extra(ng2['id'], 1, 'line2\nline3')

        h.CONF.set_override("use_neutron", True)
        try:
            main_template = h._load_template(
                'main.heat', {'resources':
                              heat_template._serialize_resources()})

            self.assertEqual(
                json.loads(main_template),
                json.loads(f.get_file_text(
                    "tests/unit/resources/"
                    "test_serialize_resources_use_neutron.heat")))
        finally:
            h.CONF.clear_override("use_neutron")

    def test_load_template_with_anti_affinity_single_ng(self):
        """This test checks Heat cluster template with Neutron enabled
           and anti-affinity feature enabled for single node process
           in single node group.
        """

        ng1 = tu._make_ng_dict('master', 42, ['namenode'], 1,
                               floating_ip_pool='floating', image_id=None,
                               volumes_per_node=0, volumes_size=0, id=1)
        ng2 = tu._make_ng_dict('worker', 42, ['datanode'], 2,
                               floating_ip_pool='floating', image_id=None,
                               volumes_per_node=0, volumes_size=0, id=2)
        cluster = tu._create_cluster("cluster", "tenant1", "general",
                                     "1.2.1", [ng1, ng2],
                                     user_keypair_id='user_key',
                                     neutron_management_network='private_net',
                                     default_image_id='1',
                                     anti_affinity=['datanode'], image_id=None)
        aa_heat_template = h.ClusterTemplate(cluster)
        aa_heat_template.add_node_group_extra(ng1['id'], 1, 'line1\nline2')
        aa_heat_template.add_node_group_extra(ng2['id'], 2, 'line2\nline3')

        h.CONF.use_neutron = True

        main_template = h._load_template(
            'main.heat', {'resources':
                          aa_heat_template._serialize_resources()})

        self.assertEqual(
            json.loads(main_template),
            json.loads(f.get_file_text(
                "tests/unit/resources/"
                "test_serialize_resources_aa.heat")))
