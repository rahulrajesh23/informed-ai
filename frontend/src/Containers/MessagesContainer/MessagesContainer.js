import React, { useEffect, useState } from 'react';
import { Loader } from '../../Components/Loader';

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
                        if(message.type == "query") {
                            return (
                                <div key={index} className={`${styles.message} ${styles.user}`}>
                                    <strong>Question:</strong>
                                    <p>{message.query}</p>
                                </div>
                            )
                        }
                        else if (message.type == "response" && message.answer) {

                            return (
                                <div key={index} className={`${styles.message} ${styles.agent}`}>
                                    <strong>Response:</strong>
                                    {(message.responseMode || 'text') === 'voice' ? (
                                        <AudioPlayer queryId={message.queryId} />
                                    ) : (
                                        <>
                                            <p>{message.answer}</p>
                                            {message.sources && Array.isArray(message.sources) && message.sources.length > 0 && (
                                                <p>
                                                    <strong>Source: </strong>
                                                    {message.sources.map((source, sourceIndex) => (
                                                        <React.Fragment key={sourceIndex}>
                                                            {sourceIndex > 0 && ', '}
                                                            <a style={{'cursor': 'pointer'}} href={source.source}>{source.source}</a>
                                                        </React.Fragment>
                                                    ))}
                                                </p>
                                            )}
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
