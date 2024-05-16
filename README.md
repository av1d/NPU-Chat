# NPU Chat
## _a Web UI for rk3588_npu_llm_server_

Chat interface for LLM running on RK3588 NPU. Responsive design for desktop & mobile.  

### Recent updates:  
#### 2024-05-16
* New version: 0.27
* New alternate UI theme availalble. Select it in settings.ini.
* New visual UI enhancements (touched up bloated rounded styles), better user-input text formatting.
* Front-end error handling in JS now alerts if any servers are offline.
* New `context` command prints current context.

##### 2024-05-16
* New version: 0.26
* Experimental: You can now (optionally) use chat contexts. Use the commands `clear`, `off`, `on` to manipulate the state.
* Improved error handling for non-2xx HTTP status codes in case of error or server offline.
* Added new parameters to `settings.ini` pertaining to contexts and error handling.
* Code cleanup: Added docstrings and improved commenting for better code readability.


  
![Screenshot 01](https://github.com/av1d/NPU-Chat/blob/main/screenshots/desktop.png)  


**install:**  
You must first be running https://github.com/av1d/rk3588_npu_llm_server  
then:  
`python3 -m pip install -r requirements.txt`  

**configure:**  
Edit `settings.ini` with your information.  

**run:**  
`python3 npuchat.py`  

then navigate to the IP/port in your browser.  

Works in any browser besides Firefox desktop or mobile (but maybe nightly, with the correct settings).  

**Known issues:**  
Some models don't output valid markdown for everything. For example, if you ask Qwen `show me a list of emoji`, it will not be valid markdown.  
The problem is it uses newline (`\n`) after each item in the emoji list, but we can't convert it to `<br>` without potentially destroying all code that passes through. It would be a bad idea. The problem is further complicated by markdown validators do not consider this emoji list to be invalid markdown, so we cannot apply conditional rules. If you have a solution I would love to hear it.
