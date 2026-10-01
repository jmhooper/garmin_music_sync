import sys
import subprocess
import re

class MTPError(Exception):
  pass

class MTPFile:
  def __init__(self, folder_id, file_id, filename, file_size):
    self.folder_id = folder_id
    self.file_id = file_id
    self.filename = filename
    self.file_size = file_size

  def __str__(self):
    return f"MTPFile(folder_id={self.folder_id}, file_id={self.file_id}, filename={self.filename}, file_size={self.file_size})"


def get_music_folder_id():
  mtp_folders_result = subprocess.run(['mtp-folders'], capture_output=True, text=True)
  if mtp_folders_result.returncode != 0:
    print(mtp_folders_result.stderr, file=sys.stderr)
    raise MTPError("Failed to get folders from MTP device")
  return parse_music_folder_id_from_output(mtp_folders_result.stdout)

def parse_music_folder_id_from_output(output):
  match = re.search(r"(\d+)\s+Music", output)
  if not match:
    raise MTPError("Music folder is missing!")
  return match.group(1)

def get_files_in_folder(folder_id):
  return [file for file in get_files() if file.folder_id == folder_id]

def get_files():
  mtp_files_result = subprocess.run(['mtp-files'], capture_output=True, text=True)
  if mtp_files_result.returncode != 0:
    print(mtp_files_result.stderr, file=sys.stderr)
    raise MTPError("Failed to list files on MTP device")
  file_blurbs = re.findall(r"File ID: \d+(?:\n\s+.*)+", mtp_files_result.stdout)
  return [parse_file_from_file_blurb(file_blurb) for file_blurb in file_blurbs]

def parse_file_from_file_blurb(file_blurb):
  folder_id_match = re.search(r"Parent ID: (\d+)", file_blurb)
  file_id_match = re.search(r"File ID: (\d+)", file_blurb)
  filename_match = re.search(r"Filename: (.+)", file_blurb)
  file_size_match = re.search(r"File size (\d+)", file_blurb)
  if (not folder_id_match) or (not file_id_match) or (not filename_match) or (not file_size_match):
    raise MTPError(f"Failed to parse file info from file blurb\n\n{file_blurb}")
  mtp_file = MTPFile(
    folder_id_match.group(1),
    file_id_match.group(1),
    filename_match.group(1),
    int(file_size_match.group(1)),
  )
  return mtp_file

def delete_files(file_ids):
  delete_args = ['mtp-connect'] + [argument_list for file_id in file_ids for argument_list in ("--delete", file_id)]
  print(f"Deleting {len(file_ids)} files...")
  delete_result = subprocess.run(delete_args)
  if not delete_result.returncode == 0:
    raise MTPError(f"Failed to delete files with IDs: {file_ids}")

def add_files_to_folder(folder_id, file_list,):
  send_file_args = ['mtp-connect'] + [argument_list for file in file_list for argument_list in ('--sendfile', file, folder_id)]
  print(f"Adding {len(file_list)} files...")
  add_file_result = subprocess.run(send_file_args)
  if not add_file_result.returncode == 0:
    raise MTPError(f"Failed to add files: {file_list}")
