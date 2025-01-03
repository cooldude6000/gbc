import RecordRTC from 'recordrtc';

export interface AudioConstraints extends MediaTrackConstraints {
    noiseSuppression?: boolean;
    echoCancellation?: boolean;
    autoGainControl?: boolean;
}

export interface StreamConfig {
    video: boolean;
    audio: boolean | AudioConstraints;
}

export interface MediaConfig {
    webcam: StreamConfig;
    screen: StreamConfig;
}

export interface RecordingState {
    isRecording: boolean;
    isLoading: boolean;
    error: string | null;
}

export interface ExtendedRecordRTC extends RecordRTC {
    stream: MediaStream;
    startRecording: () => void;
    stopRecording: (callback?: () => void) => void;
    getBlob: () => Blob;
}