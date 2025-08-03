// app.js
const express = require('express');
const rateLimit = require('express-rate-limit');
const morgan = require('morgan');
const fs = require('fs');
const path = require('path');
const askRoute = require('./routes/ask');
const logger = require('./utils/logger');
const setupSwagger = require('./utils/swagger');


const app = express();
const port = 3000;

app.use(express.json());

// Logging to file
app.use(morgan('combined', { stream: fs.createWriteStream(path.join(__dirname, 'logs/app.log'), { flags: 'a' }) }));

// Logging to console
app.use(morgan('dev'));

// Swagger docs
setupSwagger(app)

// Rate limiter
const limiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 10, // limit each IP to 10 requests per windowMs
  message: 'too many requests, please try again later.',
});
app.use('/ask', limiter);

// Routes
app.use('/ask', askRoute);

// Error handling
app.use((err, req, res, next) => {
  logger.error(err.stack || err.message);
  
  if (err.name === 'ValidationError') {
    return res.status(400).json({ detail: err.message });
  }
  
  res.status(500).json({ detail: 'A server error has occurred' });
});

app.listen(port, () => {
  console.log(`🚀 Server running at http://localhost:${port}`);
});


