import os
from dotenv import load_dotenv

from .mtp import get_music_folder_id, get_files_in_folder, add_files_to_folder, delete_files
from .subsonic import SubsonicClient

# Setup the environment
load_dotenv()
required_env_vars = [
  'SUBSONIC_URL',
  'SUBSONIC_USER',
  'SUBSONIC_PASSWORD',
  'SUBSONIC_PLAYLIST',
]
for env_var in required_env_vars:
  if not os.getenv(env_var):
    raise Exception(f"Missing ENV var: {env_var}")
subsonic_url = os.getenv('SUBSONIC_URL')
subsonic_user = os.getenv('SUBSONIC_USER')
subsonic_password = os.getenv('SUBSONIC_PASSWORD')
subsonic_port = int(os.getenv('SUBSONIC_PORT', 443))
subsonic_playlist = os.getenv('SUBSONIC_PLAYLIST')

# Build a client
client = SubsonicClient(subsonic_url, subsonic_user, subsonic_password, subsonic_port)

# Get track IDs and filenames from subsonic
track_ids = client.find_track_ids_for_playlist(subsonic_playlist)
playlist_filenames = set([f'{track_id}.mp3' for track_id in track_ids])

# Get the track and folder info off of the device
music_folder_id = get_music_folder_id()
music_files = get_files_in_folder(music_folder_id)
device_filenames = set([file.filename for file in music_files])

# Determine which files need to be deleted from the device
filenames_to_delete = device_filenames - playlist_filenames
files_to_delete = [file for file in music_files if file.filename in filenames_to_delete]
print(f"Found {len(files_to_delete)} files to remove from the device")

# Determine which files need to be added
filenames_to_add = playlist_filenames - device_filenames
track_ids_to_add = [track_id for track_id in track_ids if f'{track_id}.mp3' in filenames_to_add]
track_ids_to_add = list(set(track_ids_to_add))
print(f"Found {len(track_ids_to_add)} files to add to the device")

# Delete the files from the device in batches
deletion_batch_counter = 0
batched_files_to_delete = [files_to_delete[i: i + 30] for i in range(0, len(files_to_delete), 30)]
for batch in batched_files_to_delete:
  deletion_batch_counter+=1
  print(f"Deleting {len(batch)} files in batch {deletion_batch_counter}/{len(batched_files_to_delete)}")
  file_ids = [file.file_id for file in batch]
  delete_files(file_ids)

# Download and add files to the device in batches
addition_batch_counter = 0
batched_track_ids_to_add = [track_ids_to_add[i : i + 30] for i in range(0, len(track_ids_to_add), 30)]
for batch in batched_track_ids_to_add:
  addition_batch_counter+=1
  print(f"Downloading and transferring {len(batch)} files in batch {addition_batch_counter}/{len(batched_track_ids_to_add)}")

  # Download the files from subsonic
  file_list = []
  for track_id in batch:
    filename = f'./tmp/{track_id}.mp3'
    client.download_mp3(track_id, filename)
    file_list.append(filename)

  # Add the files to the device
  add_files_to_folder(music_folder_id, file_list)

  # Cleanup the downloaded files
  for filename in file_list:
    os.remove(filename)

# Print what is currently on the device
music_files = get_files_in_folder(music_folder_id)
print(f"{len(music_files)} files currently on device:")
total_bytes = 0
for file in music_files:
  total_bytes += file.file_size
  print(f"- {file.filename} ({file.file_size} bytes)")
print(f"Total: {total_bytes} bytes")
