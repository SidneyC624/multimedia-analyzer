import React, { useState } from 'react';
import DropZone from "./components/DropZone";
import ProgressBar from './components/ProgressBar';
import axios from 'axios';

const STYLES = {
    screenWrapper: "min-h-screen bg-gray-50 p-12",
    title: "text-2xl font-bold text-center mb-8",
    statusCard: "mt-4 p-4 border rounded bg-white max-w-lg mx-auto shadow-sm",
    statusTitle: "text-green-600 font-medium",
    statusDetails: "text-gray-600 text-sm"
};

function App() {

    const [selectedFile, setSelectedFile] = useState(null);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [isUploading, setIsUploading] = useState(false);
    const [jobId, setJobId] = useState(null);
    const [status, setStatus] = useState(null);

    const handleFileCheck = (validFile) => {
      console.log("App.jsx caught the file successfully! ", validFile);
      setSelectedFile(validFile);
      uploadMediaFile(selectedFile);
    };

    const uploadMediaFile = async (file) => {
      const formData = new FormData();
      formData.append("file", file);

      try {
        setIsUploading(true);
        const response = await axios.post("http://localhost:8000/upload", formData, {
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(percentCompleted);
          }
        })

        
      }
      catch(e) {
        console.error("Upload failed", e.response?.data?.detail || e.message);
      }
      finally {
        setIsUploading(false);
      }

      setJobId(response.data.jobId);
      setStatus(response.data.status);
    }

    return(
      <div className={STYLES.screenWrapper}>
        <h1 className={STYLES.title}>Multimedia Content Analyzer</h1>

        <DropZone onFileSelect={handleFileCheck}/>

        {selectedFile && (
          <div className={STYLES.statusCard}>
            <p className={STYLES.statusTitle}>Ready for backend processing:</p>
            <p className={STYLES.statusDetails}>
              {selectedFile.name} ({(selectedFile.size / (1024 * 1024)).toFixed(2)} MB)
            </p>
          </div>
        )}

        {isUploading && (
          <ProgressBar 
            currentValue={uploadProgress}
            label="Uploading"
          />
        )}
      </div>
    );
}

export default App
