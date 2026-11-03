import React, { useState, useRef } from "react";
import ReactPlayer from "react-player";
import {
    Play, Pause, RotateCcw, BookOpen,
    Layers, Image as ImageIcon, ChevronRight
} from "lucide-react";

const STYLES = {
    container: "max-w-7xl mx-auto p-6 text-zinc-100 grid grid-cols-1 lg:grid-cols-12 gap-6",
    header: "col-span-12 border-b border-zinc-800 pb-4 mb-2 flex justify-between items-center",
    headerTitle: "text-xl font-bold tracking-tight text-white flex items-center gap-2",
    badge: "px-3 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20",
    leftCol: "lg:col-span-6 flex flex-col gap-4",
    rightCol: "lg:col-span-6 flex flex-col gap-4 bg-zinc-900/60 border border-zinc-800/80 rounded-2xl p-5 backdrop-blur-sm min-h-[600px]",
    playerWrapper: "relative aspect-video bg-black rounded-2xl overflow-hidden border border-zinc-800 shadow-2xl",
    controlsBar: "flex items-center justify-between bg-zinc-900 border border-zinc-800 px-4 py-3 rounded-xl",
    btn: "p-2 hover:bg-zinc-800 rounded-lg text-zinc-300 hover:text-white transition-all flex items-center gap-1.5 text-xs font-medium cursor-pointer",
    timelineCard: "bg-zinc-900/40 border border-zinc-800/80 rounded-2xl p-4 flex flex-col gap-2 max-h-[300px] overflow-y-auto",
    timelineItem: "p-3 rounded-xl border border-zinc-800/50 hover:border-zinc-700 bg-zinc-950/40 cursor-pointer transition-all flex justify-between items-center group",
    activeTimelineItem: "border-blue-500/50 bg-blue-500/10 text-blue-300",
    tabHeader: "flex border-b border-zinc-800 pb-3 gap-4",
    tabBtn: "text-xs font-semibold uppercase tracking-wider px-3 py-1.5 rounded-lg transition-all cursor-pointer flex items-center gap-1.5",
    activeTab: "bg-white text-black font-bold shadow-sm",
    inactiveTab: "text-zinc-400 hover:text-white hover:bg-zinc-800/50",
    flashcardCard: "bg-zinc-950 border border-zinc-800 rounded-2xl p-6 min-h-[220px] flex flex-col justify-between cursor-pointer hover:border-zinc-700 transition-all shadow-lg",
    slideThumb: "rounded-xl border border-zinc-800 overflow-hidden bg-black aspect-video relative group cursor-pointer"
}

