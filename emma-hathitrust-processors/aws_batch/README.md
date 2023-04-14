# Chunkinator batch

This batch file loops through the incoming file and breaks it into smaller files.
It sends these smaller files to another S3 bucket.

## Rebuilding the Docker image

Prerequisite: Log on to EMMA role (one method)

```shell script
bks-aws-mfa  
source ~/.bks-aws-mfa
```

Build, tag, and push the image
```shell script
docker build -t emma/hathitrust-bigfiles-handler .
docker tag emma/hathitrust-bigfiles-handler:latest 002481031907.dkr.ecr.us-east-1.amazonaws.com/emma/hathitrust-bigfiles-handler:latest
aws ecr get-login --no-include-email --profile emma
docker login -u AWS ... (result of previous command)
docker push 002481031907.dkr.ecr.us-east-1.amazonaws.com/emma/hathitrust-bigfiles-handler:latest
```

## Command line parameters

Example:

Source bucket: hathitrust-bigfiles-qa

Source key: hathi_full_20200401.txt.gz

Target bucket: hathitrust-upload-qa

Target key basename: incoming/hathi_full_20200101
