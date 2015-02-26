# Copyright (c) 2013 Keedio, Inc.
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

from sahara.plugins import provisioning as p

class OpenbusProvider(p.ProvisioningPluginBase):

    # Ok
    def get_versions(self):
        pass

    # Ok
    def get_configs(self, hadoop_version):
        pass

    # Ok
    def get_node_processes(self, hadoop_version):
        pass

    def configure_cluster(self, cluster):
        pass

    def start_cluster(self, cluster):
        pass

    def scale_cluster(self, cluster, instances):
        pass

    def decommission_nodes(self, cluster, instances):
        pass

    def convert(self, config, plugin_name, version, template_name,
                cluster_template_create):
        pass

    def update_infra(self, cluster):
        pass