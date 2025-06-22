import React, { useRef, useState } from 'react'
import WebcamDetection from './WebcamDetection';


export default function MainPage() {
    const [imageSrc , setImageSrc] = useState(null) ;
    const fileInputRef = useRef(null) ;
    const [loading, setLoading] = useState(null) ;
    const [prediction, setPrediction] = useState({label:null , conf:null}) ;
    const [mode, setMode] = useState("upload");

    const handleUpload = async () => {
      if (!fileInputRef.current.files[0]) {
        alert("Please select an image first!");
        return;
    }

    const formData = new FormData();
    formData.append("image", fileInputRef.current.files[0]); // Append the file directly from the input
    
    setLoading(true); // Start loading animation or status
    
    try {
        const response = await fetch("http://127.0.0.1:5000/predict-emotion", {
            method: "POST",
            body: formData, // Send as FormData
        });
        const data = await response.json();
        if (data.label && data.conf) {
            const pred = {
              label: data.label ,
              conf: data.conf
            } ;
            setPrediction(pred); // Set the predicted emotion
        } else {
            setPrediction("Error in prediction");
        }
    } catch (error) {
        console.error("Error:", error);
        setPrediction("Error uploading image");
    } finally {
        setLoading(false); // Stop loading status
    }
      };

    const handleFileSelect = () => {
      const file = fileInputRef.current.files[0]; // Access the selected file
      if (file) {
          setImageSrc(URL.createObjectURL(file)); // Display the image preview using ObjectURL
      }
      };

    return (
        <div style={{
        height: '100vh' ,
        width: '100vw' ,
        display: 'flex' ,
        flexDirection: 'column' ,
        alignItems: 'center' , 
        justifyContent: 'center' , 
        border: '2px solid white' ,
      }}>
      <div style={{ marginBottom: 20 }}>
        <button onClick={() => setMode("upload")}>Upload mode</button>
        <button onClick={() => setMode("webcam")}>Webcam mode</button>
      </div>

      {mode === "webcam" && <WebcamDetection />}
      {mode === "upload" && (
        <>
        <input
        type="file"
        ref={fileInputRef}
        accept="image/*" 
        onChange={handleFileSelect} 
        style={{ marginBottom: '10px' , display: 'none' }}
      />
      {imageSrc && (
        <div>
          <img
            src={imageSrc}
            alt="Uploaded"
            style={{
              width: 'auto',
              height: 'auto',
              border: '2px solid white',
              borderRadius: '10px',
              marginTop: '20px',
            }}
          />
        </div>
      )}
        <button onClick={() => fileInputRef.current.click()}>Upload image</button>
        <button onClick={handleUpload}>{ loading ? "Processing..." : "Let AI guess the emotion" }</button>
        {prediction.label !== null && prediction.conf !== null && (
        <>
          <p>Emotion: {prediction.label}</p>
          <p>Confidence score: {prediction.conf}</p>
        </>
       )}
      </>
      )}
    </div>
    );
}
