from http import HTTPStatus
from http.client import HTTPResponse

from cvat_sdk.api_client import Configuration, ApiClient
from time import sleep
import shutil

configuration = Configuration(
    host='',
    username='',
    password=''
)

# APP will check every 10 second if annotations were ready to download
MAX_RETRIES = 10000
INTERVAL_SECONDS = 10

# Cvat Project ID
PROJECT_ID = '2'


def export_dataset(api_client,
                   project_id: int,
                   max_retries: int = MAX_RETRIES,
                   interval: float = INTERVAL_SECONDS, ) -> HTTPResponse:
    for _ in range(max_retries):
        (_, response) = api_client.projects_api.retrieve_annotations(id=project_id,
                                                                     format='YOLO 1.1',
                                                                     _parse_response=False)
        if response.status == HTTPStatus.CREATED:
            break
        if not response.status == HTTPStatus.ACCEPTED:
            raise Exception(f"response.status not {HTTPStatus.ACCEPTED}")
        sleep(interval)
    if not response.status == HTTPStatus.CREATED:
        raise Exception(f"response.status not {HTTPStatus.CREATED}")

    (_, response) = api_client.projects_api.retrieve_annotations(id=project_id,
                                                                 format='YOLO 1.1',
                                                                 action="download", _parse_response=False)
    if response.status == HTTPStatus.OK:
        save_zip(response)

    return response


def save_zip(response, chunk_size=100):
    with open(f'annotations.zip', 'wb') as out:
        while True:
            data = response.read(chunk_size)
            if not data:
                break
            out.write(data)
    response.release_conn()


with ApiClient(configuration) as api_client:
    try:
        print(f"Export annotations for project {PROJECT_ID}")
        export_dataset(api_client, project_id=int(PROJECT_ID))
        print("Annotations successfully exported")
        shutil.unpack_archive("annotations.zip", "")
        print("Annotations successfully extracted")
    except Exception as e:
        print(f"Error: {e}")
        raise Exception(f"Error: {e}")
