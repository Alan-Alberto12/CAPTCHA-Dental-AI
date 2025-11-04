import React from "react";

/**
 * ToothSelectBoard
 * Renders a 3×4 grid from mock tiles; tap toggles selection.
 * Props:
 *  - roundData: { boardData: { tiles: [{ id, imgSrc }], cols?: number } }
 *  - answerDraft: Set<string>
 *  - onChange: (next: Set<string>) => void
 */
export default function ToothSelectBoard({ roundData, answerDraft, onChange }) {
    const { tiles = [], cols = 2 } = roundData.boardData || {};

    function toggle(id) {
        const next = new Set(answerDraft || []);
        next.has(id) ? next.delete(id) : next.add(id);
        onChange(next);
    }

    return (
        <div className="w-full flex justify-center">
            <div
                className="grid gap-2 sm:gap-3 justify-items-center"
                style={{ gridTemplateColumns: `repeat(${cols}, max-content)` }}
            >
                {tiles.map((t) => {
                    const selected = answerDraft?.has(t.id);
                    return (
                        <button
                            key={t.id}
                            type="button"
                            onClick={() => toggle(t.id)}
                            aria-pressed={selected}
                            className={[
                                "relative aspect-square hover:cursor-pointer",
                                "w-[clamp(120px,40vw,180px)]",
                                "sm:w-[clamp(130px,32vw,200px)]",
                                "md:w-[clamp(150px,26vw,220px)]",
                                "lg:w-[clamp(170px,20vw,220px)]",
                                "overflow-hidden rounded-lg border transition",
                                selected ? "border-[#D9CEC1] ring-2 ring-[#D9CEC1]" : "border-white/60",
                            ].join(" ")}
                        >
                            {/* eslint-disable-next-line jsx-a11y/alt-text */}
                            <img src={t.imgSrc} className="h-full w-full object-cover" />
                        </button>
                    );
                })}
            </div>
        </div>
    );
}
