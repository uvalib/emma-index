
def copy_s3_completed(s3_resource, source_bucket, source_key, from_prefix="incoming", to_prefix="completed"):
    copy_source = {
        'Bucket': source_bucket,
        'Key': source_key
    }
    target_key = source_key.replace(from_prefix, to_prefix)
    s3_resource.Object(source_bucket, target_key).copy_from(CopySource=copy_source)
    s3_resource.Object(source_bucket, source_key).delete()