from django.core.management.base import BaseCommand
from pathlib import Path
from django.conf import settings
import logging
from auctions.models import UserProfile, Auction

# Counts the error logs
class CallCounted(logging.Handler):
    def __init__(self, level = 0):
        super().__init__(level)
        self.error_count = 0

    def emit(self, record):
        if record.levelno == logging.ERROR:
            self.error_count += 1

logger = logging.getLogger(__name__)

# handler to show info level logs
if not logger.handlers:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

# handler to count errors
callcounted = CallCounted()
logger.addHandler(callcounted)

def safe_iterdir(path:Path):
    '''Functions returns a set of iterable files Paths if the directory exists'''
    try:
        return list(f for f in path.iterdir() if f.is_file())
    except FileNotFoundError:
        logger.warning(f"Directory not found: {path}")
        return list()

class Command(BaseCommand):
    help = "This command helps you with dumped image files cleanup"

    def add_arguments(self, parser):
        parser.add_argument("-y", "--yes", action="store_true", help="Skips confirmation!")

    def handle(self, *args, **options):
        # Handling log
        if options["verbosity"] > 1:
            logger.setLevel(logging.INFO)

        # All the associated avatar image files
        userprofile_images = set(
            Path(userprofile.avatar.path)
            for userprofile in UserProfile.objects.all()
            if userprofile.avatar
            and userprofile.avatar != UserProfile.avatar.field.default
        )
        # All the associated auction picture image files
        auction_images = set(
            Path(auction.picture.path)
            for auction in Auction.objects.all()
            if auction.picture and auction.picture != Auction.picture.field.default
        )

        # Images direcotories paths
        auction_images_dir_path = Path(settings.MEDIA_ROOT).joinpath("auction_images")
        profile_images_dir_path = Path(settings.MEDIA_ROOT).joinpath("profile_images")

        # All the auction_images directory image files
        all_images = set(
            safe_iterdir(auction_images_dir_path)
        )
        # All the userprofile avatars image files
        all_images.update(
            safe_iterdir(profile_images_dir_path)
        )

        # The Aboundant files
        differences = all_images.difference(userprofile_images, auction_images)
        if not differences:
            self.stdout.write("Already cleanedUp nothing todo!")
            return

        if not options["yes"]:
            # Shows images that are going to get removed
            self.stdout.write("Following image files are going to get removed!")
            self.stdout.write('\n'.join(f" - {image.name}" for image in differences))
            # Permission to remove images
            try:
                permission = input("This action is irreversible input; y or yes to continue: ")
            except KeyboardInterrupt:
                logger.warning("Process interrupted by user!")
                return
            if permission.lower().strip() not in ["y", "yes"]:
                logger.info("Process aborted by user!")
                return
                
            
        # Removing Abundant image files
        removed_images_count = 0
        for image in differences:
            try:
                image.unlink()
                removed_images_count += 1
                logger.info(f"Removed file: {image.name}")
            except FileNotFoundError:
                logger.error(f"File not found: {image.name}")
            except PermissionError:
                logger.error(f"Permission denied: {image.name}")
            except OSError as e:
                logger.error(f"OS Error: {e}")

        # info for user
        if removed_images_count > 0:
            self.stdout.write(f"Cleaned Up {removed_images_count} abundant images")
        if callcounted.error_count > 0:
            self.stdout.write(f"{callcounted.error_count} errors occurred!")