
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

## How to run it.
### Docker (recommended)
You can run this demo via docker. Docker is a containerisation service that will make it easier to run the demo.

The instructions here assume some knowledge of using the terminal. If you are on linux or mac, then the default terminals will suffice. If you are on windows, __use powershell__, and these commands should hopefully work. **Do not use cmd, it will not work**. 
1. [Install docker.](https://docs.docker.com/engine/install/)
2. clone the repo `git clone https://github.com/Navrin/css2-llm-integration.git` (if you do not have git you can install it [here](https://git-scm.com/downloads) or you can manually download the zip file from the github site and extract it, however, this is not recommended as you will not be able to contribute to the project code.)
3. cd in `cd css2-llm-integration`
4. __set up your .env file__: `touch .env-docker` and then edit it with whatever program
5. run docker via `docker compose --env-file=.env-docker up`

If you make modifications to the code, you can rebuild the images using `docker compose --env-file=.env-docker build`. If you need to clear data, try `docker compose --env-file=.env-docker down` or `docker compose --env-file=.env-docker rm chat db` and then `docker compose --env-file=.env-docker up`.
When running `docker compose --env-file=.env-docker up` you should have a URL that will let you run the app in the browser. 

### Setting up your .env
In the project root folder, you will need a `.env`. Here is an example base template. You will need to substitute in variables such as the API token.

~~__If you are using docker, name your file `.env-docker`__. The docker compose file mount `.env-docker` as `.env`. This is because the `.env` files will differ slightly if you are hosting the bot directly (i.e local postgres). The example template will work for the docker version.~~
`.env-docker` is no longer needed! Just make sure you set up your regular `.env` properly.
```
OPENAI_KEY=<OPENAI KEY>
OR_KEY=<OPENROUTER KEY>
DB_NAME=css2_llm
DB_HOST="${DB_HOST:-0.0.0.0}"
DB_PASSWORD=password
DB_USER=postgres
PROJECT_ROOT=<PROJECT ROOT HERE (use pwd in the root directory)>
DB_DATA_FOLDER="${PROJECT_ROOT}/example_data"

POSTGRES_USER=${DB_USER}
POSTGRES_PASSWORD=${DB_PASSWORD}
POSTGRES_DB=${DB_NAME}
```
## Example Database Items

### Products

| Name          | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Price | Modifiers                |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----- | ------------------------ |
| Arctic Freeze | Indulge in the refreshing taste of our Arctic Freeze Blueberry Shake. Made with plump, juicy blueberries and creamy vanilla ice cream, this frosty treat is sure to take your taste buds on a journey to the arctic. Perfect for hot summer days or as a sweet indulgence any time of year, our Arctic Freeze Blueberry Shake is a must-try for any blueberry lover. So go ahead, sip and savor the cool, fruity goodness of our Arctic Freeze Blueberry Shake today! | 9.99  | [Dairy Free], [Less Ice] |


