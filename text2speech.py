#!/usr/bin/env python
import boto3
import sys
import re
import hashlib
import os.path
import shutil

sentence_filename = sys.argv[1]
engine_type = sys.argv[2]  # needs to be: standard | neural
language = sys.argv[3]

print("Engine:" + engine_type)
print("Processing sentence filename: " + sentence_filename + ".txt")

separator = "="
aws_properties = {}

with open('aws.properties') as property_file:

    for line in property_file:
        if separator in line:
            name, value = line.split(separator, 1)
            aws_properties[name.strip()] = value.strip()


sha256_hash = hashlib.sha256()

with open(sentence_filename + ".txt", "r") as sentence_file:
    sentence = sentence_file.readlines()[0]

hex_digest = hashlib.sha256(sentence.encode('utf-8')).hexdigest()
cache_filename = 'cache/' + hex_digest + ".mp3"

if not os.path.exists(cache_filename):
    polly_client = boto3.Session(aws_access_key_id=aws_properties['aws_access_key_id'],
                                 aws_secret_access_key=aws_properties['aws_secret_access_key'],
                                 region_name='us-east-1').client('polly')

    if(language == "ENGLISH"):
        # short individual words are easier to understand spoken more slowly
        if re.match(r"^\s*([A-Za-z]{1,4})\s*$", sentence):
            print("Pronouncing slowly: " + sentence)
            ssml = "<speak><prosody rate=\"x-slow\">" + sentence + "</prosody></speak>"
            response = polly_client.synthesize_speech(Engine=engine_type, VoiceId='Matthew', OutputFormat='mp3', TextType="ssml", Text=ssml)
        else:
            print("Pronouncing normal speed: " + sentence)
            response = polly_client.synthesize_speech(Engine=engine_type, VoiceId='Matthew', OutputFormat='mp3', Text=sentence)
            print("sentence" + sentence)
    else:
        voice_id = "Matthew"
        if(language == "SWEDISH"):
            voice_id = "Astrid"

        print("Using Voice: " + voice_id)
        response = polly_client.synthesize_speech(Engine=engine_type, VoiceId=voice_id, OutputFormat='mp3', Text=sentence)
        print("sentence" + sentence)

    file = open(cache_filename, 'wb')
    file.write(response['AudioStream'].read())
    file.close()

shutil.copy2(cache_filename, sentence_filename + '-voice.mp3')
