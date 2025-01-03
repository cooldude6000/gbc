import { AudioConstraints } from '../types';

export const getScreenStream = async (captureAudio: boolean) => {
    return await navigator.mediaDevices.getDisplayMedia({
        video: true,
        audio: captureAudio
    });
};

export const getWebcamStream = async (config: {
    video: boolean;
    audio: boolean | AudioConstraints
}) => {
    return await navigator.mediaDevices.getUserMedia({
        video: config.video,
        audio: config.audio
    });
};