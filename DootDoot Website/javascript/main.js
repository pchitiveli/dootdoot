document.getElementById('uploadForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const formData = new FormData(); // holds form data
    const fileInput = document.getElementById('myFile').files[0];

    if (!fileInput) { // alerts user if file wasn't selected
        alert('Please select a file first');
        return;
    }

    formData.append('file', fileInput);

    try { //sends post request with form data to URL
        const response = await fetch('http://127.0.0.1:5500/ ...', { /*input python backend integration file here*/
            method: 'POST',
            body: formData
        });
       
        // Checks if response is successful from the server
        if (response.ok) {
            const blob = await response.blob();
            const pdfUrl = URL.createObjectURL(blob); // Creates a source from the URL to use as the PDF viewer
           
            document.getElementById('pdfViewer').style.display = 'block';
            const pdfFrame = document.getElementById('pdfFrame');
            pdfFrame.src = pdfUrl;


            const downloadButton = document.getElementById('downloadPdf');
            downloadButton.onclick = () => {
                const a = document.createElement('a');
                a.href = pdfUrl;
                a.download = 'sheet_music.pdf';
                a.click();
            };
        } else {
            alert('Failed to process file.');
        }
    } catch (error) { //Checks for any errors that occurs during fetch process
        console.error('Error:', error);
        alert('An error occurred while processing file.');
    }
});

let mediaRecorder;
let audioChunks = [];

const startButton = document.getElementById('startRecording');
const stopButton = document.getElementById('stopRecording');
const uploadButton = document.getElementById('uploadRecording');

    
