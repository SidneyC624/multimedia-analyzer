import React, {useState, useRef} from 'react';
import { CloudUpload } from 'lucide-react';

const STYLES = {
    container: `
        flex flex-col items-center justify-center 
        min-h-[250px] p-8 border-2 border-dashed 
        rounded-2xl transition-all 
        duration-200 cursor-pointer max-w-lg mx-auto
    `,
    iconWrapper: "mb-4 text-gray-400",
    heading: "text-lg font-medium text-gray-700 text-center",
    browseLink: "text-blue-500 underline decoration-2 underline-offset-2",
    subtitle: "mt-2 text-sm text-gray-400 text-center",
    errorText: "mt-3 text-sm font-semibold text-red-500 text-center"
}


function DropZone({ onFileSelect }) {

    const [isDragging, setIsDragging] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");

    // invisible input for triggering file browser
    const fileInputRef = useRef(null);

    const handleDragEnter = (e) => {
        e.stopPropagation();
        // allows for valid drop zone
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.stopPropagation();
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDragOver = (e) => {
        e.stopPropagation();
        e.preventDefault();
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);

        const files = e.dataTransfer.files;
        handleProcessFiles(files);
    };

    const handleContainerClick = () => {
        fileInputRef.current.click();
    };

    const handleFileChange = (e) => {
        const files = e.target.files;
        handleProcessFiles(files);
    };  

    const handleProcessFiles = (files) => {
        if(!files || files.length === 0) return;
        // if there was error before, clear it
        setErrorMessage("");

        const file = files[0];

        // --- Check file size and extension --- 
        const MAX_FILE_SIZE = 500 * 1024 * 1024;
        if(file.size > MAX_FILE_SIZE) {
            setErrorMessage("File is too large. 500MB is the maximum allowed size.");
            return;
        }

        const allowedExtensions = /(\.mp4|\.mp3|\.mkv)$/i;
        if(!allowedExtensions.test(file.name)) {
            setErrorMessage("Invalid file type. Please upload an MP4, MP3 or MKV file.");
            return;
        }

        console.log("File passed frontend checks, ready to upload: ", file.name);

        if (onFileSelect) {
            onFileSelect(file);
        }
    };

    return(
        <div className={`
                ${STYLES.container}
                ${isDragging
                    // Dynamic UI when dragged over
                    ? "border-blue-500 bg-blue50/50 scale-[1.02]"
                    : !errorMessage ? "border-gray-300 bg-gray-100 hover:bg-gray-100/70 hover:border-blue-400" : ""
                }
            `}
            
            onDragEnter={handleDragEnter}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={handleContainerClick}
        >
            {/* Icon tint if there is an error */}
            <div className={`${STYLES.iconWrapper} ${errorMessage ? 'text-red-400' : ''}`}>
                <CloudUpload className="w-12 h-12" strokeWidth={2}/>
            </div>

            <h3 className={STYLES.heading}>
                Drag and drop your media here, or <span className={STYLES.browseLink}>click to browse</span>
            </h3>

            <p className={STYLES.subtitle}>
                MP4, MP3, or MKV up to 500 MB
            </p>
            
            {errorMessage && (
                <p className={STYLES.errorText}>
                    {errorMessage}
                </p>
            )}

            <input 
                ref={fileInputRef}
                className="hidden" 
                type="file" 
                accept=".mp4,.mp3,.mkv"
                onChange={handleFileChange}
            />
        </div>
    );
}

export default DropZone;