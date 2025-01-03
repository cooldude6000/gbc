import { useState, useRef } from 'react';
import RecordRTC, { invokeSaveAsDialog } from 'recordrtc';
import { MediaConfig, RecordingState, ExtendedRecordRTC, AudioConstraints } from '../types';
import { getScreenStream, getWebcamStream } from '../utils/mediaStreams';

export const useMediaRecorder = (config: MediaConfig) => {
    const [state, setState] = useState<RecordingState>({
        isRecording: false,
        isLoading: false,
        error: null
    });

    const recorders = useRef<Map<string, ExtendedRecordRTC>>(new Map());

    const startRecording = async () => {
        try {
            setState(prev => ({ ...prev, isLoading: true }));

            if (config.screen.video) {
                const screenStream = await getScreenStream(!!config.screen.audio);
                const screenRecorder = new RecordRTC(screenStream, {
                    type: 'video',
                    mimeType: 'video/mp4',
                    frameRate: 30,
                    videoBitsPerSecond: 4500000,
                    disableLogs: false
                }) as ExtendedRecordRTC;
                screenRecorder.stream = screenStream;
                recorders.current.set('screen', screenRecorder);

                screenStream.getVideoTracks()[0].addEventListener('ended', () => {
                    stopRecording();
                });
            }

            if (config.webcam.video || config.webcam.audio) {
                const audioConstraints: AudioConstraints = {
                    noiseSuppression: true,
                    echoCancellation: true,
                    autoGainControl: true
                };

                const webcamStream = await getWebcamStream({
                    video: config.webcam.video,
                    audio: config.webcam.audio ? audioConstraints : false
                });

                if (config.webcam.video) {
                    const webcamRecorder = new RecordRTC(webcamStream, {
                        type: 'video',
                        mimeType: 'video/mp4',
                        frameRate: 30,
                        videoBitsPerSecond: 4500000,
                        disableLogs: false
                    }) as ExtendedRecordRTC;

                    webcamRecorder.stream = webcamStream;
                    recorders.current.set('webcam', webcamRecorder);
                } else if (config.webcam.audio) {
                    const audioRecorder = new RecordRTC(webcamStream, {
                        type: 'audio',
                        mimeType: 'audio/wav',
                        recorderType: RecordRTC.StereoAudioRecorder,
                        numberOfAudioChannels: 2,
                        sampleRate: 44100,
                        desiredSampRate: 44100,
                        bufferSize: 16384,
                        timeSlice: 1000,
                        disableLogs: false
                    }) as ExtendedRecordRTC;
                    audioRecorder.stream = webcamStream;
                    recorders.current.set('webcam-audio', audioRecorder);
                }
            }

            recorders.current.forEach(recorder => recorder.startRecording());
            setState(prev => ({ ...prev, isRecording: true, isLoading: false }));

        } catch (error) {
            setState(prev => ({
                ...prev,
                error: (error as Error).message,
                isLoading: false
            }));
        }
    };

    const stopRecording = async () => {
        try {
            const promises = Array.from(recorders.current.entries()).map(
                async ([key, recorder]) => {
                    return new Promise<void>((resolve) => {
                        recorder.stopRecording(() => {
                            const blob = recorder.getBlob();
                            let filename = '';

                            switch (key) {
                                case 'screen':
                                    filename = 'screen.mp4';
                                    break;
                                case 'webcam':
                                    filename = 'webcam.mp4';
                                    break;
                                case 'webcam-audio':
                                    filename = 'webcam-audio.wav';
                                    break;
                            }

                            invokeSaveAsDialog(blob, filename);

                            if (recorder.stream?.getTracks) {
                                recorder.stream.getTracks().forEach(track => track.stop());
                            }
                            resolve();
                        });
                    });
                }
            );

            await Promise.all(promises);
            setState(prev => ({ ...prev, isRecording: false, isLoading: false }));
            recorders.current.clear();

        } catch (error) {
            setState(prev => ({
                ...prev,
                error: (error as Error).message,
                isLoading: false
            }));
        }
    };

    return { state, startRecording, stopRecording };
};
