# EMMA HathiTrust file handlers

This project contains projects used to handle the HathiTrust file uploads to 
the EMMA/Bookshare Federated/Unified Search project.

* batch_trigger_lambda: lambda function which launches an AWS batch job to break down big files
* aws_batch: batch script which breaks down one big S3 file into many small S3 files.
* get_hathi_file_lambda: retrieve file from HathiTrust website and save to S3.