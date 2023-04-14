The make-schema.py script will create versions of the schema to be uploaded to AWS or SwaggerHub.
- The singlefile version can be uploaded to AWS
- The SwaggerHub version can be uploaded to SwaggerHub.  It uses the "domain" of shared objects.

You can either run the script using pipenv, or install the following libraries to your local Python 3 installation:
- pyyaml
- dollar-ref

If you install those libraries, you can run the script in this directory as
./make-schema.py