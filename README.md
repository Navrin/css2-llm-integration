## Overview

This demo will consist of 3 components:

### Front-end

- Simple web front-end that provides a chatbot interface.
- Some way of inserting reviews into the system.

### API

- Facilitates the data connection between the LLM and the database.
- Will have an endpoint for query and response, and an endpoint for adding a review.

### LLM interface

- Create platform-agnostic adapter protocol that can handle connections/API queries to various LLM providers.
- Provide adapters for local LLM models, OpenAI GPT API, any other relevant LLM we have access to.

## Database

The aim for this demo integration is for a hypothetical end-to-end transactional company. We will be approaching from the perspective of a fruit tea/smoothie company looking to query their sales information through their online platform.
Therefore, we will generate dummy data that should resemble the typical information an end-to-end provider will host.

- Customer/loyalty
- Sales
- Products
- Modifiers
- Stores
