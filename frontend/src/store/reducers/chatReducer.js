import * as actionTypes from '../ActionTypes';

const initialState = {
  user: null,
  error: null,
  isLoading: false,
  isQuestionLoading: false,
  currentChatThreadId: null,
  isAgentRequestLoading: false,
  waitingForResponse: false,
  messages: []
};


function chatReducer(state = initialState, action) {
    switch (action.type) {
        case actionTypes.CHAT_USER_MESSAGE_REQUEST:
            return { ...state, isLoading: true, error: null };
        case actionTypes.CHAT_USER_MESSAGE_SUCCESS:
            return {
                ...state,
                isLoading: false,
                waitingForResponse: true,
                currentChatThreadId: action.chat_thread_id,
                messages: action.messages,
                // messages: [...state.messages, { type: 'query', query: action.query, id: action.query_id }],
                error: null
            };
        case actionTypes.CHAT_USER_MESSAGE_FAILURE:
            return { ...state, isLoading: false, error: action.payload };
        case actionTypes.CHAT_AGENT_POLL_REQUEST:
            return { ...state, isAgentRequestLoading: true, error: null };
        case actionTypes.CHAT_AGENT_POLL_SUCCESS:
            return {
                ...state,
                messages: action.messages,
                currentChatThreadId: action.chat_thread_id,
                isAgentRequestLoading: false,
                waitingForResponse: false,
                error: null
            }
            // let messages = state.messages
            // if(state.waitingForResponse)
            //     messages = [...messages, { type: 'response', answer: action.answer, queryId : action.query_id, responseMode: action.response_mode || 'text', sources: action.sources }]
            // return { ...state, isAgentRequestLoading: false, waitingForResponse: false, messages: messages, error: null };
        case actionTypes.CHAT_AGENT_POLL_FAILURE:
            return { ...state, isAgentRequestLoading: false, waitingForResponse: false, error: action.payload };

        case actionTypes.LOGOUT_SUCCESS:
            return { ...state, messages: [] };
        default:
        return state;
    }
}

export default chatReducer;
