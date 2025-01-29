from pynput import keyboard
import pyaudio
import wave

class listener(keyboard.Listener):
    def __init__(self, recorder):
        super().__init__(on_press=self.on_press, on_release=self.on_release)
        self.recorder = recorder
    
    def on_press(self, key):
        if key is None:  # unknown event
            pass
        elif isinstance(key, keyboard.Key):  # special key event
            if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.recorder.start()
        elif isinstance(key, keyboard.KeyCode):  # alphanumeric key event
            if key.char == 'q':  # press q to quit
                if self.recorder.recording:
                    self.recorder.stop()
                return False  # this is how you stop the listener thread                                                  

    def on_release(self, key):
        if key is None:  # unknown event
            pass
        elif isinstance(key, keyboard.Key):  # special key event
            if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.recorder.stop()
        elif isinstance(key, keyboard.KeyCode):  # alphanumeric key event
            pass

class recorder:
    def __init__(self, 
                 wavfile, 
                 chunksize=8192, 
                 dataformat=pyaudio.paInt16, 
                 channels=2, 
                 rate=44100):
        self.filename = wavfile
        self.chunksize = chunksize
        self.dataformat = dataformat
        self.channels = channels
        self.rate = rate
        self.recording = False
        self.pa = pyaudio.PyAudio()

    def start(self):
        if not self.recording:
            self.wf = wave.open(self.filename, 'wb')
            self.wf.setnchannels(self.channels)
            self.wf.setsampwidth(self.pa.get_sample_size(self.dataformat))
            self.wf.setframerate(self.rate)
            
            def callback(in_data, frame_count, time_info, status):
                # file write should be able to keep up with audio data stream (about 1378 Kbps)
                self.wf.writeframes(in_data) 
                return (in_data, pyaudio.paContinue)
            
            self.stream = self.pa.open(format=self.dataformat,
                                       channels=self.channels,
                                       rate=self.rate,
                                       input=True,
                                       stream_callback=callback)
            self.stream.start_stream()
            self.recording = True
            print('Recording started')

    def stop(self):
        if self.recording:         
            print('Recording finished')

            self.stream.stop_stream()
            self.stream.close()
            self.wf.close()

            self.recording = False

if __name__ == '__main__':
    r = recorder("mic.wav")
    l = listener(r)
    print('Press Alt key to start recording and release to stop. Press "q" to quit.')
    l.start()  # keyboard listener is a thread so we start it here
    l.join()  # wait for the thread to terminate so the program doesn't instantly close