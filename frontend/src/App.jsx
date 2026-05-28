import React, { useState } from 'react';
import DropZone from "./components/DropZone";

const STYLES = {
    screenWrapper: "min-h-screen bg-gray-50 p-12",
    title: "text-2xl font-bold text-center mb-8",
    statusCard: "mt-4 p-4 border rounded bg-white max-w-lg mx-auto shadow-sm",
    statusTitle: "text-green-600 font-medium",
    statusDetails: "text-gray-600 text-sm"
};

function App() {

    const [selectedFile, setSelectedFile] = useState(null);

    const handleFileCheck = (validFile) => {
      console.log("App.jsx caught the file successfully! ", validFile);
      setSelectedFile(validFile);

    };

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
      </div>
    );
}

export default App
