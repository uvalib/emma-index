import sys
import os
import boto3
import gzip
from datetime import datetime, timezone
from io import TextIOWrapper, BytesIO


def get_base_filename(filepath):
    return os.path.splitext(filepath)[0]


def get_chunk_bucket(bucket_format, count):
    return bucket_format.format(str(count).zfill(8))


def get_source_iterator(format, s3_reader, source_bucket, source_key):
    if 'gzip' == format:
        return get_gzip_iterator(s3_reader, source_bucket, source_key)
    else:
        return get_text_iterator(s3_reader, source_bucket, source_key)


def get_text_iterator(s3_reader, source_bucket, source_key):
    return s3_reader.Object(source_bucket, source_key).get()['Body'].iter_lines()


def get_gzip_iterator(s3_reader, source_bucket, source_key):
    response = s3_reader.Object(source_bucket, source_key).get()
    # if gzipped
    gzipped = gzip.GzipFile(None, 'rb', fileobj=response['Body'])
    return TextIOWrapper(gzipped)


def get_new_chunk_target():
    return BytesIO()


def put_chunk(format, s3_writer, chunk_target_body, chunk_target_bucket, chunk_filename_format, count):
    if 'gzip' == format:
        put_gzip_chunk(s3_writer, chunk_target_body, chunk_target_bucket, chunk_filename_format, count)
    else:
        put_text_chunk(s3_writer, chunk_target_body, chunk_target_bucket, chunk_filename_format, count)


def put_gzip_chunk(s3_writer, chunk_target_body, chunk_target_bucket, chunk_filename_format, count):
    gz_body = BytesIO()
    gz = gzip.GzipFile(None, 'wb', 9, gz_body)
    gz.write(chunk_target_body.getvalue())  # convert unicode strings to bytes!
    gz.close()
    # GzipFile has written the compressed bytes into our gz_body
    s3_writer.put_object(
        Bucket=chunk_target_bucket,
        Key=get_chunk_bucket(chunk_filename_format, count),  # Note: NO .gz extension!
        ContentType='text/plain',  # the original type
        ContentEncoding='gzip',  # MUST have or browsers will error
        Body=gz_body.getvalue()
    )
    chunk_target_body.close()


def put_text_chunk(s3_writer, chunk_target_body, chunk_target_bucket, chunk_filename_format, count):
    s3_writer.put_object(
        Bucket=chunk_target_bucket,
        Key=get_chunk_bucket(chunk_filename_format, count),
        ContentType='text/plain',
        Body=chunk_target_body.getvalue()
    )
    chunk_target_body.close()

def mv_s3_completed(s3_resource, source_bucket, source_key):
    copy_source = {
        'Bucket': source_bucket,
        'Key': source_key
    }
    target_key = source_key.replace("incoming", "completed")
    s3_resource.Object(source_bucket, target_key).copy_from(CopySource=copy_source)
    s3_resource.Object(source_bucket, source_key).delete()

def main():
    start_time = datetime.utcnow()

    source_bucket = None
    source_key = None
    target_bucket = None
    target_key_basename = None
    lines_per_file = 500
    output_format = "gzip"
    print_first_x_lines = 10

    GOLDEN_KEY = os.environ.get('GOLDEN_KEY', 'unset')

    if len(sys.argv) > 1:
        source_bucket = sys.argv[1]
    if len(sys.argv) > 2:
        source_key = sys.argv[2]
    if len(sys.argv) > 3:
        target_bucket = sys.argv[3]
    if len(sys.argv) > 4:
        target_key_basename = sys.argv[4]
    if len(sys.argv) > 5:
        lines_per_file = int(sys.argv[5])
    if len(sys.argv) > 6:
        output_format = sys.argv[6]

    if None in (source_bucket, source_key, target_bucket, target_key_basename):
        print("Usage:")
        print("")
        print("aws_batch.py [source bucket] [source key] [target bucket] [target key] [lines per file] [output format]")
        print("")
        print("where target and key information are required, but lines per file and output format are optional")
        exit(0)

    # Print statements in this docker container will go to cloudwatch
    print("Source bucket: " + str(source_bucket))
    print("Source key: " + str(source_key))
    print("Target bucket: " + str(target_bucket))
    print("Target key basename: " + str(target_key_basename))
    print("Lines per file: " + str(lines_per_file))
    print("Output format: " + str(output_format))
    print("Start time: " + start_time.strftime("%Y-%m-%dT%H:%M:%SZ"))

    chunk_key_format = target_key_basename + '-chunk-{0}.txt'

    if 'dev' == GOLDEN_KEY:
        s3_session = boto3.session.Session(profile_name='emma')
    else:
        s3_session = boto3.session.Session()
    s3_resource = s3_session.resource('s3')
    s3_writer = s3_session.client('s3')

    count = 0
    file_count = 0
    chunk_target_body = get_new_chunk_target()
    iterator = get_source_iterator("gzip", s3_resource, source_bucket, source_key)
    for line in iterator:
        count = count + 1
        if count < print_first_x_lines:
            print(line)
        chunk_target_body.write(line.encode('utf-8'))
        if count % lines_per_file == 0:
            file_count = file_count + 1
            print("Writing file " + get_chunk_bucket(chunk_key_format, count // lines_per_file), flush=True)
            put_chunk(output_format, s3_writer, chunk_target_body, target_bucket, chunk_key_format, count // lines_per_file)
            chunk_target_body = get_new_chunk_target()
    if chunk_target_body.getvalue() is not None and len(chunk_target_body.getvalue()) > 0:
        put_chunk(output_format, s3_writer, chunk_target_body, target_bucket, chunk_key_format, count // lines_per_file)
        file_count = file_count + 1
    mv_s3_completed(s3_resource, source_bucket, source_key)

    print("Number of files: " + str(file_count))
    print("Number of lines: " + str(count))
    print("Script completed")
    end_time = datetime.utcnow()
    print("End time: " + end_time.strftime("%Y-%m-%dT%H:%M:%SZ"))
    delta = end_time - start_time
    print("Elapsed: " + str(delta))



if __name__ == '__main__':
    main()
