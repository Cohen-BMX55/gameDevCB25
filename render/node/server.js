import express from 'express';
import cors from 'cors';

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 3000;

// Classic Magic 8-Ball responses
const answers = [
  "It is certain.",
  "Without a doubt.",
  "You may rely on it.",
  "Yes, definitely.",
  "Most likely.",
  "Ask again later.",
  "Cannot predict now.",
  "Don’t count on it.",
  "My sources say no.",
  "Very doubtful."
];

// API endpoint to answer questions
app.post("/api/ask", (req, res) => {
  const { question } = req.body;

  if (!question || question.trim() === "") {
    return res.status(400).json({ error: "Please ask a question!" });
  }

  const randomAnswer = answers[Math.floor(Math.random() * answers.length)];
  res.json({ question, answer: randomAnswer });
});

// Serve frontend
app.use(express.static("public"));

app.listen(PORT, () => {
  console.log(`Magic 8-Ball server running on port ${PORT}`);
});

