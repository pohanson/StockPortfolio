import { getJsonHandler, postJsonHandler } from "../../../lib/baseApiHandler";

export default async function handler(req, res) {
  console.log(req.method, `/api/transaction`);
  let statusCode, json;
  if (req.method == "GET") {
    [statusCode, json] = await getJsonHandler(
      process.env.API_URL + `/transaction`,
      req.headers.cookie || "",
    );
  } else if (req.method == "POST") {
    [statusCode, json] = await postJsonHandler(
      process.env.API_URL + `/transaction`,
      req.body,
      req.headers.cookie || "",
    );
  } else {
    res.status(405).json({ error: `Invalid method ${req.method}` });
  }
  res.status(statusCode).json(json);
}
