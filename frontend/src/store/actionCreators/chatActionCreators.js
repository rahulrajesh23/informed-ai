import { actions } from '../actions'
import apiClient from '../apiClient';
import { Constants } from "../../Config/Constants";


const api_urls = Constants.apis
const chatActions = actions.chat

export const submitQuestion = (message, responseType="text") => dispatch => {
    dispatch(chatActions.chatUserMessageRequest());
    if(message) {
        apiClient.post(api_urls.submit, { message, requested_response_type: responseType })
            .then(response => {
                const data = response.data;
                if (data.error) {
                    dispatch(chatActions.chatUserMessageFailure(data.error));
                } else {
                    const queryId = data && data.id || ''
                    dispatch(chatActions.chatUserMessageSuccess({ message, queryId }));
                }
            })
            .catch(error => {
                dispatch(chatActions.chatUserMessageFailure(error.message));
            });
    }
}

export const getAssistantResponse = () => dispatch => {
    dispatch(chatActions.chatAgentPollRequest());
    apiClient.get(api_urls.generateResponse)
        .then(response => {
            const data = response.data
            if (data.error) {
                dispatch(chatActions.chatAgentPollFailure(data.error));
            } else {
                if (data.state != 'completed') {
                    console.info('Data is still processing, retrying...');
                } else {
                    console.info('Processing complete');
                    dispatch(chatActions.chatAgentPollSuccess(data));
                }

            }
        })
        .catch(error => {
            console.log("chat error")
            dispatch(chatActions.chatAgentPollFailure(error.message))
        });
}
