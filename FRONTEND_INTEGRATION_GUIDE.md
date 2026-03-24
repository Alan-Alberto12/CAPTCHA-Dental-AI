# Frontend Integration Guide

## 📱 How the Frontend Will Work

### **User Flow:**

1. **User logs in** → Gets session with 4 images and questions
2. **For each question:**
   - Display the question text
   - Show all 4 images in a grid
   - User clicks on images to select them
   - Submit answer with selected image IDs

---

## 🎨 UI Component Structure

### **Session Page Layout**

```
┌─────────────────────────────────────────────────┐
│  Question 1 of 5                                │
│  "Select all images showing tooth #14"          │
├─────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│  │ Image 1  │  │ Image 2  │  │ Image 3  │  │ Image 4  │
│  │    🖼️    │  │    🖼️    │  │    🖼️    │  │    🖼️    │
│  │  [ ]     │  │  [✓]     │  │  [ ]     │  │  [✓]     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘
│                                                          │
│              [Submit Answer] [Skip]                     │
└─────────────────────────────────────────────────────────┘
```

---

## 🔌 API Integration (React Example)

### **1. Start Session**

```typescript
// Get new session
const startSession = async () => {
  const response = await fetch('http://localhost:8000/auth/sessions/next?num_images=4&num_questions=5', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  const data = await response.json();
  /*
  {
    session_id: 1,
    images: [
      { id: 1, filename: "tooth14.jpg", image_url: "https://...", order: 1 },
      { id: 2, filename: "tooth12.jpg", image_url: "https://...", order: 2 },
      { id: 3, filename: "cavity.jpg", image_url: "https://...", order: 3 },
      { id: 4, filename: "gums.jpg", image_url: "https://...", order: 4 }
    ],
    questions: [
      { id: 50, question_text: "Select all images showing tooth #14", order: 1 },
      { id: 51, question_text: "Select all images with cavities", order: 2 },
      ...
    ]
  }
  */

  setSessionId(data.session_id);
  setImages(data.images);
  setQuestions(data.questions);
  setCurrentQuestionIndex(0);
};
```

---

### **2. Display Images with Selection**

```typescript
interface SessionState {
  sessionId: number;
  images: Array<{id: number, filename: string, image_url: string, order: number}>;
  questions: Array<{id: number, question_text: string, order: number}>;
  currentQuestionIndex: number;
  selectedImageIds: number[];  // Track which images user selected
}

const ImageGrid = ({ images, selectedImageIds, onToggleImage }) => {
  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
      {images.map((image) => (
        <div
          key={image.id}
          className={`cursor-pointer border-4 ${
            selectedImageIds.includes(image.id)
              ? 'border-blue-500'
              : 'border-gray-300'
          }`}
          onClick={() => onToggleImage(image.id)}
        >
          <img
            src={image.image_url}
            alt={image.filename}
            className="w-full h-auto"
          />
          <div className="text-center p-2">
            {selectedImageIds.includes(image.id) && <span>✓ Selected</span>}
          </div>
        </div>
      ))}
    </div>
  );
};
```

---

### **3. Handle Image Selection**

```typescript
const [selectedImageIds, setSelectedImageIds] = useState<number[]>([]);

const toggleImageSelection = (imageId: number) => {
  setSelectedImageIds((prev) => {
    if (prev.includes(imageId)) {
      // Deselect
      return prev.filter(id => id !== imageId);
    } else {
      // Select
      return [...prev, imageId];
    }
  });
};
```

---

### **4. Submit Answer**

```typescript
const submitAnswer = async () => {
  const currentQuestion = questions[currentQuestionIndex];
  const startTime = Date.now(); // Track when user started

  const response = await fetch('http://localhost:8000/auth/annotations', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      session_id: sessionId,
      question_id: currentQuestion.id,
      selected_image_ids: selectedImageIds,  // [1, 3] - images user clicked
      time_spent: (Date.now() - startTime) / 1000  // seconds
    })
  });

  const data = await response.json();
  /*
  {
    id: 1,
    session_id: 1,
    question_id: 50,
    selected_image_ids: [1, 3],
    is_correct: null,
    time_spent: 8.5,
    created_at: "2025-11-08T..."
  }
  */

  // Move to next question
  setSelectedImageIds([]);  // Clear selection
  setCurrentQuestionIndex(prev => prev + 1);

  // If all questions answered, show completion screen
  if (currentQuestionIndex === questions.length - 1) {
    showCompletionScreen();
  }
};
```

---

### **5. Complete React Component**

