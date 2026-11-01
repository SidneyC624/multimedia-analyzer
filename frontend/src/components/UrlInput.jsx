import React, { useState } from 'react';
import { Link2, ArrowRight, DivideCircle } from 'lucide-react';

const STYLES = {
    container: "max-w-lg mx-auto p-8 border border-zinc-800 rounded-2xl bg-zinc-900/30 flex flex-col items-center text-center",
    iconWrapper: "mb-4 text-zinc-400",
    heading: "text-lg font-medium text-zinc-300 mb-2",
    subtitle: "text-sm text-zinc-500 mb-6",
    form: "w-full flex gap-2",
    input: "flex-1 bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 text-sm text-zinc100 placeholder-zinc-600 focus:outline-none focus:border-zinc-600 transition-all",
    button: "bg-white text-black font-medium px-5 py-3 rounded-xl text-sm flex items-center justify-center gap-2 hover:bg-zinc-200 transition-all cursor-pointer disabled:opacity-50",
    errorText: "mt-3 text-sm font-semibold text-red-500 text-center"
};

function UrlInput({ onSubmit }) {
    const [url, setUrl] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!url.trim()) {
            setError("Please enter a valid URL.");
            return
        }
        setError("");
        onSubmit(url.trim());
    };

    return (
        <div className={STYLES.container}>
            <div className={STYLES.iconWrapper}>
                <Link2 className="w-10 h-10" strokeWidth={1.5}/>
            </div>
            <h3 className={STYLES.heading}>Paste your lecture or media link</h3>
            <p className={STYLES.subtitle}>Supports Youtube links and public video URLS</p>

            <form onSubmit={handleSubmit} className={STYLES.form}>
                <input 
                    type="url"
                    placeholder='https://www.youtube.com/watch?v=...'
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    className={STYLES.input}                
                />
                <button type="submit" className={STYLES.button}>
                    Analyze <ArrowRight className="w-4 h-4" />
                </button>
            </form>

            {error && <p className={STYLES.errorText}>{error}</p>}
        </div>
    );
}

export default UrlInput;