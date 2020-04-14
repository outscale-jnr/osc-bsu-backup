import unittest
import logging
from unittest.mock import patch
import boto3
import botocore.session
from botocore.stub import Stubber
import json
import os
import osc_bsu_backup.bsu_backup as bsu
from osc_bsu_backup.error import InputError
import tests.unit.fixtures_bsu_backup as fixtures

class TestBsuBackup(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        return

    def tearDown(self):
        logging.disable(logging.NOTSET)
        return

    def test_auth(self):
        with patch('boto3.Session'):
            self.assertTrue(bsu.auth(region="eu-west-2", profile="default", endpoint=None))

        self.assertRaises(InputError, bsu.auth, "eu-west-3", "default", None)

    def test_find_instance_by_id(self):
        ec2 = botocore.session.get_session().create_client('ec2')
        stubber = Stubber(ec2)

        response = fixtures.instances

        with Stubber(ec2) as stubber:
            stubber.add_response('describe_instances', response, {'InstanceIds': ['i-e6b7ab04']})
            for i in bsu.find_instance_by_id(ec2, "i-e6b7ab04"):
                self.assertEqual(i, "vol-a87f91c1")

        with Stubber(ec2) as stubber:
            stubber.add_response('describe_instances', {}, {'InstanceIds': ['i-e6b7ab05']})
            self.assertFalse(bsu.find_instance_by_id(ec2, "i-e6b7ab05"))

    def test_find_instances_by_tags(self):
        ec2 = botocore.session.get_session().create_client('ec2')
        stubber = Stubber(ec2)

        response = fixtures.instances

        with Stubber(ec2) as stubber:
            stubber.add_response('describe_instances', response, { 'Filters' : [{"Name": "tag:Name", "Values": ["test1"]}]} )
            for i in bsu.find_instances_by_tags(ec2, "Name:test1"):
                self.assertEqual(i, "vol-a87f91c1")

    def test_find_volume_by_id(self):
        ec2 = botocore.session.get_session().create_client('ec2')
        stubber = Stubber(ec2)

        response = fixtures.volumes

        with Stubber(ec2) as stubber:
            stubber.add_response('describe_volumes', response, {'VolumeIds': ["vol-a24fffdc"]})
            for i in bsu.find_volume_by_id(ec2, "vol-a24fffdc"):
                self.assertEqual(i, "vol-a24fffdc")

        with Stubber(ec2) as stubber:
            stubber.add_response('describe_volumes', { "Volumes": [] }, {'VolumeIds': ["vol-a24fffda"]})
            for i in bsu.find_volume_by_id(ec2, "vol-a24fffda"):
                assertEqual(i, None)

    def test_find_volumes_by_tags(self):
        ec2 = botocore.session.get_session().create_client('ec2')
        stubber = Stubber(ec2)

        response = fixtures.volumes

        with Stubber(ec2) as stubber:
            stubber.add_response('describe_volumes', response, { 'Filters' : [{"Name": "tag:Name", "Values": ["test1"]}]} )
            for i in bsu.find_volumes_by_tags(ec2, "Name:test1"):
                self.assertEqual(i, "vol-a24fffdc")

        with Stubber(ec2) as stubber:
            stubber.add_response('describe_volumes', { "Volumes": [] }, { 'Filters' : [{"Name": "tag:Name", "Values": ["abc"]}]} )
            for i in bsu.find_volumes_by_tags(ec2, "Name:abc"):
                self.assertEqual(i, None)

if __name__ == "__main__":
    unittest.main()