import { WeatherAlert } from '../store/actions/types';

export interface User {
  email: string;
  // Add other user properties
}

export interface Message {
  source: 'webapp' | 'assistant';
  content: string;
  message_id?: string;
  response_type?: 'text' | 'audio' | 'text_message';
}

export interface NotificationItem {
  notification_id: string;
  title: string;
  content: string;
  status: 'READY' | 'DELIVERED' | 'VIEWED';
  created_at: string;
  chat_thread_id?: string;
}

export interface RootState {
  admin: {
    weatherAlerts: WeatherAlert[];
  };
  user: {
    user: User | null;
    loggedIn: boolean;
    isLoading: boolean;
    user_details: any; // Define specific type if available
    user_medical_details: any; // Define specific type if available
    user_settings: any; // Define specific type if available
    notifications: NotificationItem[];
    error: string | null;
  };
  chat: {
    messages: Message[];
    waitingForResponse: boolean;
    currentChatThreadId: string | null;
  };
}
