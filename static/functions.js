/*
MIT License

Copyright (c) 2024 av1d - https://github.com/av1d/

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

/*
   place cursor in the input_text area on page load
*/
document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('input_text').focus();
});

/*
   auto-expand the text input area
*/
function autoExpand(textarea) {
    // Reset textarea height to default in case it shrinks
    textarea.style.height = 'auto';
    // Calculate the height of the content and limit it to 20vw
    const maxHeight = 15 * (window.innerWidth / 100); // Convert 15vw to pixels
    const newHeight = Math.min(textarea.scrollHeight, maxHeight);
    textarea.style.height = newHeight + 'px';
}

/*
   handle form submission, start animation. this will also
   listen for a response from npu_server then append the messages
   to the chat dialog and hide the animation once a message is
   received
*/
const chatMessages = document.getElementById('chat-messages');
const form = document.getElementById('user-input');
const loader = document.querySelector('.loader');
const loaderBefore = document.querySelector('.loader:before');
const pupil = document.querySelector('.pupil');
const sendIcon = document.querySelector('.send-icon');

form.addEventListener('submit', function(event) {
    event.preventDefault();

    // Generate a random hash
    const randomHash = Math.random().toString(36).substring(2, 34);

    fetch('/search', {
        method: 'POST',
        body: new FormData(form)
    })
    .then(response => response.json())
    .then(data => {
        const newResponse = document.createElement('div');
        newResponse.classList.add('message', 'received');
        newResponse.setAttribute('id', randomHash);
        newResponse.innerHTML = `<p>${data.content}</p>`; //content = json key
        chatMessages.appendChild(newResponse);

        // Call the renderMarkdown() function of Markdown-Tag
        renderMarkdown(newResponse);

        // Create and insert copy button
        const copyBtn = document.createElement('button');
        copyBtn.setAttribute('id', 'copyBtn');
        copyBtn.setAttribute('class', 'copy-button');
        copyBtn.setAttribute('onclick', 'copyDivContents(this.parentElement.id)');
        copyBtn.innerHTML = '&#x2398;';
        copyBtn.addEventListener('click', function() {
            copyAnswerResponseContent(this);
        });
        newResponse.appendChild(copyBtn);

        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Hide loader and loader:before and unhide send-icon
        // this stops the animation
        loader.style.display = 'none';
        pupil.style.display = 'none';
        if (loaderBefore) {
            loaderBefore.style.display = 'none';
        }
        sendIcon.style.display = 'block';
    })
    .catch(error => {
        console.error('Error:', error);
        const failedMessage = document.createElement('div');
        failedMessage.classList.add('message', 'received');
        failedMessage.innerHTML = '<p>Failed to fetch. Is the server for this UI offline?</p>';
        chatMessages.appendChild(failedMessage);

        // Hide loader and loader:before and unhide send-icon
        // this stops the animation
        loader.style.display = 'none';
        pupil.style.display = 'none';
        if (loaderBefore) {
            loaderBefore.style.display = 'none';
        }
        sendIcon.style.display = 'block';
    });

    document.getElementById('input_text').value = '';
});

/*
    behavior for text entry (enter to send, allow shift+enter for newline)
*/
const inputTextElement = document.getElementById('input_text');
const sendButton = document.querySelector('.send-button');

inputTextElement.addEventListener('keydown', function(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    sendButton.click();
  }
});

/*
   behaviors for sent message
*/
sendButton.addEventListener('click', function() {
    const inputText = inputTextElement.value.trim();

    if (inputText) {
        const newMessage = document.createElement('div');
        newMessage.textContent = inputText;
        newMessage.classList.add('message', 'sent');
        chatMessages.appendChild(newMessage);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        const sendIcon = document.querySelector('.send-icon');
        sendIcon.style.display = 'none';

        const loaderDivs = document.querySelectorAll('.loader, .loader:before, .pupil');
        loaderDivs.forEach(div => div.style.display = 'block');

        form.dispatchEvent(new Event('submit'));

        inputTextElement.style.height = 'auto';
        inputTextElement.value = ''; // Clear the textarea after sending
    }
});

/*
   copy button behavior (copy text + animation)
*/
function copyDivContents(divId) {
  const div = document.getElementById(divId);
  const mdElement = div.querySelector('md');
  const mdText = mdElement.textContent;
  const tempInput = document.createElement('textarea');

  tempInput.value = mdText;
  document.body.appendChild(tempInput);

  tempInput.select();
  document.execCommand('copy');

  document.body.removeChild(tempInput);

  const button = document.getElementById('copyBtn');
  button.classList.add('animate');
  setTimeout(() => {
    button.classList.remove('animate');
  }, 1000);

  console.log('Copied text:', mdText);
}
