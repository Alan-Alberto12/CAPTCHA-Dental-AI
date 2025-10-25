import ToothSelectBoard from "./ToothSelectBoard.jsx";

// Mock round generator (replace with API later)
function createRound() {
  const prompt = "Select all instances of tooth #14";
  const tiles = Array.from({ length: 4 }, (_, i) => ({
    id: String(i + 1),
    imgSrc: `https://picsum.photos/seed/tooth${i + 1}/160/160`,
  }));
  const solution = new Set(["2", "3"]); // mock answer set
  return { prompt, boardData: { tiles, cols: 2 }, solution };
}

function initialAnswer() {
  return new Set();
}

// Simple evaluation: +1 correct pick, -1 incorrect; false if any miss
function evaluate(answerDraft, roundData) {
  const sel = answerDraft || new Set();
  let score = 0;
  let correct = true;

  roundData.boardData.tiles.forEach((t) => {
    const picked = sel.has(t.id);
    const should = roundData.solution.has(t.id);
    if (picked && should) score += 1;
    if (picked && !should) score -= 1;
    if (!picked && should) correct = false;
    if (picked && !should) correct = false;
  });

  return { correct, scoreDelta: score, details: {} };
}

export default {
  id: "tooth-select",
  label: "Tooth Select",
  createRound,
  initialAnswer,
  evaluate,
  Board: ToothSelectBoard,
};
