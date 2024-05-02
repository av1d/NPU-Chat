# Web UI for rk3588_npu_llm_server  

Chat interface for LLM running on RK3588 NPU.  


![Screenshot 01](https://github.com/av1d/NPU-Chat/blob/main/screenshots/desktop.png)  


![Screenshot 02](https://github.com/av1d/NPU-Chat/blob/main/screenshots/mobile.jpg)

install:  
You must first be running https://github.com/av1d/rk3588_npu_llm_server  
then:  
`python3 -m pip install -r requirements.txt`  

configure:  
Edit `settings.ini` with your information.  

run:  
`python3 npuchat.py`  

then navigate to the IP/port in your browser.  

Works in any browser besides Firefox desktop or mobile (but maybe nightly, with the correct settings).
