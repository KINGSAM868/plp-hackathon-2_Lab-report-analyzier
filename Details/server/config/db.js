// server/config/db.js
const mysql = require('mysql2/promise');

const pool = mysql.createPool({
  host: 'localhost',
  user: 'root',        // MySQL username
  password: 'Saidi_868',// MySQL password
  database: 'lab_reports_db'
});

module.exports = pool;