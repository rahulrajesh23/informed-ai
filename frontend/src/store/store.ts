import { configureStore } from '@reduxjs/toolkit';
import rootReducer from './reducers';
import { RootState } from './reducers/types';

export const store = configureStore({
  reducer: rootReducer,
});

// Infer the `AppDispatch` type from the store itself
export type AppDispatch = typeof store.dispatch;

// Export the RootState type
export type { RootState };

export default store;
