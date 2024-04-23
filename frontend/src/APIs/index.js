import { Constants } from "../Constants";

const api_urls = Constants.apis
export function submitQuestionAndDocuments(question, documents) {
    const apiUrl = api_urls.submit;

    const data = {
        question, documents
    };

    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok'); // TODO: Handle gracefully
        }
        return response.json(); 
    })
    .then(data => {
        console.log('Success:', data);
        return data
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

export function getQuestionAndFacts() {
    const apiUrl = api_urls.generateResponse;
    return fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'processing') {
                console.log('Data is still processing, retrying...');
            } else if (data.status === 'done') {
                console.log('Processing complete:', data);
            }
            return data
        })
        .catch(error => console.error('Error polling the API:', error));
}

