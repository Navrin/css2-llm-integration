def get_tools_with_schema(schema: str):
    return [
        {
            "type": "function",
            "function": {
                "name": "query_database",
                "description": "Receives an SQL query about sales, products, modifiers, stores, and returns the result.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": f"""
                                SQL query extracting info to answer the user's question.
                                SQL should be written using this database schema:
                                {schema}
                                The query should be returned in plain text, not in JSON."""},
                    }
                },
                "required": ["query"]
            }
        }
    ]