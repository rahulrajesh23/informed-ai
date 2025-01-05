import { User, WeatherAlert, ChatMessage } from '../actions/types';

export interface AdminState {
  weatherAlerts: WeatherAlert[];
  isLoading: boolean;
  error: string | null;
}

export interface ChatState {
  user: User | null;
  error: string | null;
  isLoading: boolean;
  isQuestionLoading: boolean;
  currentChatThreadId: string | null;
  waitingForResponse: boolean;
  messages: ChatMessage[];
}

export interface NotificationItem {
  notification_id: string;
  title: string;
  content: string;
  status: 'READY' | 'DELIVERED' | 'VIEWED';
  created_at: string;
  chat_thread_id?: string;
}

export interface UserState {
  user: User | null;
  user_details: any;
  user_medical_details: any;
  error: null | string;
  isLoading: boolean;
  isNotificationsLoading: boolean;
  loggedIn: boolean;
  notifications: NotificationItem[];
  user_settings: any;
}

export interface RootState {
  user: UserState;
  chat: ChatState;
  admin: AdminState;
}
