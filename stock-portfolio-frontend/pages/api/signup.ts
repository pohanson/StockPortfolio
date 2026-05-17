import { putJsonHandler } from "../../lib/baseApiHandler";

export default async function handler(req, res) {
  console.log(req.method, "/api/signup");
  let [statusCode, json] = await putJsonHandler(
    process.env.API_URL + "/user",
    req.body,
  );
  res.status(statusCode).json(json);
}
