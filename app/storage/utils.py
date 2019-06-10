import base64
import os

from flask import current_app

from google.auth import compute_engine
from google.cloud import storage


class Storage(object):

    def __init__(self, bucket_name):
        if self.no_google_config():
            current_app.logger.info('Google credentials not available')
            return

        if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            credentials = compute_engine.Credentials()
            self.storage_client = storage.Client(credentials=credentials, project=current_app.config['PROJECT'])
        else:
            self.storage_client = storage.Client()

        if bucket_name not in [b.name for b in self.storage_client.list_buckets()]:
            self.bucket = self.storage_client.create_bucket(bucket_name)
            current_app.logger.info('Bucket {} created'.format(self.bucket.name))
        else:
            self.bucket = self.storage_client.get_bucket(bucket_name)

    def no_google_config(self):
        return (
            not current_app.config.get('GOOGLE_APPLICATION_CREDENTIALS') and
            current_app.config['ENVIRONMENT'] == 'development')

    def upload_blob(self, source_file_name, destination_blob_name, set_public=True):
        if self.no_google_config():
            current_app.logger.info('No Google config, upload_blob: source: %s, destination: %s, public %s',
                                    source_file_name, destination_blob_name, set_public)
            return

        blob = self.bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)

        if set_public:
            blob.make_public()

        current_app.logger.info('File {} uploaded to {}'.format(
            source_file_name,
            destination_blob_name))

    def upload_blob_from_base64string(
        self, image_filename, destination_blob_name, base64data, content_type='image/png'
    ):
        if self.no_google_config():
            current_app.logger.info(
                'No Google config, upload_blob_from_base64string: fielname: '
                '%s, destination: %s, base64data: %s, content_type %s',
                image_filename, destination_blob_name, base64data, content_type)
            return

        blob = self.bucket.blob(destination_blob_name)

        binary = base64.b64decode(base64data)

        blob.upload_from_string(binary, content_type=content_type)
        blob.make_public()

        binary_len = len(binary)
        current_app.logger.info('Uploaded {} file {} uploaded to {}'.format(
            sizeof_fmt(binary_len),
            image_filename,
            destination_blob_name))

    def blob_exists(self, prefix, delimiter=None):
        if self.no_google_config():
            current_app.logger.info(
                'No Google config, blob_exists: prefix: %s, delimiter: %s', prefix, delimiter)
            return

        blobs = self.bucket.list_blobs(prefix=prefix, delimiter=delimiter)
        return any(True for _ in blobs)


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Gi', suffix)
