import React from 'react';
import { Loader2 } from 'lucide-react';

function AnalysisLoader({ jobId, status }) {

    const STYLES = {
        cardContainer: "max-w-lg mx-auto mt-6 p-8 border border-zinc-800 rounded-2xl bg-zinc-900/50 backdrop-blur-sm shadow-2xl flex flex-col items-center justify-center text-center",
        spinner: "w-8 h-8 text-blue-400 animate-spin mb-3",
        title: "text-lg font-bold text-white mb-1 tracking-tight",
        description: "text-xs text-zinc-400 max-w-sm mt-1 mb-5 leading-relaxed",
        pulsingBadge: "inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider animate-pulse mb-4",
        metadataID: "text-[10px] font-mono text-zinc-500 bg-zinc-950 px-2.5 py-1 rounded-md border border-zinc-800/80"
    };

    const isProcessing = status === "processing";

    const titleText = isProcessing ? 
                        "Analyzing Lecture Content..." : 
                        "Linked Received";

    const descriptionText = isProcessing 
                            ? "Extracting video keyframes, transcribing audio and generating AI notes & flashcards. This may take a minute..."
                            : "Queued for processing. Preparing multimedia pipeline..."

    const badgeStyle = isProcessing
                        ? "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                        : "bg-amber-500/10 text-amber-400 border border-amber-500/20";

    return(
        <div className={STYLES.cardContainer}>
            <Loader2 className={STYLES.spinner} />

            <h3 className={STYLES.title}>{titleText}</h3>
            <p className={STYLES.description}>{descriptionText}</p>

            {/* Dynamic Pulsing Badge based on status */}
            <div className={`${STYLES.pulsingBadge} ${badgeStyle}`}>
                {status  || "Pending"}
            </div>

            <div className={STYLES.metadataID}>
                Job ID: {jobId}
            </div>
        </div>
    );
}

export default AnalysisLoader;