function StudyDashboard({ videoUrl, studyGuide, slidesMetadata }) {
    const playerRef = useRef(null);
    const [playing, setPlaying] = useState(false);
    const [activeTab, setActiveTab] = useState("notes"); // 3 tabs: notes, flashcards, slides
    const [selectedChapterIdx, setSelectedChapterIdx] = useState(0);
    const [flashcardFlipped, setFlashcardFlipped] = useState(false);
    const [currentCardIdx, setCurrentCardIdx] = useState(0);

    const chapters = studyGuide?.chapters || [];
    const currentChapter = chapters[selectedChapterIdx] || chapters[0];

    // Interactive chapter sync
    const handleSeekTo = (timestampSec) => {
        if (playerRef.current) {
            playerRef.current.seekTo(timestampSec, "seconds");
            setPlaying(true);
        }
    }

    const handleSkip = (seconds) => {
        if (playerRef.current) {
            const current = playerRef.current.getCurrentTime();
            playerRef.current.seekTo(current + seconds, "seconds")
        }
    }

    return (
        <div className={STYLES.container}>
            {/* Top Bar / Header */}
            <div className={STYLES.header}>
                <div>
                    <h2 className={STYLES.headerTitle}>
                        <BookOpen className="w-5 h-5 text-blue-400"/>
                    </h2>
                    <p className="text-xs text-zinc-400 mt-1">{studyGuide?.overall_summary?.slice(0, 140)}...</p>
                </div>
                <span className={STYLES.badge}>{chapters.length} Chapters Generated</span>
            </div>

            {/* LEFT COLUMN: Player & Timelines */}
            <div className={STYLES.leftCol}>
                {/* HTML5 Video Player / Youtube Embed */}
                <div className={STYLES.playerWrapper}>
                    <ReactPlayer
                        ref={playerRef}
                        url={videoUrl}
                        width="100%"
                        height="100%"
                        playing={playing}
                        controls={true}
                        onPlay={() => setPlaying(true)}
                        onPause={() => setPlaying(false)}
                    />
                </div>

                {/* Video Quick Controls */}
                <div className={STYLES.controlsBar}>
                    <button className={STYLES.btn} onClick={() => handleSkip(-10)}>
                        <RotateCcw className="w-4 h-4" /> -10s
                    </button>
                    <button className={STYLES.btn} onClick={() => setPlaying(!playing)}>
                        {playing ? <Pause className="w-4 h-4"/> : <Play className="w-4 h-4"/>}
                        {playing ? "Pause" : "Play"}
                    </button>
                    <button className={STYLES.btn} onClick={() => handleSkip(10)}>
                        <RotateCcw className="w-4 h-4" /> +10s
                    </button>
                    <span className="text-xs font-mono text-zinc-500">Sync Mode Active</span>
                </div>

                {/* Chapter Timelines */}
                <div className={STYLES.timelineCard}>
                    <h4 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-1">
                        Chapter Timelines:
                    </h4>
                    {chapters.map((chap, idx) => {
                        const isSelected = selectedChapterIdx === idx;
                        const minutes = Math.floor(chap.timestamp_start / 60);
                        const seconds = Math.floor(chap.timestamp_start % 60);
                        const timeStr = `${minutes.toString().padStart(2, "0")}: ${seconds}`;

                        return(
                            <div
                                key={idx}
                                onClick={() => {
                                    setSelectedChapterIdx(idx);
                                    handleSeekTo(chap.timestamp_start);
                                }}
                                className={`${STYLES.timelineItem} ${isSelected ? STYLES.activeTimelineItem : ""}`}
                            >
                                <div>
                                    <span className="text-xs font-mono font-bold mr-2 text-blue-400">[{timeStr}]</span>
                                    <span className="text-sm font-medium">{chap.title}</span>
                                </div>
                                <ChevronRight className="w-4 h-4  text-zinc-600 group-hover:text-zinc-300"/>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* RIGHT COLUMN: Notes, Flashcards & Extracted Slides */}
            <div className={STYLES.rightCol}>
                {/* Tab Headers */}
                <div className={STYLES.tabHeader}>
                    <button
                        onClick={() => setActiveTab("notes")}
                        className={`${STYLES.tabBtn} ${activeTab === "notes" ? STYLES.activeTab : STYLES.inactiveTab}`}
                    >
                        <BookOpen className="w-3.5 h-3.5" /> Notes
                    </button>
                    <button
                        onClick={() => setActiveTab("flashcards")}
                        className={`${STYLES.tabBtn} ${activeTab === "flashcards" ? STYLES.activeTab : STYLES.inactiveTab}`}
                    >
                        <Layers className="w-3.5 h-3.5" /> Flashcards ({currentChapter?.flashcards?.length || 0})
                    </button>
                    <button
                        onClick={() => setActiveTab("slides")}
                        className={`${STYLES.tabBtn} ${activeTab === "slides" ? STYLES.activeTab : STYLES.inactiveTab}`}
                    >
                        <ImageIcon className="w-3.5 h-3.5" /> Extracted Slides ({slidesMetadata?.length || 0})
                    </button>
                </div>

                {/* TAB 1: NOTES VIEW */}
                {activeTab === "notes" && (
                    <div className="flex flex-col gap-4 overflow-y-auto max-h-125 pr-2">
                        <div>
                            <h3 className="text-lg font-bold text-white">{currentChapter?.title}</h3>
                            <p className="text-xs text-blue-400 font-mono mt-0.5">
                                Start Time: {Math.floor(currentChapter?.timestamp_start / 60)}m {Math.floor(currentChapter?.timestamp_start % 60)}s
                            </p>
                        </div>

                        {/* Key Concepts */}
                        <div>
                            <h4 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2">Key Concepts:</h4>
                            <div className="flex flex-wrap gap-1.5">
                                {currentChapter?.key_concepts?.map((concept, i) => (
                                    <span key={i} className="px-2.5 py-1 bg-zinc-800 text-zinc-200 text-xs rounded-md border -700/60 font-medium">
                                        {concept}
                                    </span>
                                ))}
                            </div>
                        </div>

                        {/* Summary Notes */}
                        <div>
                            <h4 className="text-xs font-seminold text-zinc-400 uppercase tracking-wider mb-2">Chapter Notes:</h4>
                            <div className="text-sm text-zinc=300 leading-relaxed bg-zinc-950/60 p-4 rounded-xl border border-zinc-800/80 whitespace-pre-line">
                                {currentChapter?.summary_markdown}
                            </div>
                        </div>

                        {/* Jump to Time Button */}
                        <button
                            onClick={() => handleSeekTo(currentChapter?.timestamp_start)}
                            className="mt-2 w-full py-2.5 bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 border border-blue-500/30 rounded-xl text-xs font-semibold transition-all flex items-center justify-center gap-2 cursor-pointer"
                        >
                            <Play className="w-3.5 h-3.5"/> Jump to {Math.floor(currentChapter?.timestamp_start / 60)}:{Math.floor(currentChapter?.timestamp_start % 60).toString().padStart(2, "0")} in Video
                        </button>
                    </div>
                )}

                {/* TAB 2: ACTIVE RECALL FLASHCARDS WIDGET */}
                {activeTab === "flashcards" && (
                    <div className="flex flex-col gap-4">
                        <h4 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">
                            Active Recall Flashcard ({currentCardIdx + 1} of {currentChapter?.flashcards?.length || 1})
                        </h4>

                        {currentChapter?.flashcards?.length > 0 ? (
                            <div 
                                onClick={() => setFlashcardFlipped(!flashcardFlipped)}
                                className={STYLES.flashcardCard}                            
                            >
                                <div>
                                    <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest block mb-2">
                                        {flashcardFlipped ? "Answer" : "Question (Click to flip)"}
                                    </span>

                                    <p classname="text-base font-medium text-white leading-snug">
                                        {flashcardFlipped
                                            ? currentChapter.flashcards[currentCardIdx].back
                                            : currentChapter.flashcards[currentCardIdx].front}
                                    </p>
                                </div>
                                <span classname="text-xs text-blue-400 font-semibold self-end">
                                    {flashcardFlipped ? "Click to see Question" : "Show Answer →"}
                                </span>
                            </div>
                        ): (
                            <p className="text-sm text-zinc-500 italic">No flashcards available for this chapter</p>
                        )}

                        {/* Flashcard Navigation */}
                        <div className="flex justify-between items-center mt-2">
                            <button
                                disabled={currentCardIdx === 0}
                                onClick={() => {
                                    setFlashcardFlipped(false);
                                    setCurrentCardIdx(c => Math.max(0, c - 1))
                                }}
                                className="px-4 py-2 bg-zinc-800 disabled: opacity-40 text-xs font-medium rounded-lg hover:bg-zinc-700 transition-all cursor-pointer"
                            >
                                ← Previous Card
                            </button>
                            <button
                                disabled={currentCardIdx >= (currentChapter?.flashcards?.length || 1) - 1}
                                onClick={() => {
                                    setFlashcardFlipped(false);
                                    setCurrentCardIdx(c => Math.min(currentChapter?.flashcards?.length - 1, c + 1))
                                    className="px-4 py-2 bg-zinc-800 disabled: opacity-40 text-xs font-medium rounded-lg hover:bg-zinc-700 transition-all cursor-pointer"
                                }}
                            >
                                Next Card →
                            </button>
                        </div>
                    </div>
                )}

                {/* TAB 3: EXTRACTED SLIDES SYNC VIEWER */}
                {activeTab === "slides" && (
                    <div classname="grid grid-cols-2 gap-3 overflow-y-auto max-h-[500] pr-2">
                        {slidesMetadata?.map((slide, idx) => (
                            <div
                                key={idx}
                                onClick={() => handleSeekTo(slide.timestamp_start)}
                                className={STYLES.slideThumb}
                            >
                                <img
                                    src={`http://localhost:8000/${slide.image_path.replace(/\\/g, "/")}`}
                                    alt={`Slide ${slide.slide_id}`}
                                    className="w-full h-full object-cover"
                                />
                                <div className="absolute inset-0 bg-linear-to-t from-black/80 via-transparent to-transparent opacity-90 p-2 flex flex-col justify-end">
                                    <span className="text-[10px]" font-mono text-blue-300 font-bold>
                                        Slide {slide.slide_id} @ {Math.floor(slide.timestamp_start)}s
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}

export default StudyDashboard;