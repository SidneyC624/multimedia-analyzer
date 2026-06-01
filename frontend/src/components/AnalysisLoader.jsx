import React from 'react';
import { Loader2 } from 'lucide-react';

function AnalysisLoader({ jobId, status }) {

    const STYLES = {
        cardContainer: "max-w-lg mx-auto mt-4 p-6 border border-zinc-800 rounded-xl bg-zinc-900 shadow-2xl flex flex-col items-center justify-center text-center",
        spinner: "w-6 h-6 text-zinc-400 animate-spin mb-4",
        title: "text-base font-semibold text-white mb-1 mt-3 tracking-tight",
        description: "text-xs text-zinc-400 max-w-xs mt-1 mb-4",
        pulsingBadge: "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20 uppercase tracking-wider animate-pulse mb-3",
        metadataID: "text-[10px] font-mono text-zinc-500 bg-zinc-950 px-2 py-1 rounded border border-zinc-800/60"
    };

    return(
        <div className={STYLES.cardContainer}>
            <Loader2 className={STYLES.spinner} />
            <h3 className={STYLES.title}>File Upload Complete!</h3>
            <p className={STYLES.description}>Your file was received successfully...</p>
            {/* Dynamic Pulsing Badge based on status */}
            <div className={STYLES.pulsingBadge}>
                {status  || "Pending"}
            </div>
            <div className={STYLES.metadataID}>
                ID: {jobId}
            </div>
        </div>
    );
}

export default AnalysisLoader;