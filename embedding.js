const embed_fn = {
    document_mode: true,
    embed: async (texts) => {
      return [/* array of embeddings */];
    },
  };
  
  const client = {
    models: {
      generate_content: async ({ model, contents }) => {
        return {
          text: "Sample response from gemini",
        };
      },
    },
  };
  
  module.exports = { embed_fn, client };
  