```typescript
const AnnotationSession = () => {
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [images, setImages] = useState([]);
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedImageIds, setSelectedImageIds] = useState<number[]>([]);
  const [startTime, setStartTime] = useState(Date.now());

  useEffect(() => {
    loadSession();
  }, []);

  const loadSession = async () => {
    const response = await fetch('/auth/sessions/next?num_images=4&num_questions=5', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    setSessionId(data.session_id);
    setImages(data.images);
    setQuestions(data.questions);
  };

  const toggleImage = (imageId: number) => {
    setSelectedImageIds(prev =>
      prev.includes(imageId)
        ? prev.filter(id => id !== imageId)
        : [...prev, imageId]
    );
  };

  const submitAnswer = async () => {
    const timeSpent = (Date.now() - startTime) / 1000;

    await fetch('/auth/annotations', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        session_id: sessionId,
        question_id: questions[currentQuestionIndex].id,
        selected_image_ids: selectedImageIds,
        time_spent: timeSpent
      })
    });

    // Move to next question
    setSelectedImageIds([]);
    setStartTime(Date.now());
    setCurrentQuestionIndex(prev => prev + 1);
  };

  if (!questions.length) return <div>Loading...</div>;

  const currentQuestion = questions[currentQuestionIndex];
  const isLastQuestion = currentQuestionIndex === questions.length - 1;

  return (
    <div className="container mx-auto p-4">
      <div className="mb-4">
        <h2 className="text-xl font-bold">
          Question {currentQuestionIndex + 1} of {questions.length}
        </h2>
        <p className="text-lg mt-2">{currentQuestion.question_text}</p>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4 mb-6">
        {images.map((image) => (
          <div
            key={image.id}
            className={`cursor-pointer border-4 rounded-lg overflow-hidden ${
              selectedImageIds.includes(image.id)
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onClick={() => toggleImage(image.id)}
          >
            <img
              src={image.image_url}
              alt={image.filename}
              className="w-full h-48 object-cover"
            />
            <div className="p-2 text-center">
              {selectedImageIds.includes(image.id) && (
                <span className="text-blue-600 font-bold">✓ Selected</span>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="flex gap-4">
        <button
          onClick={submitAnswer}
          disabled={selectedImageIds.length === 0}
          className="bg-blue-500 text-white px-6 py-2 rounded disabled:bg-gray-300"
        >
          {isLastQuestion ? 'Finish Session' : 'Next Question →'}
        </button>

        <button
          onClick={() => submitAnswer()}  // Submit with empty array
          className="bg-gray-300 px-6 py-2 rounded"
        >
          Skip Question
        </button>
      </div>

      <div className="mt-4 text-sm text-gray-600">
        Selected: {selectedImageIds.length} image(s)
      </div>
    </div>
  );
};
```

---

## 🎯 Key Points for Frontend

1. **Multiple Selection**: Users can select 0, 1, or multiple images
2. **Visual Feedback**: Show clear indication of selected images (border, checkmark, etc.)
3. **Time Tracking**: Track how long user spends on each question
4. **Progress Indicator**: Show "Question X of Y"
5. **Validation**: Disable submit if no images selected (or allow skip)
6. **Session Management**: One session = all questions shown at once or one at a time

---

## 📝 Data Flow Summary

```
1. Frontend calls GET /sessions/next
   ↓
2. Backend creates session + assigns 4 images + 5 questions
   ↓
3. Frontend displays Question 1 with 4 images
   ↓
4. User clicks images #2 and #4
   ↓
5. Frontend calls POST /annotations with selected_image_ids: [2, 4]
   ↓
6. Backend stores annotation + annotation_images records
   ↓
7. Frontend shows Question 2 with same 4 images
   ↓
8. Repeat until all questions answered
```

---

## 🎨 UI/UX Recommendations

### **Image Display:**
- Use responsive grid (2 cols mobile, 4 cols desktop)
- Large clickable areas
- Clear selected/unselected states
- Image preview on hover

### **Question Display:**
- Large, readable font
- Progress bar or counter
- Question type badge (optional)

### **Controls:**
- Primary button: "Submit Answer" or "Next Question"
- Secondary button: "Skip" (submits empty selection)
- Clear selection button (optional)

### **Feedback:**
- Show how many images selected
- Disable submit if none selected
- Loading state while submitting
- Success animation on submit

---

## 🚀 Next Steps for Frontend Dev

1. Create session state management (React Context or Redux)
2. Build ImageGrid component with selection
3. Build QuestionDisplay component
4. Add submit logic with API calls
5. Add progress tracking
6. Add session completion screen
7. Add error handling for API failures

The backend is ready! You can start building the frontend now! 🎉
