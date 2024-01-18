# YTLangF
YTLangF is a project to classify YouTube videos on your YouTube search page according to their language. How often have you searched for a topic on YouTube and clicked a video that had its title in say "English" and the video's content was not in English? So this project is aimed towards preventing such clickbaits on the Youtube platform.

## Requirements
- An x64-based Linux system (preferably an Ubuntu-based distro)
- Any chromium-based browser

## Installation instructions
YTLangF has both a Frontend and a Backend component. The Frontend component is a browser extension and the backend is a Python FastApi server. 

### Frontend
Enable developer mode in your Chromium-based browser and drag and drop the frontend folder to the extensions page. You can also load it using "load unpacked". This procedure depends on your browser. So you may search on how to load extensions on developer mode in your browser of choice.

### Backend
Create an account on MongoDB Atlas with a free cluster option and add a .env file in the "Backend" folder having your credentials to Atlas. The format of the file should look like this:

MONGODB_URI="mongodb+srv://<user>:<password>@cluster0.abuudvk.mongodb.net/?retryWrites=true&w=majority"

Make sure you have superuser permission and run:

```
chmod +x install.sh
./install.sh
cd src/
uvicorn main:app --reload
```
