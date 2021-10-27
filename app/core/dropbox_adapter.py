import os
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError
from dropbox.exceptions import AuthError

from app.core.config import Settings

__all__ = ["DropboxSession"]

# Add OAuth2 access token here.
# You can generate one for yourself in the App Console.
# See <https://blogs.dropbox.com/developers/2014/05/generate-an-access-token-for-your-own-account/>

settings = Settings()


class DropboxSession:
    """ a class for using Dropbox"""

    def __init__(self):
        # Check for an access token
        try:
            self.dbx = dropbox.Dropbox(settings.DROPBOX_TOKEN)
        except AuthError:
            print("Dropbox token missing... ")

        # Create an instance of a Dropbox class, which can make requests to the API.
        print("Creating a Dropbox object...")

        # Check that the access token is valid
        try:
            self.dbx.users_get_current_account()
        except:
            print(
                "ERROR: Invalid access token; try re-generating an "
                "access token from the app console on the web."
            )

    def send_image_file(self, file_path):

        try:
            print("Start dropbox upload...")
            filename = os.path.basename(file_path)
            dest_path = os.path.join("/natron_test", filename)
            with open(file_path, "rb") as f:
                self.dbx.files_upload(f.read(), dest_path, mode=WriteMode("overwrite"))
            print("Upload complete.")
        except Exception as err:
            print("Failed to upload %s\n%s" % (file_path, err))