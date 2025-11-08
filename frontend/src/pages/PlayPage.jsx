import React, { useEffect, useMemo, useState } from "react";
import { getMode } from "../modes/registry.js";
import Header from "../components/Header";
import BottomTabs from "../components/BottomTab";
import { useNavigate } from "react-router-dom";

/**
 * PlayPage — Step 1a: shell only (no registry, no data)
 * Regions: Prompt Bar • Board slot • Action Bar
 * - Mobile-first layout
 * - Uses project palette
 */
export default function PlayPage() {
    const [modeId] = useState("tooth-select");
    const mode = useMemo(() => getMode(modeId), [modeId]);
    const navigate = useNavigate();

    const [roundData, setRoundData] = useState(null);
    const [answerDraft, setAnswerDraft] = useState(null);
    const [result, setResult] = useState(null);

    useEffect(() => {
        const rd = mode.createRound();
        setRoundData(rd);
        setAnswerDraft(mode.initialAnswer(rd));
        setResult(null);
    }, [mode]);

    function handleSubmit() {
        if (!mode || !roundData) return;
        const r = mode.evaluate(answerDraft, roundData);
        console.log("Evaluation:", r);
        setResult(r);
    }

    function handleNext() {
        const rd = mode.createRound();
        setRoundData(rd);
        setAnswerDraft(mode.initialAnswer(rd));
        setResult(null);
    }

    if (!mode || !roundData) return null;
    const Board = mode.Board;

    return (
        <div className="min-h-screen bg-[#98A1BC]">
            <Header />
            <div className="mx-auto w-full max-w-4xl px-3 md:px-4 lg:px-8 pb-20 md:pb-6">
                {/* Prompt Bar */}
                <div className="mt-3 rounded-xl bg-[#525470] px-4 py-3 text-[#F5EEDC]">
                    <h1 className="text-base font-semibold">{roundData.prompt}</h1>
                </div>

            {/* Board slot (placeholder) */}
            <div className="mt-4">
                <Board roundData={roundData} answerDraft={answerDraft} onChange={setAnswerDraft} />
            </div>

            {/* Action Bar */}
            <div className="mt-4 grid grid-cols-2 gap-3 max-w-xs sm:max-w-sm mx-auto">
                <button
                    type="button"
                    onClick={handleSubmit}
                    disabled={!!result}
                    className="rounded-lg bg-[#F5EEDC] px-4 py-2 font-medium text-[#525470]"
                >
                    Submit
                </button>
                <button
                    type="button"
                    onClick={handleNext}
                    className="rounded-lg border border-[#D9CEC1] px-4 py-2 font-medium"
                    style={{ background: "#98A1B6", color: "#F5EEDC" }}
                >
                    Skip
                </button>
            </div>
            {result && (
                <div className="mt-3 rounded-lg border border-[#D9CEC1] bg-white/70 p-3 text-sm text-[#525470]">
                    <p className="font-semibold text-lg">{result.correct ? "Correct!" : "Not quite!"}</p>
                    {/*<p className="mt-1">Score change: {result.scoreDelta > 0 ? "+" : ""}{result.scoreDelta}</p>*/}
                </div>
            )}
            </div>
            <BottomTabs
                active="play"
                onChange={(tab) => {
                    navigate(
                        tab === 'dashboard'
                            ? '/dashboard'
                            : tab === 'play'
                            ? '/play'
                            : '/leaderboard'
                    );
                }}
            />
        </div>
    );
}
