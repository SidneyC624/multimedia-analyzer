import React from 'react';

const STYLES = {
    wrapper: "w-full max-w-lg mx-auto my-4",
    labelWrapper: "flex justify-between items-center mb-1.5",
    labelText: "text-sm font-medium text-gray-700",
    percentText: "text-sm font-semibold text-blue-600",
    track: "w-full h-3 bg-gray-200 rounded-full overflow-hidden shadow-inner",
    fill: "h-full bg-blue-600 rounded-full transition-all duration-300 ease-out"
};


function ProgressBar({currentValue = 0, label, maxValue = 100}) {

    const percentage = Math.min(
        Math.max(Math.round((currentValue / maxValue) * 100), 0),
        100
    );

    return(
        <div className={STYLES.wrapper}>
            <div className={STYLES.labelWrapper}>
                {label && <span className={STYLES.labelText}>{label}</span>}
                <span className={STYLES.percentText}>{percentage}%</span>
            </div>

            <div className={STYLES.track} role="progressbar" aria-valuenow={percentage} aria-valuemin="0" aria-valuemax="100">
                <div
                    className={STYLES.fill}
                    style={{ width: `${percentage}%` }}
                />
            </div>
        </div>
    );
}

export default ProgressBar;