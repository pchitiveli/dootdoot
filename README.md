![DootDoot Logo](https://github.com/santhoshv25/Hackathon-2024-Website/blob/main/images/DootDootFullLogo.png?raw=true)
# DootDoot


## What is DootDoot

This is **DootDoot**, an app to convert audio recoordings into sheet music. Have you ever wanted to learn to play a piece music but just never had a chance to transcribe it? Well this program is the perfect solution for you! Whether is uploading a recording of music you heard live or a riff from a song you want to learn, this app has it all. Learn to play your favorite pieces with DootDoot.

## How it works

**DootDoot** uses a variety of technologies to be able to achieve the capabilities it has. The website uploadds the .wav file to a Flask server. This then preprocesses the audio file by reducing background noise and cropping out unnecessary scilences. Afterwards, it extracts various featrue such as the BPMs. Using the BPM, the troughts, and peaks found in the .wav file, it splits the file into individual notes. These notes are converted into chromograms and the pitch is analyzed to get a the note value. This value is then further validated by a custom deep CNN model we built by scratch. The note is converted into a spectrogram and fed into the deep CNN model to get the note value. Once we have all the notes, we convert it into a pdf and send it back to the website for the user to download.
