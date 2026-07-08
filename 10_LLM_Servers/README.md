<p align = "center" draggable="false" ><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
     width="200px"
     height="auto"/>
</p>

## <h1 align="center" id="heading">Session 10: LLM Servers</h1>

| 📰 Session Sheet                                  | ⏺️ Recording                           | 🖼️ Slides                                   | 👨‍💻 Repo       | 📝 Homework                                              | 📁 Feedback                        |
| ------------------------------------------------- | -------------------------------------- | ------------------------------------------- | ------------- | -------------------------------------------------------- | ---------------------------------- |
| [Session 10: LLM Servers](https://github.com/AI-Maker-Space/The-AI-Engineering-Certification-v1.0/tree/main/00_Docs/Modules/10_LLM_Servers) |[Recording!](https://us02web.zoom.us/rec/share/zXd6__uO2RwCmJUmNyGKY01sbwYjjrkpDDNPbfK_Es0MANaqRpFOqqYX4sEVYY1d.gJwTZk1729siXnjj) <br> passcode: `^1$@$R@.`| [Session 10 Slides](https://canva.link/953giejzt5igxvw) |You are here! | [Session 10 Assignment](https://forms.gle/hKxFnEM8U16fCCnG8) | [Feedback 7/2](https://forms.gle/uj2QvYjHfHKFFQ8a6) |

**⚠️!!! PLEASE BE SURE TO SHUTDOWN YOUR DEDICATED ENDPOINT ON FIREWORKS AI WHEN YOU'RE FINISHED YOUR ASSIGNMENT !!!⚠️**

# Build 🏗️

In today's assignment, we'll be creating Fireworks AI endpoints, and then building a RAG application.

- 🤝 Breakout Room #1
  - Set-up Open Source Endpoint (Instructions [here](./ENDPOINT_SETUP.md)) ((This process may take 15-20min.))
  - Test Endpoint and Embeddings with the `endpoint_slammer.ipynb` notebook.

- 🤝 Breakout Room #2
  - Use the Open Source Endpoints to build a RAG LangGraph application

# Ship 🚢

The completed notebook and your RAG app/notebook!

### Deliverables

- A short Loom of either:
  - the notebook and the RAG application you built for the Main Homework Assignment; or
  - the notebook you created for the Advanced Build

# Share 🚀

Make a social media post about your final application!

### Deliverables

- Make a post on any social media platform about what you built!

Here's a template to get you started:

```
🚀 Exciting News! 🚀

I am thrilled to announce that I have just built and shipped a RAG application powered by open-source endpoints! 🎉🤖

🔍 Three Key Takeaways:
1️⃣
2️⃣
3️⃣

Let's continue pushing the boundaries of what's possible in the world of AI and question-answering. Here's to many more innovations! 🚀
Shout out to @AIMakerspace !

#LangChain #QuestionAnswering #RetrievalAugmented #Innovation #AI #TechMilestone

Feel free to reach out if you're curious or would like to collaborate on similar projects! 🤝🔥
```

# Submitting You Homework

## Main Homework Assignment

Follow these steps to prepare and submit your homework assignment:

1. Follow the instructions in `ENDPOINT_SETUP.md`
2. Replace both `model` values in `endpoint_slammer.ipynb` with the `gpt-oss` endpoint you created in Step 1
3. Run the code cells in `endpoint_slammer.ipynb`
4. Respond to the questions in the section below
5. Build a sample RAG
6. Record a Loom video reviewing what you have learned from this session

**⚠️!!! PLEASE BE SURE TO SHUTDOWN YOUR DEDICATED ENDPOINT ON FIREWORKS AI WHEN YOU HAVE FINISHED YOUR ASSIGNMENT !!!⚠️**

## Questions

### ❓ Question #1:

What is the difference between serverless and dedicated endpoints?

#### ✅ Answer:

Serverless endpoints are shared infrastructure that Fireworks already runs. You call the model by its identifier and pay per token, nothing when idle. You never manage or provision GPUs. The tradeoff is that you share capacity with everyone else hitting the same pool, so under heavy or bursty load you can hit queueing, rate limits, or cold responses.
Dedicated endpoints are GPUs provisioned for you alone. You get guaranteed capacity and consistent latency because no one else is competing for the hardware. The tradeoff is cost: you pay by the hour whether or not the endpoint is being used, which is why Fireworks warns you to configure auto-shutdown or delete the deployment when done.
For this assignment I used serverless, which is the correct instinct for a low-traffic homework workload. A production system with steady load and strict latency requirements, especially in a regulated setting, is where dedicated earns its cost.

### ❓ Question #2:

Why is it important to consider token throughput and latency when choosing an LLM for user-facing applications?

#### ✅ Answer:

Latency is how long a single request takes, which is what one user feels while waiting for a reply. Throughput is how many requests or tokens the system handles per second across all users, which is what determines whether the app survives under concurrent load. They're different numbers and you need both.
I saw this directly. A single request returned quickly, but firing 24 concurrent requests at the serverless endpoint took 29.89 seconds for all 24 to complete, with zero failures. That tells me the endpoint handled the burst without dropping requests, but the per-request time under concurrency was higher than a single isolated call, because shared serverless capacity queues work under load.
For a user-facing app this matters because good latency for one user doesn't guarantee the app holds up when many users arrive at once. If throughput is weak, real users experience slow or timed-out responses at peak. The only honest way to know your ceiling is to measure it on a realistic load, which is exactly what the slam test does, rather than guessing from a single request.

## Activity 1: RAGAS Evaluation with Cost Analysis

Use RAGAS to evaluate your open-source Fireworks AI powered RAG app against an OpenAI `gpt-4.1-mini` powered equivalent. Compare retrieval quality, answer faithfulness, and end-to-end accuracy across both providers.

Additionally, instrument both pipelines with **LangSmith** to capture token usage and cost per query. Use LangSmith's tracing and cost dashboards to compare the total cost of running each provider at scale. Include your evaluation results, cost breakdown, and analysis in your Loom video.

## Notes
I compared an open RAG (Fireworks gpt-oss-20b with Qwen3-Embedding-8B) against a closed RAG (OpenAI gpt-4.1-mini with text-embedding-3-small) over the same cat health guide, using six fixed questions and gpt-4.1-mini as the RAGAS judge.
Quality scores:

Faithfulness: Fireworks 0.79, OpenAI 0.83
Answer relevancy: Fireworks 0.75, OpenAI 0.76
Context precision: Fireworks 0.72, OpenAI 0.76
Context recall: Fireworks 0.83, OpenAI 0.83

Cost per query, from captured token usage at published rates:

Fireworks: $0.00026
OpenAI: $0.00121
Fireworks is 4.7x cheaper. At 1M queries that is $259 vs $1,211.

What I found:

OpenAI is a little better across the board, but the gap is small. The open model is competitive, not far behind. Context recall was identical because both retrieved over the same chunks.
The cost gap comes from input tokens, not output. gpt-oss-20b was about 6x more verbose on output, but both pipelines send similar input volume, and Fireworks charges 5.7x less per input token. For RAG this makes sense: every query loads retrieved context into the prompt, so input is the big, constant cost. Output verbosity barely moved the total.
On a question the guide does not answer (a declawing anesthesia protocol), both models correctly said "I don't know." The open model held the line on this run. One run is not proof of reliability though. Running that question 20 times and measuring the refusal rate would be the real test.

## Advanced Activity: Local Models

Swap out the Fireworks AI endpoints for **locally-running open-source models** using [Ollama](https://ollama.com/) or another local inference server of your choice. Run both your embedding model and your chat model locally, and rebuild the RAG pipeline on top of them.

- Compare quality and latency between the local setup and your Fireworks AI hosted endpoint.
- Reflect: what are the trade-offs of local models vs. managed endpoints in a production setting?

Include your findings and a demo in your Loom video.
