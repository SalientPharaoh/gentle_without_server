import json
import logging
import os
import uuid
import wave
import shutil
import gentle

from gentle.util.paths import get_resource, get_datadir
from gentle.util.cyst import Insist


class Transcriber:
    def __init__(self, data_dir, nthreads=4, ntranscriptionthreads=2):
        self.data_dir = data_dir
        self.nthreads = nthreads
        self.ntranscriptionthreads = ntranscriptionthreads
        self.resources = gentle.Resources()
        self.full_transcriber = gentle.FullTranscriber(self.resources, nthreads=ntranscriptionthreads)
        self._status_dicts = {}

    def get_status(self, uid):
        return self._status_dicts.setdefault(uid, {})

    def out_dir(self, uid):
        return os.path.join(self.data_dir, 'transcriptions', uid)

    def next_id(self):
        uid = None
        while uid is None or os.path.exists(os.path.join(self.data_dir, uid)):
            uid = uuid.uuid4().hex[:8]
        return uid

    def transcribe(self, uid, transcript, audio, async_mode, **kwargs):
        status = self.get_status(uid)
        status['status'] = 'STARTED'
        output = {'transcript': transcript}

        outdir = os.path.join(self.data_dir, 'transcriptions', uid)
        os.makedirs(outdir, exist_ok=True)

        tran_path = os.path.join(outdir, 'transcript.txt')
        with open(tran_path, 'w') as tranfile:
            tranfile.write(transcript)
        audio_path = os.path.join(outdir, 'upload')
        with open(audio_path, 'wb') as wavfile:
            wavfile.write(audio)

        status['status'] = 'ENCODING'

        wavfile_path = os.path.join(outdir, 'a.wav')
        if gentle.resample(os.path.join(outdir, 'upload'), wavfile_path) != 0:
            status['status'] = 'ERROR'
            status['error'] = "Encoding failed. Make sure that you've uploaded a valid media file."
            with open(os.path.join(outdir, 'status.json'), 'w') as jsfile:
                json.dump(status, jsfile, indent=2)
            return

        wav_obj = wave.open(wavfile_path, 'rb')
        status['duration'] = wav_obj.getnframes() / float(wav_obj.getframerate())
        status['status'] = 'TRANSCRIBING'

        def on_progress(p):
            print(p)
            for k, v in p.items():
                status[k] = v

        if len(transcript.strip()) > 0:
            trans = gentle.ForcedAligner(self.resources, transcript, nthreads=self.nthreads, **kwargs)
        elif self.full_transcriber.available:
            trans = self.full_transcriber
        else:
            status['status'] = 'ERROR'
            status['error'] = 'No transcript provided and no language model for full transcription'
            return

        output = trans.transcribe(wavfile_path, progress_cb=on_progress, logging=logging)

        os.unlink(os.path.join(outdir, 'upload'))

        with open(os.path.join(outdir, 'align.json'), 'w') as jsfile:
            jsfile.write(output.to_json(indent=2))
        with open(os.path.join(outdir, 'align.csv'), 'w') as csvfile:
            csvfile.write(output.to_csv())

        status['status'] = 'OK'
        logging.info('done with transcription.')

        return output.to_json(indent=2)

def transcribe_audio(transcript, audio):
    data_dir = './data'
    transcriber = Transcriber(data_dir, nthreads=4, ntranscriptionthreads=2)
    uid = transcriber.next_id()
    async_mode = False  # Not used in this simplified version

    kwargs = {'disfluency': False, 'conservative': False, 'disfluencies': set(['uh', 'um'])}
    result = transcriber.transcribe(uid, transcript, audio, async_mode, **kwargs)
    return result
