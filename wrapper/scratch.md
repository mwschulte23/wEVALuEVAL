#### Deconstructing the Prompt
1. Get the user's sentiments from the database
2. Get the user's suggestions from the database
3. Build off of the user's suggestions to provide new suggestions
4. See if the user has feedback or has completed the suggestions
5. Provide the prompt

Sentiment:

Past Input / Output (e.g memory):

User Query -> todays Input
Past I/O -> past Input(s)


const { data: sentiments, error: sentimentsError } = await supabase
      .from("users_sentiment")
      .select("*")
      .eq("user_id", userId);

    // TODO: get old suggestions, build off of them, do not repeat, see if the user has feedback or has completed them.
    const { data: suggestions, error: suggestionsError } = await supabase
      .from("suggestions")
      .select("*")
      .eq("user_id", userId);

    const allSentiments = `Today's input: ${todayInputs} \n Context about the user: ${
      sentiments?.[0]?.about ?? "Unknown context about the user"
    } \n Past inputs: ${pastInputs}`;

    if (sentimentsError) {
      throw new Error(`Error fetching sentiments: ${sentimentsError.message}`);
    }

    const prompt = `
      For '${userId}', can you provide the following details in JSON format:
      {
        "wellbeing": "[0-100] - This is the average wellbeing score from the users sentiments from the input below and context of the user",
        "connectedness": "[0-100] - This is the average connectedness score from the users sentiments from the input below and context of the user",
        "happiness": "[0-100] - This is the average happiness score from the users sentiments from the input below and context of the user",
        "ai_analysis": "Your response.",
        "suggestions_for_user": "[suggestion1, suggestion2, suggestion3] - provide very specific and actionable suggestions for how to make meaningful improvements based on the users context and inputs and feedback of previous suggestions.",
        "suggestions_for_manager": "[suggestion1, suggestion2, suggestion3] - Avoid mentioning any explicit negative actions or severe dissatisfaction. Do not use name. Be relatively vague to protect the user.",
        "score": "[0-100] - This is the score average sentiment from wellbeing, happiness, connectedness scores calculated from the input below"
      }

      Context:
      ${allSentiments}

      Do not provide any extraneous information other than the JSON.