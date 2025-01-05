import { combineReducers, Reducer } from 'redux';
import userReducer from './userReducer';
import chatReducer from './chatReducer';
import adminReducer from './adminReducer';
import { RootState } from './types';
import { UserAction, ChatAction, AdminAction } from '../actions/types';
import { UserState, ChatState, AdminState } from './types';

const rootReducer = combineReducers({
  user: userReducer as Reducer<UserState, UserAction>,
  chat: chatReducer as Reducer<ChatState, ChatAction>,
  admin: adminReducer as Reducer<AdminState, AdminAction>,
});

export type { RootState };
export default rootReducer;
