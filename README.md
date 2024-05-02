# Web UI for rk3588_npu_llm_server  

Chat interface for LLM running on RK3588 NPU. Responsive design for desktop & mobile.  


  
![Screenshot 01](https://github.com/av1d/NPU-Chat/blob/main/screenshots/desktop.png)  


![Screenshot 02](https://github.com/av1d/NPU-Chat/blob/main/screenshots/mobile.jpg)

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
