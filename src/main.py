# pylint: disable=unused-variable, unused-import
"""Main entrypoint for the Artist Pulse ingestion job.

Cloud Function HTTP entrypoint that runs the Artist Pulse ingestion job.
"""

from datetime import datetime
from zoneinfo import ZoneInfo
import json

from extract.fetch_christmas_artists import ChristmasArtistsExtractor
from load.upload_gcs import upload_to_gcs
from utils.logger import get_logger


logger = get_logger(__name__)


def artist_pulse_job():
    """
    Cloud Run Job entrypoint that runs the Artist Pulse ingestion job.

     Intended to be executed as a Cloud Run Job (non-HTTP). Computes a snapshot
     date in the "America/Sao_Paulo" timezone, runs the extraction for that date
     via ChristmasArtistsExtractor.extract(snapshot_date), and uploads JSON
     snapshots for artists and tracks to Google Cloud Storage using upload_to_gcs.

     Notes:
     - This function is NOT an HTTP handler and does not accept a request object.
     - Returns a (message, int) tuple for local/testing convenience. Cloud Run Jobs
       rely on the container exit code rather than an HTTP response.
     - Exceptions are caught and logged; on error the function returns an error
       tuple and logs the stack trace.

     Side effects:
     - Calls ChristmasArtistsExtractor.extract(snapshot_date).
     - Uploads two JSON files to GCS (artists and tracks).
    """
    snapshot_date = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%Y-%m-%d")

    extractor = ChristmasArtistsExtractor()

    if request:
        logger.debug(
            "Triggered by request method: %s", getattr(request, "method", None)
        )

    try:
        data = extractor.extract(snapshot_date)

        artists = data.get("artists", [])
        tracks = data.get("tracks", [])

        artists_filename = f"bronze/artists/{snapshot_date}/snapshot.json"
        tracks_filename = f"bronze/tracks/{snapshot_date}/snapshot.json"
        # Log small summary so variables are used (avoids unused-variable warnings)
        logger.info(
            "Extracted %d artists and %d tracks",
            len(artists),
            len(tracks),
        )

        upload_to_gcs(
            data=json.dumps(artists, ensure_ascii=False, indent=2),
            destination_blob_name=artists_filename,
        )

        upload_to_gcs(
            data=json.dumps(tracks, ensure_ascii=False, indent=2),
            destination_blob_name=tracks_filename,
        )

        return "Artists/Tracks Pulse ingested!", 200
    except (ValueError, RuntimeError, OSError) as e:
        logger.error("Job error: %s", e, exc_info=True)
        return "Error", 500


if __name__ == "__main__":
    artist_pulse_job()
