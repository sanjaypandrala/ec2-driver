import unittest
import time

from novaclient.v1_1 import client
from ..credentials import get_nova_creds

from boto import ec2
from ..ec2driver_config import *


class TestPowerOff(unittest.TestCase):

    def setUp(self):
        print "Establishing connection with AWS"
        self.ec2_conn = ec2.connect_to_region(aws_region, aws_access_key_id=aws_access_key_id,
                                              aws_secret_access_key=aws_secret_access_key)
        self.creds = get_nova_creds()

    # @unittest.skip("For fun")
    def test_power_off(self):
        print "Spawning an instance"
        nova = client.Client(**self.creds)
        image = nova.images.find(name="cirros-0.3.1-x86_64-uec")
        flavor = nova.flavors.find(name="m1.tiny")
        self.server = nova.servers.create(name="cirros-test", image=image.id, flavor=flavor.id)
        instance = nova.servers.get(self.server.id)
        while instance.status != 'ACTIVE':
            time.sleep(10)
            instance = nova.servers.get(self.server.id)


        #Send poweroff to the instance
        nova.servers.stop(instance)

        while instance.status != 'SHUTOFF':
            time.sleep(5)
            instance = nova.servers.get(self.server.id)
            print "while: %s" % instance.status
        instance = nova.servers.get(self.server.id)
        print "Status after POWEROFF ing: %s" % instance.status

        #assert power off
        ec2_instance = self.ec2_conn.get_only_instances(instance_ids=[self.server.metadata['ec2_id']], filters=None,
                                                        dry_run=False, max_results=None)[0]
        self.assertEqual(ec2_instance.state, "stopped")

    def tearDown(self):
        print "Cleanup: Destroying the instance used for testing"
        self.server.delete()

if __name__ == '__main__':
    unittest.main()