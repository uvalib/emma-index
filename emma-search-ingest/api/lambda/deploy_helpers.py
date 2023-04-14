import os
import subprocess
import datetime
import re
import json


EMMA_PROFILE_ID_NUMBER = os.environ.get('PROFILE_ID', '')
LAMBDA_ARN_PREFIX = "arn:aws:lambda:us-east-1:" + EMMA_PROFILE_ID_NUMBER + ":function:"


def get_commit_tag():
    """
    Get the GIT commit tag, either from CodeBuild environment or directly from git.
    """
    if os.getenv('CODEBUILD_RESOLVED_SOURCE_VERSION'):
        rev_hash = os.getenv('CODEBUILD_RESOLVED_SOURCE_VERSION')
    else:
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE)
        rev_hash = result.stdout.decode().replace('\n', '')
    return str(rev_hash)


def write_commit_details(commit_id, profile_param, s3_name):
    """
    Writes the commit details to a handy file we can upload to S3
    """
    detail_filename = 'deploy/' + commit_id + '.json'
    with open(detail_filename, "w") as outfile:
        subprocess.run(
            ['aws', 'codecommit', 'get-commit', '--repository-name', 'emma-search-ingest', '--commit-id', commit_id],
            stdout=outfile)
    print_and_run('aws s3 cp ' + profile_param + detail_filename + ' s3://' + s3_name + '/'
                  + commit_id + '/commit_detail.json')


def parse_posix_date(posix_date_str):
    """
    Used to parse the date from the aws codecommit client
    tzinfo parsing https://stackoverflow.com/questions/17976063/how-to-create-tzinfo-when-i-have-utc-offset/37097784#37097784
    """
    (posix, offset) = posix_date_str.split(' ')
    posix_timestamp = int(posix)
    sign, hours, minutes = re.match('([+\-]?)(\d{2})(\d{2})', offset).groups()
    sign = -1 if sign == '-' else 1
    hours, minutes = int(hours), int(minutes)
    tzinfo = datetime.timezone(sign * datetime.timedelta(hours=hours, minutes=minutes))
    date_obj = datetime.datetime.fromtimestamp(posix_timestamp, tzinfo)
    return date_obj.isoformat()


def write_s3_commit_tags(s3_filename, commit_id, profile_param, s3_code_bucket_name):
    """
    All this trouble just so we can see some commit information associated with the file in S3
    """
    try:
        detail_filename = 'deploy/' + commit_id + '.json'
        with open(detail_filename, "r") as detail_file:
            commit_details = json.load(detail_file)
        if commit_details :
            tag_set = {
                "TagSet":[
                    {"Key": "committer_email", "Value": commit_details['commit']['committer']['email']},
                    {"Key": "committer_name", "Value": commit_details['commit']['committer']['name']},
                    {"Key": "commit_id", "Value": commit_details['commit']['commitId']},
                    {"Key": "commit_message", "Value": commit_details['commit']['message']},
                    {"Key": "commit_date", "Value": parse_posix_date(commit_details['commit']['committer']['date'])}
                ]
            }
            #print(json.dumps(tag_set, indent=4))
            tag_set_json = json.dumps(tag_set)
            print_and_run('aws s3api put-object-tagging '+ profile_param +'--bucket ' + s3_code_bucket_name
                          + ' --key ' + commit_id + '/' + s3_filename
                          + " --tagging '" + tag_set_json + "'")
    except:
        print("[WARNING] Unable to associate commit info tags with package file in S3.")


def write_lambda_commit_tags(lambda_name, commit_id, profile_param, s3_code_bucket_name):
    """
    All this trouble just so we can see some commit information associated with the file in S3
    """
    try:
        print_and_run(
            'aws s3 cp '+ profile_param +' ' + ' s3://' + s3_code_bucket_name + '/' + commit_id + '/commit_detail.json deploy_commit_detail.json')

        with open('deploy_commit_detail.json', "r") as detail_file:
            commit_details = json.load(detail_file)
        if commit_details :
            commit_message = commit_details['commit']['message']
            commit_message = re.sub(r'[^A-Za-z0-9\-_.: ]', '', commit_message)
            lambda_tags = "committer_email=" + commit_details['commit']['committer']['email'] + "," \
                + "committer_name=" + commit_details['commit']['committer']['name'] + "," \
                + "commit_id=" + commit_details['commit']['commitId'] + "," \
                + "commit_message=" + commit_message + "," \
                + "commit_date=" + parse_posix_date(commit_details['commit']['committer']['date'])
            lambda_arn = LAMBDA_ARN_PREFIX + lambda_name
            print_and_run('aws lambda tag-resource '+ profile_param +' --resource ' + lambda_arn
                          + ' --tags "' + lambda_tags + '"')
    except:
        print("[WARNING] Unable to associate commit info tags with deployed lambda functions.")


def print_and_run(command):
    print(command + "\n")
    os.system(command)