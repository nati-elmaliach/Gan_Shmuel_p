from flask import Flask, Response, request
import os
import sys
from dotenv import load_dotenv, find_dotenv
from time import sleep

app = Flask(__name__)

REPOSITORY_URL = 'https://github.com/ChrisPushkin/Gan_Shmuel_p.git'
TESTING_DIR = 'test/'
PRODUCTION_DIR = 'production/'
PORTS_FILE = 'ports.txt'

def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

@app.route('/payload', methods=['POST'])
def gitWebHook():
	data = request.get_json()
	branch = data['ref'].split('/')[-1]

	os.system('rm -rf {}*'.format(TESTING_DIR))
	os.system('git clone {} --single-branch -b {} {}{}'.format(REPOSITORY_URL, branch, TESTING_DIR, branch))

	# Finding the Dockerfile
	docker_file = find('Dockerfile', '{}{}'.format(TESTING_DIR, branch))
	docker_path = '/'.join(docker_file.split('/')[:-1])

	# Finding the docker-compose file
	compose_file = find('docker-compose.yml', '{}{}'.format(TESTING_DIR, branch))
	compose_path = '/'.join(compose_file.split('/')[:-1])

	# Load .env file as environment variables
	print('ENV FILE:: {}/.env'.format(compose_path))
	load_dotenv('{}/.env'.format(compose_path), override=True)

	# Build Dockerfile to get image artifact
	os.system('docker build -t {} ./{}'.format(os.environ['IMAGE_NAME'], docker_path))

	# Run the test build
	os.system('docker-compose -f {} up -d'.format(compose_file))
	'''
	# TODO:
	# End-2-End testing here....

	# Test complete, remove test containers and update production containers
	# ..to work with new images.
	os.system('docker-compose -f {} kill'.format(compose_file))
	
	# Copy successful test clone to production
	os.system('rm -rf {}{}'.format(PRODUCTION_DIR, compose_path))
	os.system('mkdir {}{}'.format(PRODUCTION_DIR, compose_path.split('/')[-1]))
	os.system('mv -f {}/* {}/.* {}{}/'.format(compose_path, compose_path, PRODUCTION_DIR, compose_path.split('/')[-1]))

	# Run app with production port
	os.environ['PORT'] = os.environ['PROD_PORT']
	os.system('docker-compose -f {}{}/docker-compose.yml up -d'.format(PRODUCTION_DIR, compose_path.split('/')[-1]))
	'''
	return Response(status=200)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8085, threaded=True, debug=True)