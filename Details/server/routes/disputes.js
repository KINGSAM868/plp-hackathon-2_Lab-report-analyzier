// server/routes/disputes.js
const express = require('express');
const pool = require('../config/db');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

// Student opens dispute
router.post('/', authenticateToken, async (req, res) => {
  if (req.user.role !== 'student') return res.sendStatus(403);

  const { submission_id, lecturer_id, reason } = req.body;
  const [result] = await pool.query(
    "INSERT INTO disputes (submission_id, student_id, lecturer_id, reason) VALUES (?, ?, ?, ?)",
    [submission_id, req.user.id, lecturer_id, reason]
  );
  res.json({ success: true, disputeId: result.insertId });
});

// Lecturer resolves dispute
router.put('/:id', authenticateToken, async (req, res) => {
  if (req.user.role !== 'lecturer') return res.sendStatus(403);

  const { resolution, status } = req.body;
  await pool.query(
    "UPDATE disputes SET resolution=?, status=? WHERE id=? AND lecturer_id=?",
    [resolution, status, req.params.id, req.user.id]
  );
  res.json({ success: true });
});

module.exports = router;