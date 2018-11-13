from app.storage.utils import Storage


class MockBlob:
    def upload_from_filename(self, filename):
        self.source_filename = filename

    def make_public(self):
        self.public = True


class MockBucket:
    def __init__(self, bucket_name):
        self.name = bucket_name
        self.bucket_created = False

    def blob(self, filename=None):
        self.destination_filename = filename
        self.blob = MockBlob()
        return self.blob

    def upload_blob(self, filename):
        self.upload_block = True

    def list_blobs(self, prefix, delimiter):
        self.prefix = prefix
        self.delimiter = delimiter
        return ['prefix']

    def create_bucket(self, bucket_name):
        self.bucket_created = True


class MockEmptyStorageClient:
    def __init__(self, credentials=None, project=None):
        self.credentials = credentials
        self.project = project
        self.buckets = []

    def list_buckets(self):
        return self.buckets

    def create_bucket(self, bucket_name):
        self.buckets.append(bucket_name)

        return MockBucket(bucket_name)


class MockStorageClient:
    def list_buckets(self):
        return ['test-store']

    def get_bucket(self, bucket_name):
        return MockBucket(bucket_name)


class WhenUsingStorage:

    def it_uses_gce_creds_for_storage_client_without_google_creds_envs(self, app, mocker):
        mocker.patch.dict('os.environ', {
            'GOOGLE_APPLICATION_CREDENTIALS': '',
            'PROJECT': 'test-project'
        })

        mock_google_creds = mocker.patch("google.auth.compute_engine.Credentials", return_value='google-credentials')
        mocker.patch("google.cloud.storage.Client", MockEmptyStorageClient)

        store = Storage('test-store')

        assert mock_google_creds.called
        assert store.storage_client.credentials == 'google-credentials'
        assert store.storage_client.project == 'test-project'
        assert store.storage_client.list_buckets() == ['test-store']

    def it_uses_api_key_for_storage_client_with_google_creds_envs(self, app, mocker):
        mocker.patch.dict('os.environ', {
            'GOOGLE_APPLICATION_CREDENTIALS': 'path/to/creds'
        })

        mock_google_creds = mocker.patch("google.auth.compute_engine.Credentials")
        mocker.patch("google.cloud.storage.Client", MockEmptyStorageClient)

        store = Storage('test-store')

        assert not mock_google_creds.called
        assert store.storage_client.list_buckets() == ['test-store']

    def it_doesnt_create_the_bucket_if_it_exists_(self, app, mocker):
        mocker.patch.dict('os.environ', {
            'GOOGLE_APPLICATION_CREDENTIALS': 'path/to/creds'
        })

        mocker.patch("google.cloud.storage.Client", MockStorageClient)
        mock_google_creds = mocker.patch("google.auth.compute_engine.Credentials")

        store = Storage('test-store')

        assert not mock_google_creds.called
        assert not store.bucket.bucket_created
        assert store.bucket.name == 'test-store'

    def it_uploads_a_file(self, app, mocker):
        mocker.patch.dict('os.environ', {
            'GOOGLE_APPLICATION_CREDENTIALS': 'path/to/creds'
        })

        mocker.patch("google.cloud.storage.Client", MockStorageClient)
        mocker.patch("google.auth.compute_engine.Credentials")

        store = Storage('test-store')
        store.upload_blob('source', 'destination')

        assert store.bucket.destination_filename == 'destination'
        assert store.bucket.blob.source_filename == 'source'
        assert store.bucket.blob.public

    def it_checks_blob_exists(self, app, mocker):
        mocker.patch.dict('os.environ', {
            'GOOGLE_APPLICATION_CREDENTIALS': 'path/to/creds'
        })

        mocker.patch("google.cloud.storage.Client", MockStorageClient)
        mocker.patch("google.auth.compute_engine.Credentials")

        store = Storage('test-store')
        res = store.blob_exists('prefix', 'delimiter')

        assert store.bucket.prefix == 'prefix'
        assert store.bucket.delimiter == 'delimiter'
        assert res
