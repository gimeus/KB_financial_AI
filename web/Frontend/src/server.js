const express = require('express');
const mysql = require('mysql');
const app = express();
const port = 3001;

app.use(express.json());

const db = mysql.createConnection({
  host: 'localhost',
  user: 'yourusername',
  password: 'yourpassword',
  database: 'yourdatabase',
});

db.connect((err) => {
  if (err) {
    throw err;
  }
  console.log('MySQL connected...');
});

app.get('/api/data', (req, res) => {
  let sql = 'SELECT * FROM your_table';
  db.query(sql, (err, results) => {
    if (err) {
      res.status(500).send(err);
    } else {
      res.json(results);
    }
  });
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
