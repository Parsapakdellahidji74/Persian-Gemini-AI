const chromadb = require('chromadb'); 
const { embed_fn } = require('../utils/embedding');

const chromaClient = new chromadb.Client();
const DB_NAME = 'googlecar_collection';

const db = chromaClient.getOrCreateCollection({
  name: DB_NAME,
  embeddingFunction: embed_fn,
});

module.exports = db;
