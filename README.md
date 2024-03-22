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
  - First/Last Name
  - Postcode
  - Email
  - Phone number
  - Temporary profile
- Sales
  - SaleItem
    - Product ID
    - Modifier ID (multiple)
    - Quantity
  - Sale
    - SaleItem (multiple)
    - Customer ID
- Products
  - Name
  - Description
  - Price
  - Applicable modifiers (multiple IDs)
- Modifiers
  - Name
  - Price
- Stores
  - Name
  - Location

## Example Database Items

### Products

| Name          | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Price | Modifiers                |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----- | ------------------------ |
| Arctic Freeze | Indulge in the refreshing taste of our Arctic Freeze Blueberry Shake. Made with plump, juicy blueberries and creamy vanilla ice cream, this frosty treat is sure to take your taste buds on a journey to the arctic. Perfect for hot summer days or as a sweet indulgence any time of year, our Arctic Freeze Blueberry Shake is a must-try for any blueberry lover. So go ahead, sip and savor the cool, fruity goodness of our Arctic Freeze Blueberry Shake today! | 9.99  | [Dairy Free], [Less Ice] |
