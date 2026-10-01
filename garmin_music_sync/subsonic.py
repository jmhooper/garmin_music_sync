import libsonic

class SubsonicError(Exception):
  pass

class SubsonicClient:
  def __init__(self, url, username, password, port):
    self.connection = libsonic.Connection(url , username , password, port=port)

  def find_track_ids_for_playlist(self, playlist_name):
    playlist_id = self.get_playlist_id_for_playlist_name(playlist_name)
    playlist_response = self.connection.getPlaylist(playlist_id)['playlist']['entry']
    return [entry['id'] for entry in playlist_response if entry['mediaType'] == 'song']

  def get_playlist_id_for_playlist_name(self, playlist_name):
    playlists_response = self.connection.getPlaylists()['playlists']['playlist']
    for playlist in playlists_response:
      if playlist['name'] == playlist_name:
        return playlist['id']
    raise SubsonicError(f'No playlist found with name {playlist_name}')

  def download_mp3(self, track_id, location):
    print(f'Downloading {track_id} to {location}')
    response = self.connection.stream(track_id, tformat='mp3', maxBitRate=320)
    with open(location, 'wb') as song_file:
      song_file.write(response.read())
