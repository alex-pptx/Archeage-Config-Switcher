<div align="center">
  
<img src="aacs.ico" />

</div>

<h1 align="center">Archeage-Config-Switcher</h1>

A simple app for convienently swapping Archeage config files - for example load a config file with low graphics settings for pvp or load a config file with high graphics settings for taking screenshots.

<br>

<div align="center">
  
<img width="302" height="383" alt="image" src="https://github.com/user-attachments/assets/6a6303c8-a6f6-4c94-899f-73cd1502d687" />
<img width="307" height="386" alt="image" src="https://github.com/user-attachments/assets/f926abe5-5caa-4028-8165-c152cc4015cf" />
<img width="406" height="388" alt="image" src="https://github.com/user-attachments/assets/c6e6ae2e-ca68-4834-83af-82f292d139f6" />

</div>

<h2>Usage</h2>

- Download and run aacs.exe
- On first start up the app will auto-detect your Archeage Classic documents directory (ex: C:/Documents/AAClassic).
  - Use the "Change AA Directory" button if dectected folder is incorrect or if you want to point to another Archeage instance.
- To backup a config file: Click "Save New Config" and navigate to the system.cfg file you want to save/backup (ex: C:/Documents/AAClassic/system.cfg).
- To load a config file: Select an option from the dropdown and click "Load Config".
  - Note: this will overwrite your active config file located at ~/Documents/AAClassic/system.cfg
- To delete a config file: Select an option from the dropdown and click "Delete Config".

<h2>Build it yourself</h2>

- Install python (https://www.python.org/downloads/).
- Clone the repo.
- Install dependencies:

```
pip install -r requirements.txt
```
- Run it:
```
py aacs.py
```
