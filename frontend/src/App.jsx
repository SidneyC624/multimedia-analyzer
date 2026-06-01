import React, { useState, useEffect } from 'react';
import DropZone from "./components/DropZone";
import ProgressBar from './components/ProgressBar';
import AnalysisLoader from './components/AnalysisLoader';
import axios from 'axios';

const STYLES = {
    screenWrapper: "min-h-screen bg-black text-zinc-50 p-12",
    title: "text-2xl font-bold text-center mb-8 tracking-tight text-white",
    statusCard: "mt-4 p-4 border border-zinc-800 bg-zinc-900/50 rounded-xl max-w-lg mx-auto backdrop-blur-sm",
    statusTitle: "text-zinc-400 text-xs font-medium uppercase tracking-wider",
    statusDetails: "text-zinc-200 text-sm font-medium mt-1",
    uiError: "mt-4 p-3 bg-red-500/10 border border-red-500/20 text-red-400 text-sm rounded-xl text-center max-w-lg mx-auto"
};

function App() {

    const [selectedFile, setSelectedFile] = useState(null);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [isUploading, setIsUploading] = useState(false);
    const [jobId, setJobId] = useState(null);
    const [status, setStatus] = useState(null);
    const [uiError, setUiError] = useState(null);

    useEffect(() => {
      if (!jobId) {
        return
      }

      const polling = async () => {
        const response = await axios.get(`http://localhost:8000/status/${jobId}`);
        setStatus(response.data.status);
        // state updates do not happen instantly, status would originally be null
        if (response.data.status === "completed" || response.data.status === "failed") {
          clearInterval(intervalId);
        }
      }

      const intervalId = setInterval(polling, 3000)
      return () => {
        clearInterval(intervalId);
      };
    }, [jobId]);

    const handleFileCheck = (validFile) => {
      console.log("App.jsx caught the file successfully! ", validFile);
      setSelectedFile(validFile);
      uploadMediaFile(validFile);
    };

    const uploadMediaFile = async (file) => {
      const formData = new FormData();
      formData.append("file", file);
      setUiError(null);

      try {
        setIsUploading(true);
        const response = await axios.post("http://localhost:8000/upload", formData, {
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(percentCompleted);
          }
        })

        setJobId(response.data.job_id);
        setStatus(response.data.status);
      }
      catch(e) {
        console.error("Upload failed", e.response?.data?.detail || e.message);
        setUiError(e.response?.data?.detail || "Server unreachable. Please try again later.")
      }
      finally {
        setIsUploading(false);
      }
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

        {jobId && status === "pending" && !isUploading && (
          <AnalysisLoader jobId={jobId} status={status}/>
        )}

        {uiError && (
          <div className={STYLES.uiError}>
            {uiError}
          </div>
        )}
      </div>
    );
}

export default App
