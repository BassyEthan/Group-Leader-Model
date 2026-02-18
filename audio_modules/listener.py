
import threading
import queue
import time
import speech_recognition as sr
from .voice import audio_to_numpy, identify_speaker, preprocess_wav

# ═══════════════════════════════════════════════════════════════════════════
#  AUDIO LISTENER
# ═══════════════════════════════════════════════════════════════════════════
class AudioListener:
    def __init__(self, result_queue, encoder, profiles):
        self.result_queue = result_queue
        self.encoder = encoder
        self.profiles = profiles
        self._stop_event = threading.Event()
        self._thread = None
        self._prev_speaker = None
        self._prev_speaker_time = 0.0

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()

    @property
    def running(self):
        return self._thread is not None and self._thread.is_alive()

    def _listen_loop(self):
        recognizer = sr.Recognizer()
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.8
        
        # Suppress ALSA/PortAudio warnings by redirecting stderr if needed
        # (Not implemented here to keep it simple, but good for Phase 2b)

        try:
            mic = sr.Microphone()
            with mic as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
        except OSError:
            self.result_queue.put("[AUDIO ERROR: No microphone found]")
            return

        while not self._stop_event.is_set():
            try:
                with mic as source:
                    # Listen for up to 10 seconds of speech, timeout after 3s of silence
                    audio = recognizer.listen(source, timeout=3, phrase_time_limit=10)
                
                speaker = None
                confidence = 0.0
                
                # 1. Identify Speaker
                if self.encoder is not None and self.profiles:
                    try:
                        wav_np = audio_to_numpy(audio)
                        processed = preprocess_wav(wav_np, source_sr=16000)
                        embedding = self.encoder.embed_utterance(processed)
                        speaker, confidence = identify_speaker(
                            embedding, self.profiles
                        )
                    except Exception:
                        pass # Silently fail on embedding errors

                # 2. Convert to Text
                try:
                    text = recognizer.recognize_google(audio)
                except sr.UnknownValueError:
                    continue # Speech was unintelligible
                except sr.RequestError as e:
                    self.result_queue.put({
                        "speaker": None, "confidence": 0.0,
                        "text": f"[STT ERROR: {e}]", "interrupted": None,
                    })
                    time.sleep(2)
                    continue

                if not text:
                    continue

                # 3. Detect Interruption (Simple Logic)
                interrupted_person = None
                now = time.time()
                # If speaker changed quickly (within 2.5s), assume interruption
                if (
                    speaker is not None
                    and self._prev_speaker is not None
                    and speaker != self._prev_speaker
                    and (now - self._prev_speaker_time) < 2.5
                ):
                    interrupted_person = self._prev_speaker
                
                self._prev_speaker = speaker
                self._prev_speaker_time = now

                self.result_queue.put({
                    "speaker": speaker,
                    "confidence": confidence,
                    "text": text,
                    "interrupted": interrupted_person,
                })

            except sr.WaitTimeoutError:
                continue # Just loop back if no speech heard
            except Exception as e:
                # Catch-all for other audio errors to keep thread alive
                print(f"Listener Error: {e}")
                continue
