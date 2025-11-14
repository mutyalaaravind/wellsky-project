Transcript Extraction:
Input:
⁃ transcript text
⁃ questionnaire - need not be FHIR but we can model generically like the FHIR questionnaire
Output
⁃ questionnaire response
⁃ Each answer should include evidence citation and meta info of source of the evidence. Ex: transcript ID
Design questions:
⁃ What if text is very large?
⁃ Should have a way to organize prompts like - AppID, use case ID. Anything else?
⁃ Prompt multiple or single question per LLM call
⁃ Support possibility of a prompt chain   To get a single answer. Ex: extract text followed by confession of unit out scoring etc. or 2nd prompt to cross check or validate the answer further after extraction in step 1
⁃ Audit log every prompt and answer
⁃ Hard errors check before returning response when prompt doesn’t return expected answer for required fields etc.
⁃ Asynchronous job to review more responsible AI checks
⁃ Can the framework add prompt for chain of thought, verbatim source etc. or need caller to do it?
⁃ What if verbatim source is not in extracted answer?
⁃ Unit test validation in CICD
Milestones:
⁃ identify each unique prompt scenarios from oasis and complete first
⁃ All oasis sections




Document Extraction:
Additional design questions:
⁃ can we validate against ocr data?
⁃ Capture the coordinates
⁃ We should let higher level abstraction component handle optimization of which docs/pages to search for answer as use case specific context can easily define optimization approach but not genetically



Overarching design questions:
The reason for two separate services is because the evidence logic is quite different and the validations could also be very different

we need to support every prompt, llm settings to be used (e.g: different prompts with different models)


AI gaurdrails:
https://github.com/piratos/llmfilters
Guardrails.ai 
NeMo Guardrails

Some Orchestrator Application framework for AI development:

Bubble.AI: Bubble is a widely recognized no-code platform known for enabling individuals to create scalable and responsive web-based applications without the need for coding. Their platform offers a web-based design studio, simplifying the creation of UI/UX components for the app that seamlessly integrate with almost any data sources through the API connector pattern. Also the Bubble platform facilitates hosting web and mobile applications, ensuring scalability to  accommodate increased traffic. An additional feature of Bubble is its API connector, which seamlessly integrates with OpenAI's platform and popular models like GPT-3.5, GPT-4, and DALL-E.


Langchain : The Langchain framework is a revolutionary open source project in the Generative AI space, specifically tailored to utilize the power of large language models and the data flow. At its core, Langchain acts as a structured framework to facilitate the development, deployment, and orchestration of language-driven AI products. This innovative framework aids the engineering team to tailor practical enterprise grade AI solutions based on the foundation model, enabling businesses to leverage advanced AI capabilities while bridging the gap between technology and end users. Langchain is a modularize framework and supports the following modules:


 Model I/O:   LangChain provides the capability to interface with any language model. This module provides support with a powerful Prompt Template to handle dynamic prompt engineering, option for long running chat interaction or regular textual tasks using LLM as well as output management through different parsers.


 Data Connection: LangChain has the capability to connect to almost any type of Vector databases, equipped with a scalable document loader from any input sources including the document chunking feature.

 Chains: One of the powerful modules of LangChain is the Chains module which allows the developer to combine multiple components together for a single and coherent experience to the end users.

 Agents: The agents module is an extremely powerful module which makes the underlying LLM model as a thinking machine and helps the developer to build a flexible AI application having the reasoning capability to think and decide which action to take and in which order.

 Memory: We all know LLMs or FMs are stateless and thus require the external framework to integrate memory if there is a requirement to preserve the interaction.

 Callback: The framework allows integrating external callback capability which helps integrating logging or tracing during various stages of the application flow.

LlamaIndex : This another popular framework based on Python and getting full support from the open source community. The framework comes with built in out of the box  features such as


 Ingest from almost any kind of data sources and data formats using Data connectors (Llama Hub). They even have data connectors to crawl Wikipedia, Discord channels etc. No need to reinvent the wheel.

 Smooth data indexing support so that LLMs can consume data easily.

 Support synthesis over heterogeneous data and multiple documents.

 The “Router” component allows it to connect with different flows.

 Allow for the hypothetical document embeddings to enhance output quality.

 It supports almost any Vector database to connect for RAG pattern.

 The best thing is it now supports the brand new OpenAI function calling.

 LLMIndex supports GuardRail markup language to add an extra layer of moderation in the output from Vector DB or LLMs.

FlowiseAI : This is an open source tool which supports no code approach to quickly develop a production grade LLM application as well as prototype for experimenting. This product comes with drag and draw visual tools to build customized LLM flow. Flowise also supports integrating custom prompt templates as well some pre-built flows namely QnA chain, Language translation chain and conversational agent with memory. One of the major features is that this tool is totally free for commercial usage.