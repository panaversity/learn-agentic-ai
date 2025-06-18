# ✅ What is `curl`?

* `curl` is a command-line tool that lets you send **HTTP requests** and see the **responses**.
* Works on Linux, macOS, and Windows (with Git Bash or WSL).

---

## Let's pretend we’re interacting with a simple test server:

We'll use [https://reqres.in](https://reqres.in), a **fake REST API** made for testing HTTP requests.

---

## 1️⃣ **GET** – Retrieve data

Get the list of users:

```bash
curl https://reqres.in/api/users?page=2
```

➡️ You’ll get a response like:

```json
{
  "page": 2,
  "data": [
    {
      "id": 7,
      "email": "michael.lawson@reqres.in",
      ...
    }
  ]
}
```

✅ This is just like opening a webpage and reading its content.

---

## 2️⃣ **POST** – Send data (e.g., signup)

Create a new user:

```bash
curl -X POST https://reqres.in/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Wania", "job": "Developer"}'
```

➡️ You’ll get a response like:

```json
{
  "name": "Wania",
  "job": "Developer",
  "id": "245",
  "createdAt": "2025-06-17T22:00:00.000Z"
}
```

✅ This simulates submitting a form to create a new account.

---

## 3️⃣ **PUT** – Update (replace) data

Update the user completely:

```bash
curl -X PUT https://reqres.in/api/users/2 \
  -H "Content-Type: application/json" \
  -d '{"name": "Wania", "job": "Senior Dev"}'
```

➡️ Response:

```json
{
  "name": "Wania",
  "job": "Senior Dev",
  "updatedAt": "2025-06-17T22:05:00.000Z"
}
```

✅ This replaces the old job with "Senior Dev".

---

## 4️⃣ **PATCH** – Partially update data

Update only one field (e.g., just the job):

```bash
curl -X PATCH https://reqres.in/api/users/2 \
  -H "Content-Type: application/json" \
  -d '{"job": "Engineer"}'
```

➡️ Response:

```json
{
  "job": "Engineer",
  "updatedAt": "2025-06-17T22:10:00.000Z"
}
```

✅ This changes only the job, not the name.

---

## 5️⃣ **DELETE** – Remove a resource

Delete a user:

```bash
curl -X DELETE https://reqres.in/api/users/2
```

➡️ Response: *(no body, just status `204 No Content`)*

✅ This tells the client that the user was deleted successfully.

---

## 6️⃣ **HEAD** – Get only headers (no content)

```bash
curl -I https://reqres.in/api/users/2
```

➡️ You get:

```
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 123
...
```

✅ Used when you want to check metadata without downloading the whole page/data.

---

## 7️⃣ **OPTIONS** – Ask what methods are allowed

```bash
curl -X OPTIONS https://reqres.in/api/users/2 -i
```

➡️ You’ll get:

```
Allow: GET, POST, PUT, PATCH, DELETE, OPTIONS
```

✅ This tells the browser or client what’s allowed on this endpoint.

---

## 📝 Summary Table

| Method  | curl Command             |
| ------- | ------------------------ |
| GET     | `curl URL`               |
| POST    | `curl -X POST -d ...`    |
| PUT     | `curl -X PUT -d ...`     |
| PATCH   | `curl -X PATCH -d ...`   |
| DELETE  | `curl -X DELETE URL`     |
| HEAD    | `curl -I URL`            |
| OPTIONS | `curl -X OPTIONS -i URL` |

