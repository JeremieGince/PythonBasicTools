import os
from typing import Optional
import tqdm
import requests


class GoogleDriveDownloader:
	"""
	Object used to download a file from Google Drive.
	
	:Exemple:
		>>> gdd = GoogleDriveDownloader(file_id='[file id]', dest_path='data.zip')
		>>> gdd.download()
	"""
	DOWNLOAD_URL = "https://docs.google.com/uc?export=download"
	
	@staticmethod
	def get_confirm_token(response):
		for key, value in response.cookies.items():
			if key.startswith('download_warning'):
				return value
		
		return None
	
	def __init__(
			self,
			file_id: str,
			dest_path: str,
			*,
			chunk_size: Optional[int] = 32768,
			skip_existing: bool = True,
			verbose: bool = True
	):
		"""
		Create a new GoogleDriveDownloader object.
		
		:param file_id: The ID of the file to download. This is the part of the URL after the "/d/" and before the "/view"
			in the URL of the file in Google Drive.
		:param dest_path: The path to save the downloaded file to.
		:param chunk_size: The chunk size to use when downloading the file.
		:param skip_existing: If True, the file will not be downloaded if it already exists at the destination path.
		:param verbose: If True, the download progress will be printed to the console.
		"""
		self.file_id = file_id
		self.dest_path = dest_path
		self.chunk_size = chunk_size
		self.skip_existing = skip_existing
		self.verbose = verbose
	
	def download(self):
		"""
		Download the file.
		
		:return: None
		"""
		session = requests.Session()
		
		response = session.get(self.DOWNLOAD_URL, params={'id': self.file_id}, stream=True)
		token = self.get_confirm_token(response)
		
		if token:
			params = {'id': self.file_id, 'confirm': token}
			response = session.get(self.DOWNLOAD_URL, params=params, stream=True)
		
		self.save_response_content(response)
	
	def save_response_content(self, response):
		if self.skip_existing and os.path.exists(self.dest_path):
			if self.verbose:
				print(f"Skipping '{self.dest_path}' because it already exists.")
			return
		os.makedirs(os.path.dirname(self.dest_path), exist_ok=True)
		with open(self.dest_path, "xb") as f:
			for chunk in tqdm.tqdm(response.iter_content(self.chunk_size), unit='chunk', disable=not self.verbose):
				if chunk:  # filter out keep-alive new chunks
					f.write(chunk)


