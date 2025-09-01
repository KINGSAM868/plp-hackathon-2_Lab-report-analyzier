// server/routes/submissions.js
const express = require('express');
const pool = require('../config/db');
const { authenticateToken } = require('../middleware/auth');
const axios = require('axios');

const router = express.Router();

// Student submits report
router.post('/', authenticateToken, async (req, res) => {
  if (req.user.role !== 'student') return res.sendStatus(403);

  const { template_id, submission_values } = req.body;
  const [result] = await pool.query(
    "INSERT INTO submissions (student_id, template_id, submission_values) VALUES (?, ?, ?)",
    [req.user.id, template_id, JSON.stringify(submission_values)]
  );

  // Call Python AI service
  try {
    const aiResponse = await axios.post('http://localhost:5000/grade', {
      submission_id: result.insertId,
      submission_values
    });
    res.json({ success: true, submissionId: result.insertId, ai: aiResponse.data });
  } catch (err) {
    res.status(500).json({ error: "AI Service error", details: err.message });
  }
});

// Get submissions for a student
router.get('/my', authenticateToken, async (req, res) => {
  const [rows] = await pool.query("SELECT * FROM submissions WHERE student_id = ?", [req.user.id]);
  res.json(rows);
});

module.exports = router;