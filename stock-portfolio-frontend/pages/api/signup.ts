import { postJsonHandler, putJsonHandler } from "../../lib/baseApiHandler";

export default async function handler(req, res) {
  console.log(req.method, "/api/signup");
  let [statusCode, json] = await postJsonHandler(
    process.env.API_URL + "/signup",
    req.body,
  );
  res.status(statusCode).json(json);
}
