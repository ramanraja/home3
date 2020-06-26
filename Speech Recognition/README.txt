Speech recognition on Chrome, using Web Speech API:
This needs an active internet connection to work.
https://www.freecodecamp.org/news/how-to-build-a-simple-speech-recognition-app-a65860da6108/

Download the html, CSS and JS files from the above blog.
Download some mp3 sound byte and rename it chime.mp3.
Put all of the above in a folder named, say,  'mywebserver'

Go one level above from the mywebserver folder.
> cd..

Run the python web server:
> C:\ProgramData\Anaconda3\python  -m  http.server  7000

Open Chrome and navigate to:
http://127.0.0.1:7000/mywebserver/

You will see a button. Click that. You will hear a chime.
After the chime, record a voice messge.
It will be transcribed and appear in the window.
