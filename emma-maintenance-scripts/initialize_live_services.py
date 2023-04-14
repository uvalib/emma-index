from initialize_scripts.live.lambda_functions.policies.emma_prod_allow_add_remove_eventbridge_targets import create as emma_prod_allow_add_remove_eventbridge_targets
from initialize_scripts.live.lambda_functions.policies.emma_prod_allow_full_batch_access import create as emma_prod_allow_full_batch_access
from initialize_scripts.live.lambda_functions.policies.emma_prod_allow_full_hathitrust_s3_access import create as emma_prod_allow_full_hathitrust_s3_access
from initialize_scripts.live.lambda_functions.policies.emma_prod_allow_full_incoming_metadata_sqs import create as emma_prod_allow_full_incoming_metadata_sqs
from initialize_scripts.live.lambda_functions.policies.emma_prod_allow_full_s3_access import create as emma_prod_allow_full_s3_access
from initialize_scripts.live.lambda_functions.policies.emma_prod_allow_update_api_gateway_targets import create as emma_prod_allow_update_api_gateway_targets
from initialize_scripts.live.lambda_functions.policies.emma_prod_allow_update_dynamodb_tables import create as emma_prod_allow_update_dynamodb_tables
from initialize_scripts.live.lambda_functions.policies.emma_prod_allow_update_event_source_mappings import create as emma_prod_allow_update_event_source_mappings
from initialize_scripts.live.lambda_functions.roles.emma_prod_lambda_batch_role import create as emma_prod_lambda_batch_role
from initialize_scripts.live.lambda_functions.roles.emma_prod_lambda_incoming_metadata_s3_sqs_role import create as emma_prod_lambda_incoming_metadata_s3_sqs_role
from initialize_scripts.live.lambda_functions.roles.emma_prod_lambda_maintenance_role import create as emma_prod_lambda_maintenance_role
from initialize_scripts.live.lambda_functions.roles.emma_prod_lambda_s3_dynamodb_role import create as emma_prod_lambda_s3_dynamodb_role
from initialize_scripts.live.lambda_functions.roles.emma_prod_lambda_update_dynamodb_role import create as emma_prod_lambda_update_dynamodb_role
from initialize_scripts.live.lambda_functions.roles.emma_prod_lambda_vpc_execution_role import create as emma_prod_lambda_vpc_execution_role
from initialize_scripts.live.dynamo.emma_bookshare_loader import create as emma_bookshare_loader
from initialize_scripts.live.dynamo.hathitrust_retrieval import create as hathitrust_retrieval
from initialize_scripts.live.sqs.incoming_metadata_to_process import create as incoming_metadata_to_process
from initialize_scripts.live.sqs.incoming_metadata_to_process_dlq import create as incoming_metadata_to_process_dlq
from initialize_scripts.live.lambda_functions.bookshare_scan import create as bookshare_scan
from initialize_scripts.live.lambda_functions.emma_bring_online import create as emma_bring_online
from initialize_scripts.live.lambda_functions.emma_ingest_delete import create as emma_ingest_delete
from initialize_scripts.live.lambda_functions.emma_ingest_get import create as emma_ingest_get
from initialize_scripts.live.lambda_functions.emma_ingest_put import create as emma_ingest_put
from initialize_scripts.live.lambda_functions.emma_maintenance_message import create as emma_maintenance_message
from initialize_scripts.live.lambda_functions.emma_publish_counts import create as emma_publish_counts
from initialize_scripts.live.lambda_functions.emma_search_get import create as emma_search_get
from initialize_scripts.live.lambda_functions.emma_take_offline import create as emma_take_offline
from initialize_scripts.live.lambda_functions.hathitrust_batch_trigger import create as hathitrust_batch_trigger
from initialize_scripts.live.lambda_functions.hathitrust_get_file import create as hathitrust_get_file
from initialize_scripts.live.lambda_functions.hathitrust_retry import create as hathitrust_retry
from initialize_scripts.live.lambda_functions.hathitrust_scan import create as hathitrust_scan
from initialize_scripts.live.lambda_functions.internet_archive_scan import create as internet_archive_scan
from initialize_scripts.live.s3_buckets.hathitrust_bigfiles import create as hathitrust_bigfiles
from initialize_scripts.live.s3_buckets.hathitrust_upload import create as hathitrust_upload
from initialize_scripts.live.batch.roles.emma_prod_batch_s3_role import create as emma_prod_batch_s3_role



env = 'prod'



# # Policies
# emma_prod_allow_add_remove_eventbridge_targets(env)
# emma_prod_allow_full_batch_access(env)
# emma_prod_allow_full_hathitrust_s3_access(env)
# emma_prod_allow_full_incoming_metadata_sqs(env)
# emma_prod_allow_full_s3_access(env)
# emma_prod_allow_update_api_gateway_targets(env)
# emma_prod_allow_update_dynamodb_tables(env)
# emma_prod_allow_update_event_source_mappings(env)

# # Roles
# emma_prod_lambda_batch_role(env)
# emma_prod_lambda_incoming_metadata_s3_sqs_role(env)
# emma_prod_lambda_maintenance_role(env)
# emma_prod_lambda_s3_dynamodb_role(env)
# emma_prod_lambda_update_dynamodb_role(env)
# emma_prod_lambda_vpc_execution_role(env)
# emma_prod_batch_s3_role(env)

# # Dynamo DB
# emma_bookshare_loader(env)
# hathitrust_retrieval(env)

# # SQS
# incoming_metadata_to_process(env)
# incoming_metadata_to_process_dlq(env)

# # Lambda
# bookshare_scan(env)
# emma_bring_online(env)
# emma_ingest_delete(env)
# emma_ingest_get(env)
# emma_ingest_put(env)
# emma_maintenance_message(env)
# emma_publish_counts(env)
# emma_search_get(env)
# emma_take_offline(env)
# hathitrust_batch_trigger(env)
# hathitrust_get_file(env)
# hathitrust_retry(env)
# hathitrust_scan(env)
# internet_archive_scan(env)

# # S3
# hathitrust_bigfiles(env)
# hathitrust_upload(env)