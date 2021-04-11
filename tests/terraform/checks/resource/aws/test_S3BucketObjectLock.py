import unittest
import hcl2

from checkov.terraform.checks.resource.aws.S3BucketObjectLock import check
from checkov.common.models.enums import CheckResult


class TestS3BucketObjectLock(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                resource "aws_s3_bucket" "test" {
                      bucket = "my-tf-test-bucket"
                      acl    = "private"
                      tags = {
                        Name        = "My bucket"
                        Environment = "Dev"
                      }
                      object_lock_configuration = {
                        object_lock_enabled = "Disabled"
                      }

                }
        """)
        resource_conf = hcl_res['resource'][0]['aws_s3_bucket']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                resource "aws_s3_bucket" "test" {
                      bucket = "my-tf-test-bucket"
                      acl    = "private"
                      tags = {
                        Name        = "My bucket"
                        Environment = "Dev"
                      }
                      object_lock_configuration = {
                        object_lock_enabled = "Enabled"
                      }
                }
        """)
        resource_conf = hcl_res['resource'][0]['aws_s3_bucket']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_no_param(self):
        hcl_res = hcl2.loads("""
                resource "aws_s3_bucket" "test" {
                      bucket = "my-tf-test-bucket"
                      acl    = "private"
                    
                      tags = {
                        Name        = "My bucket"
                        Environment = "Dev"
                      }
                }
        """)
        resource_conf = hcl_res['resource'][0]['aws_s3_bucket']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_dynamic_value_object_lock(self):
        hcl_res = hcl2.loads("""
            resource "aws_s3_bucket" "test" {
              count         = local.enabled ? 1 : 0
              bucket        = module.this.id
              acl           = "private"
              tags          = module.this.tags

              dynamic "object_lock_configuration" {
                for_each = var.object_lock_enabled == true ? [local.object_lock_params] : []

                content {
                    object_lock_enabled = "Enabled"

                    rule {
                    default_retention {
                      mode  = object_lock_configuration.value.retention_mode
                      days  = object_lock_configuration.value.retention_period_days
                      years = object_lock_configuration.value.retention_period_years
                    }
                  }
                }
              }
            }
        """)
        resource_conf = hcl_res['resource'][0]['aws_s3_bucket']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()