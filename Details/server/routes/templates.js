// server/routes/templates.js
const express = require('express');
const pool = require('../config/db');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

// Lecturer creates template
router.post('/', authenticateToken, async (req, res) => {
  if (req.user.role !== 'lecturer') return res.sendStatus(403);

  const { title, description, fields } = req.body;
  const [result] = await pool.query(
    "INSERT INTO lab_templates (lecturer_id, title, description, fields) VALUES (?, ?, ?, ?)",
    [req.user.id, title, description, JSON.stringify(fields)]
  );
  res.json({ success: true, templateId: result.insertId });
});

// Get all templates
router.get('/', async (req, res) => {
  const [rows] = await pool.query("SELECT * FROM lab_templates");
  res.json(rows);
});

module.exports = router;