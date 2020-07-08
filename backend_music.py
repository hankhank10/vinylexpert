# audio imports
import pyaudio
import wave

# API imports
import requests
import json
import sys

# specific imports
import backend_key

# static settings
path_of_recording_file = sys.path[0] + "/captured.wav"
path_of_downloaded_art = sys.path[0] + "/artwork.jpeg"
api_url = "https://api.audd.io/"
seconds_to_record = 10

def listen():
    form_1 = pyaudio.paInt16 # 16-bit resolution
    chans = 1 # 1 channel
    samp_rate = 44100 # 44.1kHz sampling rate
    chunk = 4096 # 2^12 samples for buffer
    dev_index = 0 # device index found by p.get_device_info_by_index(ii)
    path_of_recording_file

    audio = pyaudio.PyAudio() # create pyaudio instantiation

    # create pyaudio stream
    stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                        input_device_index = dev_index,input = True, \
                        frames_per_buffer=chunk)
    print("Recording " + str(seconds_to_record) + "seconds of audio....")
    frames = []

    # loop through stream and append audio chunks to frame array
    for ii in range(0,int((samp_rate/chunk)*seconds_to_record)):
        data = stream.read(chunk)
        print ("... chunk " + str (ii))
        frames.append(data)

    print("Recording complete")

    # stop the stream, close it, and terminate the pyaudio instantiation
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # save the audio frames as .wav file
    wavefile = wave.open(path_of_recording_file,'wb')
    wavefile.setnchannels(chans)
    wavefile.setsampwidth(audio.get_sample_size(form_1))
    wavefile.setframerate(samp_rate)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()
    print ("File saved down")

def identify():
    api_key = backend_key.get_key()

    if api_key == "":
        return {"status": "no api token set"}
        
    data = {
        'return': 'apple_music',
        'api_token': api_key
    }

    print ("Sending file to audd.io API")
    result = requests.post(api_url, data=data, files={'file': open(path_of_recording_file, 'rb')})

    data = result.json()
    
    with open('output.json', 'w') as f:
        json.dump(data, f)

    status = (data['status'])
    if status != "success":
        return_dict = {"status": "Lookup failed"}
        return return_dict

    if (data['result']) == None:
        return_dict = {"status": "Lookup failed"}
        return return_dict

    return_dict = {"status": "success"}
    return return_dict

def parse():

    with open('output.json') as json_file:
        data = json.load(json_file)

    if (data['result']) == None:
        return_dict = {"status": "Lookup failed"}
        return return_dict
    
    #Tidy the artwork URL
    art_raw = data['result']['apple_music']['artwork']['url']
    
    if art_raw.endswith('{w}x{h}bb.jpeg'):
        art_tidy = art_raw[:-14]
        art_tidy = art_tidy+"1500x1500bb.jpeg"

    return_dict = {
        "status": data['status'],
        "artist": data['result']['artist'],
        "album": data['result']['album'],
        "title": data['result']['title'],
        "song_link": data['result']['song_link'],
        "art_raw": data['result']['apple_music']['artwork']['url'],
        "art_tidy": art_tidy
        }

    return return_dict

def download_art():

    output = parse()
        
    if output['status'] == "Lookup failed":
        return {"status": "Lookup failed"}

    url = output['art_tidy']

    response = requests.get(url)
    if response.status_code == 200:
        with open(path_of_downloaded_art, 'wb') as f:
            f.write(response.content)
    
    return {"status": "success", "artwork_path": path_of_downloaded_art}
