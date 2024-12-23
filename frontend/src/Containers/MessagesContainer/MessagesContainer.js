import React, { useEffect, useState } from 'react';
import { Loader } from '../../Components/Loader';
import { SupportAgent } from '@mui/icons-material';

import styles from './MessagesContainer.module.css';

const AudioPlayer = ({ queryId }) => {
    const [audioUrl, setAudioUrl] = useState(null);

    useEffect(() => {
        const fetchAudio = async () => {
            try {
                const response = await fetch(`/api/v1/query/tts/${queryId}`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const audioData = await response.blob();
                // Create blob with explicit MIME type
                const audioBlob = new Blob([audioData], { type: 'audio/mpeg' });
                const url = URL.createObjectURL(audioBlob);
                setAudioUrl(url);
            } catch (error) {
                console.error('Error fetching audio:', error);
            }
        };

        fetchAudio();

        return () => {
            if (audioUrl) {
                URL.revokeObjectURL(audioUrl);
            }
        };
    }, [queryId]);

    return audioUrl ? (
        <audio
            controls
            className={styles.audioPlayer}
            src={audioUrl}
            type="audio/mpeg"
        >
            Your browser does not support the audio element.
        </audio>
    ) : (
        <div>Loading audio...</div>
    );
};

export function MessagesContainer(props) {
    const {
        messages = [],
        showLoader = false,
    } = props
    return (
        <div className={styles.messagesContainer}>
                {messages.map((message, index) => {
                    if(message) {
                        if(message.source === "webapp") {
                            return (
                                <div key={index} className={`${styles.message} ${styles.user}`}>
                                    <p>{message.content}</p>
                                </div>
                            )
                        }
                        else if (message.source === "assistant" && message.content) {

                            return (
                                <div key={index} className={`${styles.message} ${styles.agent}`}>
                                    <div className={styles.messageHeader}>
                                        <div className={styles.agentIcon}>
                                            <SupportAgent />
                                        </div>
                                        <span className={styles.agentTitle}>Assistant</span>
                                    </div>
                                    {(message.response_type || 'text') === 'voice' ? (
                                        <AudioPlayer queryId={message.queryId} />
                                    ) : (
                                        <>
                                            <p>{message.content}</p>
                                        </>
                                    )}
                                </div>
                            )
                        }
                    }
                })}

                {showLoader && <Loader /> }

            </div>
    );
}

export default MessagesContainer;
