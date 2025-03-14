import React, { useEffect, useState } from 'react';
import { SupportAgent } from '@mui/icons-material';
import { Loader } from '../../Components/Loader';
import apiClient from '../../store/apiClient';
import { Message } from '../../types';
import styles from './MessagesContainer.module.css';

interface AudioPlayerProps {
    messageId: string;
}

interface MessagesContainerProps {
    messages: Message[];
    showLoader?: boolean;
}

const AudioPlayer: React.FC<AudioPlayerProps> = ({ messageId }) => {
    const [audioUrl, setAudioUrl] = useState<string | null>(null);

    useEffect(() => {
        const fetchAudio = async () => {
            try {
                const response = await apiClient.blob(`/api/v1/chat/tts/${messageId}`);
                const url = URL.createObjectURL(response.data);
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
    }, [messageId]);

    return audioUrl ? (
        <audio controls className={styles.audioPlayer} src={audioUrl}>
            Your browser does not support the audio element.
        </audio>
    ) : (
        <div>Loading audio...</div>
    );
};

export const MessagesContainer: React.FC<MessagesContainerProps> = ({
    messages = [],
    showLoader = false,
}) => {
    return (
        <div className={styles.messagesContainer}>
            {messages.map((message, index) => {
                if (message) {
                    if (message.source === "webapp") {
                        return (
                            <div key={index} className={`${styles.message} ${styles.user}`}>
                                <p>{message.content}</p>
                            </div>
                        );
                    } else if (message.source === "assistant" && message.content) {
                        return (
                            <div key={index} className={`${styles.message} ${styles.agent}`}>
                                <div className={styles.messageHeader}>
                                    <div className={styles.agentIcon}>
                                        <SupportAgent />
                                    </div>
                                    <span className={styles.agentTitle}>Assistant</span>
                                </div>
                                {(message.responseType || 'text') === 'audio' ? (
                                    <AudioPlayer messageId={message.messageId!} />
                                ) : (
                                    <p>{message.content}</p>
                                )}
                            </div>
                        );
                    }
                }
                return null;
            })}

            {showLoader && <Loader />}
        </div>
    );
};

export default MessagesContainer;
