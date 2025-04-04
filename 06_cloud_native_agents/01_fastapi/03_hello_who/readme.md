# Different ways to pass new parameter

[Read Pages 33-41, 43-46 FastAPI Textbook](https://www.amazon.com/FastAPI-Bill-Lubanovic-ebook/dp/B0CLKZJSGV/ref=sr_1_1)

Let’s make our earlier application a little more personal by adding a parameter called who that addresses that plaintive Hello? to someone. We’ll try different ways to pass
this new parameter:

* In the URL path

* As a query parameter, after the ? in the URL

* In the HTTP body

* As an HTTP header

### Which Method Is Best?

Here are a few recommendations:

* When passing arguments in the URL, following RESTful guidelines is standard
practice.

* Query strings are usually used to provide optional arguments, like pagination.

* The body is usually used for larger inputs, like whole or partial models.

In each case, if you provide type hints in your data definitions, your arguments will be automatically type-checked by Pydantic. This ensures that they’re both present and correct.

### HTTP Responses

By default, FastAPI converts whatever you return from your endpoint function to JSON; the HTTP response has a header line Content-type: application/json. So, although the greet() function initially returns the string "Hello? World?", FastAPI
converts it to JSON. This is one of the defaults chosen by FastAPI to streamline APIdevelopment.

In this case, the Python string "Hello? World?" is converted to its equivalent JSON string "Hello? World?", which is the same darn string. But anything that you return
is converted to JSON, whether built-in Python types or Pydantic models.