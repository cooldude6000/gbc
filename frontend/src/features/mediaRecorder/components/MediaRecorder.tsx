import React from 'react';
import { useMediaRecorder } from '../hooks/useMediaRecorder';
import { MediaConfig } from '../types';

interface Props {
    config: MediaConfig;
}

export const MediaRecorder: React.FC<Props> = ({ config }) => {
    const { state, startRecording, stopRecording } = useMediaRecorder(config);

    return (
        <div>
            {state.error && (
                <div style={{ color: 'red', marginBottom: '10px' }}>
                    {state.error}
                </div>
            )}

            <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
                <button
                    onClick={startRecording}
                    disabled={state.isRecording || state.isLoading}
                >
                    {state.isLoading ? 'Starting...' : 'Start Recording'}
                </button>
                <button
                    onClick={stopRecording}
                    disabled={!state.isRecording}
                >
                    Stop Recording
                </button>
            </div>
        </div>
    );
};