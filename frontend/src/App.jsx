import React, { useState, useEffect } from 'react';
import UrlInput from './components/UrlInput';
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

    const [submittedUrl, setSubmittedUrl] = useState(null);
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

    const handleUrlSubmit = (url) => {
      console.log("App.jsx caught the URL successfully! ", url);
      setSubmittedUrl(url);
      sendUrlToBackend(url);
    };

    const sendUrlToBackend = async (url) => {
      setUiError(null);

      try {
        const response = await axios.post("http://localhost:8000/submit-url", { url });
        setJobId(response.data.job_id);
        setStatus(response.data.status);
      }
      catch(e) {
        console.error("Submission failed", e.response?.data?.detail || e.message);
        setUiError(e.response?.data?.detail || "Server unreachable. Please try again later.")
      }
    };

    return(
      <div className={STYLES.screenWrapper}>
        <h1 className={STYLES.title}>Multimedia Content Analyzer</h1>

        <UrlInput onSubmit={handleUrlSubmit} />

        {submittedUrl && (
          <div className={STYLES.statusCard}>
            <p className={STYLES.statusTitle}>Submitted Link:</p>
            <p className={STYLES.statusDetails}>{submittedUrl}</p>
          </div>
        )}

        {jobId && status === "pending" && (
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
