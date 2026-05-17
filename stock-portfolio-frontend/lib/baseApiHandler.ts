export async function getJsonHandler(fullUrl: string, cookie = "") {
  return await fetch(fullUrl, {
    headers: {
      Cookie: cookie,
    },
  }).then(async (r) => [r.status, await r.json()]);
}

async function sendJson(
  fullUrl: string,
  method: "PUT" | "POST",
  json: JSON,
  cookie = "",
) {
  return await fetch(fullUrl, {
    method: method,
    body: JSON.stringify(json),
    headers: {
      "Content-Type": "application/json",
      Cookie: cookie,
    },
  }).then(async (r) => [r.status, await r.json()]);
}

export async function postJsonHandler(
  fullUrl: string,
  json: JSON,
  cookie = "",
) {
  return await sendJson(fullUrl, "POST", json, cookie);
}

export async function putJsonHandler(fullUrl: string, json: JSON, cookie = "") {
  return await sendJson(fullUrl, "PUT", json, cookie);
}

export async function deleteJsonHandler(fullUrl: string, cookie = "") {
  return await fetch(fullUrl, {
    method: "DELETE",
    headers: {
      Cookie: cookie,
    },
  }).then(async (r) => [r.status, await r.json()]);
}
