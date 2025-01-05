import { Action } from 'redux';

// Admin Action Types
export interface WeatherAlert {
  id: string;
  zipCode: string;
  message: string;
  createdBy: string;
  createdAt: string;
  expiresAt: string;
  cancelledAt: string | null;
  isActive: boolean;
}

export interface AdminAction extends Action {
  payload?: WeatherAlert | WeatherAlert[] | string | Error;
}

// Chat Action Types
export interface ChatMessage {
  type?: string;
  query?: string;
  id?: string;
  content?: string;
}

export interface ChatAction extends Action {
  payload?: any;
  chatThreadId?: string;
  resetMessages?: boolean;
  messages?: ChatMessage[];
  chat_thread_id?: string;
  query?: string;
  query_id?: string;
}

// User Action Types
export interface User {
  id: string;
  email: string;
  details?: {
    first_name: string;
    last_name: string;
  };
  settings?: Record<string, any>;
}

export interface UserAction extends Action {
  payload?: User | string | Error | any;
}
