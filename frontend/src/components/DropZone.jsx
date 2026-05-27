import React from "react";
import { CloudUpload } from 'lucide-react';

const STYLES = {
    container: `
        flex flex-col items-center justify-center 
        min-h-62.5 p-8 border-2 border-dashed 
        border-gray-300 rounded-2xl bg-gray-100 
        hover:border-blue-400 transition-colors 
        duration-200 cursor-pointer max-w-lg mx=auto
    `,
    iconWrapper: "mb-4 text-gray-400",
    heading: "text-lg font-medium text-gray-700 text-center",
    browseLink: "text-blue-500 underline decoration-2 underline-offset-2",
    subtitle: "mt-2 text-sm text-gray-400 text-center"
}

function DropZone() {
    return(
        <div className={STYLES.container}>

            <div className={STYLES.iconWrapper}>
                <CloudUpload className="w-12 h-12" strokeWidth={2}/>
            </div>

            <h3 className={STYLES.heading}>
                Drag and drop your media here, or <span className={STYLES.browseLink}>click to browse</span>
            </h3>

            <p className={STYLES.subtitle}>
                MP4, MP3, or MKV up to 500 MB
            </p>
        </div>
    );
}

export default DropZone;